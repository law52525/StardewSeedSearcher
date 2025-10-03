"""
HTTP request handlers
"""

import asyncio
import json
import logging
import math
import os
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from internal.models import (
    SearchRequest, SearchResponse, HealthResponse,
    StartMessage, ProgressMessage, FoundMessage, CompleteMessage
)
from internal.features import WeatherPredictor
from internal.websocket import manager
from internal.gpu_pure_accelerator import PureGPUSeedSearcher, get_pure_gpu_info

logger = logging.getLogger(__name__)

router = APIRouter()

# Thread pool for CPU-intensive search operations
executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)


@router.post("/api/search", response_model=SearchResponse)
async def handle_search(request: SearchRequest) -> SearchResponse:
    """Handle search API endpoint"""
    logger.info(f"Received search request: {request.start_seed}-{request.end_seed}")
    
    # Start search in background task
    asyncio.create_task(perform_search(request))
    
    return SearchResponse(message="Search started.")


async def perform_search(request: SearchRequest) -> None:
    """Perform actual search (parallelized version)"""
    start_time = time.time()
    total_seeds = request.end_seed - request.start_seed + 1
    
    # Configure feature templates (for creating worker instances)
    search_feature_templates: List[WeatherPredictor] = []
    logger.info(f"Weather conditions count: {len(request.weather_conditions)}")
    
    if request.weather_conditions:
        predictor = WeatherPredictor()
        predictor.set_enabled(True)
        
        for condition in request.weather_conditions:
            logger.info(f"Adding weather condition: {condition}")
            predictor.add_condition(condition)
        
        search_feature_templates.append(predictor)
        logger.info(f"Configured {len(search_feature_templates)} search features")
    else:
        logger.info("No weather conditions, will match all seeds")
    
    # Send start message
    start_message = StartMessage(total=total_seeds)
    await manager.broadcast(start_message.model_dump_json(by_alias=True))
    
    # Check if we should use GPU acceleration
    use_gpu = total_seeds > 0 and request.weather_conditions  # Use GPU for large searches with weather conditions
    
    if use_gpu:
        # Try pure GPU first (with XXHash32), then hybrid GPU, then CPU
        try:
            logger.info("Attempting pure GPU acceleration with XXHash32")
            pure_gpu_searcher = PureGPUSeedSearcher(request.weather_conditions, request.use_legacy_random)
            if pure_gpu_searcher.accelerator.is_available():
                results = await pure_gpu_searcher.search_seeds_pure_gpu(request.start_seed, request.end_seed, request.output_limit)
                
                # Send found seeds
                for seed in results:
                    found_message = FoundMessage(seed=seed)
                    await manager.broadcast(found_message.model_dump_json(by_alias=True))
                
                # Send completion message
                elapsed = round(time.time() - start_time, 2)
                complete_message = CompleteMessage(total_found=len(results), elapsed=elapsed)
                await manager.broadcast(complete_message.model_dump_json(by_alias=True))
                
                logger.info(f"Pure GPU search completed: found {len(results)} matching seeds in {elapsed}s")
                return
            else:
                logger.info("Pure GPU not available, falling back to CPU")
                # Fall through to CPU search
        except Exception as e:
            logger.error(f"Pure GPU failed: {e}, falling back to CPU")
            # Fall through to CPU search
    
    # Parallel search configuration - dynamically adjust based on actual CPU cores
    max_workers = os.cpu_count() or 4
    num_workers = max_workers
    
    if total_seeds < 10000:
        num_workers = 1  # Small range search uses single thread
    elif total_seeds < 100000:
        # Medium range: use 2 threads or half of CPU cores, whichever is smaller
        num_workers = min(2, max_workers // 2)
        if num_workers < 1:
            num_workers = 1
    elif total_seeds < 1000000:
        # Large range: use 4 threads or half of CPU cores, whichever is smaller
        num_workers = min(4, max_workers // 2)
        if num_workers < 1:
            num_workers = 1
    else:
        # Very large range: use 8 threads or CPU cores, whichever is smaller
        num_workers = min(8, max_workers)
        if num_workers < 1:
            num_workers = 1
    
    logger.info(f"Using {num_workers} parallel worker threads")
    
    # Thread-safe shared state
    checked_count = [0]  # Use list to make it mutable
    results: List[int] = []
    results_lock = asyncio.Lock()
    last_progress = [0]  # Use list to make it mutable
    should_stop = [False]  # Use list to make it mutable
    
    # Use work pool pattern, reduce channel communication overhead
    # Split seed range among worker threads
    seeds_per_worker = total_seeds // num_workers
    if seeds_per_worker == 0:
        seeds_per_worker = 1
    
    # Start worker tasks - use range splitting mode
    tasks = []
    for i in range(num_workers):
        # Calculate current worker thread's seed range
        start_seed = request.start_seed + i * seeds_per_worker
        end_seed = start_seed + seeds_per_worker - 1
        if i == num_workers - 1:
            # Last worker thread handles all remaining seeds
            end_seed = request.end_seed
        
        logger.info(f"Worker thread {i} processing seed range: {start_seed}-{end_seed}")
        
        # Create worker task
        task = asyncio.create_task(
            worker_task(
                i, start_seed, end_seed, request, search_feature_templates, total_seeds,
                checked_count, results, results_lock, last_progress, should_stop
            )
        )
        tasks.append(task)
    
    # Start search - use range splitting mode, no channels needed
    logger.info(f"Starting search: seed range {request.start_seed}-{request.end_seed}, total {total_seeds}")
    
    # Wait for all worker tasks to complete
    await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = round(time.time() - start_time, 2)
    
    logger.info(f"Search completed: checked {checked_count[0]} seeds, found {len(results)} matching seeds")
    
    # Send final progress update
    await update_progress(checked_count[0], total_seeds, start_time)
    
    # Broadcast completion message
    complete_message = CompleteMessage(
        total_found=len(results),
        elapsed=elapsed
    )
    await manager.broadcast(complete_message.model_dump_json(by_alias=True))
    logger.info("Completion message sent")


async def worker_task(
    worker_id: int,
    start_seed: int,
    end_seed: int,
    request: SearchRequest,
    search_feature_templates: List[WeatherPredictor],
    total_seeds: int,
    checked_count: int,
    results: List[int],
    results_lock: asyncio.Lock,
    last_progress: int,
    should_stop: bool
) -> None:
    """Worker task for processing seed range"""
    # Create independent feature instances for each worker (optimization: reduce memory allocation)
    worker_features: List[WeatherPredictor] = []
    for template in search_feature_templates:
        # Create new weather predictor instance
        new_predictor = WeatherPredictor()
        new_predictor.set_enabled(template.is_enabled())
        # Directly copy conditions to avoid duplicate creation
        conditions = template.get_conditions()
        for condition in conditions:
            new_predictor.add_condition(condition)
        worker_features.append(new_predictor)
    
    # Use shared variables passed from main function
    
    # Process assigned seed range
    for seed in range(start_seed, end_seed + 1):
        # Check if should stop
        if should_stop[0]:
            return
        
        # Check if seed meets all enabled feature conditions
        all_match = True
        for feature in worker_features:
            if feature.is_enabled() and not feature.check(seed, request.use_legacy_random):
                all_match = False
                break
        
        if all_match:
            # Thread-safely add result (optimization: reduce lock hold time)
            async with results_lock:
                if len(results) < request.output_limit:
                    results.append(seed)
                    result_count = len(results)
                    
                    logger.info(f"Worker thread {worker_id} found matching seed: {seed}")
                    
                    # Immediately push found seed
                    found_message = FoundMessage(seed=seed)
                    await manager.broadcast(found_message.model_dump_json(by_alias=True))
                    
                    # Check if output limit reached
                    if result_count >= request.output_limit:
                        logger.info(f"Worker thread {worker_id} detected output limit {request.output_limit} reached")
                        should_stop[0] = True
                        return
                else:
                    # Results are full, set stop flag
                    should_stop[0] = True
                    return
        
        # Atomically increment check count
        checked_count[0] += 1
        
        # Update progress (optimization: use more efficient progress update strategy)
        update_interval = 5000  # Further increase update interval, reduce lock contention
        if total_seeds < 10000:
            update_interval = 1000
        if checked_count[0] % update_interval == 0 or checked_count[0] == total_seeds:
            # Use atomic operation to check if update needed
            if checked_count[0] - last_progress[0] >= update_interval:
                last_progress[0] = checked_count[0]
                await update_progress(checked_count[0], total_seeds, time.time())


async def update_progress(checked_count: int, total_seeds: int, start_time: float) -> None:
    """Thread-safe progress update method"""
    elapsed = round(time.time() - start_time, 2)
    progress = round(checked_count / total_seeds * 100, 2)
    
    # Prevent division by zero and infinite values
    speed = round(checked_count / elapsed) if elapsed > 0 else 0
    
    progress_message = ProgressMessage(
        checked_count=checked_count,
        total=total_seeds,
        progress=progress,
        speed=speed,
        elapsed=elapsed
    )
    await manager.broadcast(progress_message.model_dump_json(by_alias=True))


@router.get("/api/health", response_model=HealthResponse)
async def handle_health() -> HealthResponse:
    """Handle health check endpoint"""
    return HealthResponse(status="ok", version="1.0")


@router.get("/api/gpu-info")
async def handle_gpu_info() -> dict:
    """Handle GPU information endpoint"""
    return get_pure_gpu_info()


@router.get("/api/pure-gpu-info")
async def handle_pure_gpu_info() -> dict:
    """Handle pure GPU information endpoint"""
    return get_pure_gpu_info()


@router.get("/", response_class=HTMLResponse)
async def handle_root() -> HTMLResponse:
    """Handle root endpoint - provide HTML page"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <title>星露谷种子搜索器 API</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .card {
            background: white;
            color: #333;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 { margin-top: 0; color: #667eea; }
        .status { color: #4caf50; font-weight: bold; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class='card'>
        <h1>🌾 星露谷种子搜索器 API</h1>
        <p>服务器运行 <span class='status'>正常</span>！</p>
        <p>请打开 <code>index.html</code> 开始使用。</p>
        <hr style='margin: 20px 0; border: none; border-top: 1px solid #eee;'>
        <p style='color: #666; font-size: 0.9em; margin: 0;'>
            端口: 5000 | 状态: 运行中<br>
            WebSocket: ws://localhost:5000/ws
        </p>
    </div>
</body>
</html>"""
    
    return HTMLResponse(content=html)
