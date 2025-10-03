"""
Pure GPU implementation for seed search using CuPy XXHash32
Fully GPU-accelerated seed search with weather prediction
"""

import logging
import numpy as np
from typing import List, Tuple, Optional
import asyncio

try:
    import cupy as cp
    GPU_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Pure GPU acceleration available with CuPy")
except ImportError as e:
    GPU_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Pure GPU acceleration not available: {e}")

from internal.models import WeatherCondition, Season

logger = logging.getLogger(__name__)


class CuPyXXHash32:
    """Pure GPU implementation of XXHash32 using CuPy"""
    
    def __init__(self):
        # Define CUDA kernel code for XXHash32
        self.cuda_code = r'''
#define PRIME32_1 2654435761U
#define PRIME32_2 2246822519U
#define PRIME32_3 3266489917U
#define PRIME32_4 668265263U
#define PRIME32_5 374761393U

__device__ __inline__ unsigned int rotl32(unsigned int x, int r) {
    return (x << r) | (x >> (32 - r));
}

__device__ __inline__ unsigned int round32(unsigned int seed, unsigned int input_val) {
    seed += input_val * PRIME32_2;
    seed = rotl32(seed, 13);
    seed *= PRIME32_1;
    return seed;
}

__device__ __inline__ unsigned int read32(const unsigned char* ptr) {
    // Safely read 32-bit value using little-endian
    return (unsigned int)ptr[0] | 
           ((unsigned int)ptr[1] << 8) | 
           ((unsigned int)ptr[2] << 16) | 
           ((unsigned int)ptr[3] << 24);
}

extern "C" __global__ void xxhash32_batch(
    const unsigned char* input,
    unsigned int* output,
    const unsigned int* offsets,
    const unsigned int* lengths,
    unsigned int seed,
    int num_strings
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_strings) return;
    
    unsigned int offset = offsets[idx];
    unsigned int len = lengths[idx];
    const unsigned char* data = input + offset;
    
    unsigned int h32;
    
    if (len >= 16) {
        unsigned int v1 = seed + PRIME32_1 + PRIME32_2;
        unsigned int v2 = seed + PRIME32_2;
        unsigned int v3 = seed + 0;
        unsigned int v4 = seed - PRIME32_1;
        
        const unsigned char* ptr = data;
        const unsigned char* end = ptr + (len / 16) * 16;
        
        while (ptr < end) {
            // Use safe 32-bit read function to avoid alignment issues
            v1 = round32(v1, read32(ptr));
            v2 = round32(v2, read32(ptr + 4));
            v3 = round32(v3, read32(ptr + 8));
            v4 = round32(v4, read32(ptr + 12));
            
            ptr += 16;
        }
        
        h32 = rotl32(v1, 1) + rotl32(v2, 7) + rotl32(v3, 12) + rotl32(v4, 18);
    } else {
        h32 = seed + PRIME32_5;
    }
    
    h32 += len;
    
    // Process remaining bytes - fixed algorithm
    const unsigned char* tail = data + (len & ~0xF);
    unsigned int remaining = len & 0xF;
    
    // Process remaining bytes according to standard xxHash algorithm
    while (remaining >= 4) {
        h32 += read32(tail) * PRIME32_3;
        h32 = rotl32(h32, 17) * PRIME32_4;
        tail += 4;
        remaining -= 4;
    }
    
    while (remaining > 0) {
        h32 += (*tail) * PRIME32_5;
        h32 = rotl32(h32, 11) * PRIME32_1;
        tail++;
        remaining--;
    }
    
    // Final mixing
    h32 ^= h32 >> 15;
    h32 *= PRIME32_2;
    h32 ^= h32 >> 13;
    h32 *= PRIME32_3;
    h32 ^= h32 >> 16;
    
    output[idx] = h32;
}

__device__ __inline__ unsigned int xxhash32_single(const unsigned char* data, unsigned int len, unsigned int seed) {
    unsigned int h32;
    
    if (len >= 16) {
        unsigned int v1 = seed + PRIME32_1 + PRIME32_2;
        unsigned int v2 = seed + PRIME32_2;
        unsigned int v3 = seed + 0;
        unsigned int v4 = seed - PRIME32_1;
        
        const unsigned char* ptr = data;
        const unsigned char* end = ptr + (len / 16) * 16;
        
        while (ptr < end) {
            v1 = round32(v1, read32(ptr));
            v2 = round32(v2, read32(ptr + 4));
            v3 = round32(v3, read32(ptr + 8));
            v4 = round32(v4, read32(ptr + 12));
            
            ptr += 16;
        }
        
        h32 = rotl32(v1, 1) + rotl32(v2, 7) + rotl32(v3, 12) + rotl32(v4, 18);
    } else {
        h32 = seed + PRIME32_5;
    }
    
    h32 += len;
    
    // Process remaining bytes
    const unsigned char* tail = data + (len & ~0xF);
    unsigned int remaining = len & 0xF;
    
    while (remaining >= 4) {
        h32 += read32(tail) * PRIME32_3;
        h32 = rotl32(h32, 17) * PRIME32_4;
        tail += 4;
        remaining -= 4;
    }
    
    while (remaining > 0) {
        h32 += (*tail) * PRIME32_5;
        h32 = rotl32(h32, 11) * PRIME32_1;
        tail++;
        remaining--;
    }
    
    // Final mixing
    h32 ^= h32 >> 15;
    h32 *= PRIME32_2;
    h32 ^= h32 >> 13;
    h32 *= PRIME32_3;
    h32 ^= h32 >> 16;
    
    return h32;
}

__device__ __inline__ unsigned int get_random_seed_gpu(unsigned int a, unsigned int b, unsigned int c, unsigned int d, unsigned int e, int use_legacy_random) {
    if (use_legacy_random) {
        // Legacy random: simple addition with modulo
        unsigned long long total = (unsigned long long)a + b + c + d + e;
        return (unsigned int)(total % 2147483647ULL);
    } else {
        // New random: use XXHash32
        unsigned char data[20];
        data[0] = (unsigned char)(a & 0xFF);
        data[1] = (unsigned char)((a >> 8) & 0xFF);
        data[2] = (unsigned char)((a >> 16) & 0xFF);
        data[3] = (unsigned char)((a >> 24) & 0xFF);
        data[4] = (unsigned char)(b & 0xFF);
        data[5] = (unsigned char)((b >> 8) & 0xFF);
        data[6] = (unsigned char)((b >> 16) & 0xFF);
        data[7] = (unsigned char)((b >> 24) & 0xFF);
        data[8] = (unsigned char)(c & 0xFF);
        data[9] = (unsigned char)((c >> 8) & 0xFF);
        data[10] = (unsigned char)((c >> 16) & 0xFF);
        data[11] = (unsigned char)((c >> 24) & 0xFF);
        data[12] = (unsigned char)(d & 0xFF);
        data[13] = (unsigned char)((d >> 8) & 0xFF);
        data[14] = (unsigned char)((d >> 16) & 0xFF);
        data[15] = (unsigned char)((d >> 24) & 0xFF);
        data[16] = (unsigned char)(e & 0xFF);
        data[17] = (unsigned char)((e >> 8) & 0xFF);
        data[18] = (unsigned char)((e >> 16) & 0xFF);
        data[19] = (unsigned char)((e >> 24) & 0xFF);
        
        return xxhash32_single(data, 20, 0);
    }
}

__device__ __inline__ unsigned int get_first_rand_gpu(unsigned int seed) {
    // Use the exact same formula as Go version (.NET Random)
    const unsigned int multiplier = 1121899819U;
    const unsigned int constant = 1559595546U;
    const unsigned int int32_max = 2147483647U;
    
    // Handle negative seeds (C# Random constructor takes absolute value)
    if ((int)seed < 0) {
        seed = -seed;
    }
    
    // Calculate: y = (1121899819 * x + 1559595546) % 2147483647
    // Use unsigned long long to avoid overflow
    unsigned long long result = (unsigned long long)multiplier * (unsigned long long)seed + (unsigned long long)constant;
    unsigned int first_rand = (unsigned int)(result % (unsigned long long)int32_max);
    
    return first_rand;
}

__device__ __inline__ float random_next_double_gpu(unsigned int seed) {
    // Simulate C#'s Random.NextDouble() method using exact Go formula
    unsigned int first_rand = get_first_rand_gpu(seed);
    return (float)first_rand / 2147483647.0f;
}

__device__ __inline__ int random_next_gpu(unsigned int seed, int max_value) {
    // Simulate C#'s Random.Next(maxValue) method using exact Go formula
    if (max_value <= 0) return 0;
    
    unsigned int first_rand = get_first_rand_gpu(seed);
    return (int)((unsigned long long)first_rand * max_value / 2147483647ULL);
}

__device__ __inline__ int is_rainy_day_gpu(int season, int day_of_month, int absolute_day, unsigned int game_id, int use_legacy_random) {
    // Fixed weather rules (same as Python version)
    
    if (season == 0) {  // Spring
        if (day_of_month == 1 || day_of_month == 2 || day_of_month == 4 || day_of_month == 5) {
            return 0;  // Sunny
        }
        if (day_of_month == 3) {
            return 1;  // Rainy
        }
        if (day_of_month == 13 || day_of_month == 24) {
            return 0;  // Festival fixed sunny
        }
        // Spring continues to general logic below
        
    } else if (season == 1) {  // Summer
        // Summer special: Green rain day determination
        int year = 1;  // First year
        unsigned int green_rain_seed = get_random_seed_gpu(year * 777, game_id, 0, 0, 0, use_legacy_random);
        int green_rain_days[] = {5, 6, 7, 14, 15, 16, 18, 23};
        int green_rain_day = green_rain_days[random_next_gpu(green_rain_seed, 8)];
        
        if (day_of_month == green_rain_day) {
            return 1;  // Green rain (counts as rainy)
        }
        if (day_of_month == 11 || day_of_month == 28) {
            return 0;  // Festival fixed sunny
        }
        if (day_of_month % 13 == 0) {  // Days 13, 26
            return 1;  // Thunderstorm (counts as rainy)
        }
        
        // Normal rain: probability increases with date
        // Use summer_rain_chance hash (precomputed as -0x126d6da2)
        unsigned int summer_rain_chance_hash = 0xed92925e;
        unsigned int rain_seed = get_random_seed_gpu(absolute_day - 1, game_id / 2, summer_rain_chance_hash, 0, 0, use_legacy_random);
        float normalized_seed = random_next_double_gpu(rain_seed);
        float rain_chance = 0.12f + 0.003f * (day_of_month - 1);
        return (normalized_seed < rain_chance) ? 1 : 0;
        
    } else if (season == 2) {  // Fall
        if (day_of_month == 16 || day_of_month == 27) {
            return 0;  // Festival fixed sunny
        }
        // Fall continues to general logic below
    }
    
    // Spring and Fall normal days: 18.3% probability
    // Use location_weather hash (precomputed as -0x5a319e62)
    unsigned int location_weather_hash = 0xa5ce619e;
    unsigned int seed = get_random_seed_gpu(location_weather_hash, game_id, absolute_day - 1, 0, 0, use_legacy_random);
    float normalized_seed = random_next_double_gpu(seed);
    return (normalized_seed < 0.183f) ? 1 : 0;
}

extern "C" __global__ void weather_prediction_kernel(
    const unsigned long long* seeds,
    unsigned int* results,
    const unsigned int* season_offsets,
    const unsigned int* start_days,
    const unsigned int* end_days,
    const unsigned int* min_rain_days,
    unsigned int num_conditions,
    int use_legacy_random,
    int num_seeds
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_seeds) return;
    
    unsigned int game_id = (unsigned int)seeds[idx];
    
    // Check each weather condition
    int matches = 1;
    for (int cond_idx = 0; cond_idx < num_conditions; cond_idx++) {
        unsigned int season_offset = season_offsets[cond_idx];
        unsigned int start_day = start_days[cond_idx];
        unsigned int end_day = end_days[cond_idx];
        unsigned int min_rain = min_rain_days[cond_idx];
        
        // Calculate rain days for this condition
        int rain_days = 0;
        for (unsigned int day = start_day; day <= end_day; day++) {
            // Convert absolute day to season and day_of_month
            int season = season_offset;  // 0=Spring, 1=Summer, 2=Fall
            int day_of_month = day;
            
            // Use the same weather prediction logic as Python
            int is_rainy = is_rainy_day_gpu(season, day_of_month, season*28+day, game_id, use_legacy_random);
            if (is_rainy) {
                rain_days++;
            }
        }
        
        // Check if condition is met
        if (rain_days < min_rain) {
            matches = 0;
            break;
        }
    }
    
    results[idx] = matches;
}
'''
        try:
            # Compile CUDA kernels
            self.xxhash_kernel = cp.RawKernel(self.cuda_code, 'xxhash32_batch')
            self.weather_kernel = cp.RawKernel(self.cuda_code, 'weather_prediction_kernel')
            logger.info("Pure GPU CUDA kernels compiled successfully")
        except Exception as e:
            logger.error(f"CUDA kernel compilation failed: {e}")
            self.xxhash_kernel = None
            self.weather_kernel = None
    
    def compute_batch(self, strings, seed=0):
        """Batch compute XXHash32 for multiple strings"""
        if not strings or self.xxhash_kernel is None:
            return []
        
        # Prepare data
        all_data = []
        offsets = [0]
        lengths = []
        
        # Build continuous memory block and offset information
        for s in strings:
            if isinstance(s, str):
                s = s.encode('utf-8')
            all_data.extend(s)
            lengths.append(len(s))
            offsets.append(offsets[-1] + len(s))
        
        offsets.pop()  # Remove last cumulative value
        
        # Convert to CuPy arrays (allocate directly on GPU)
        input_data = cp.array(all_data, dtype=cp.uint8)
        offsets_arr = cp.array(offsets, dtype=cp.uint32)
        lengths_arr = cp.array(lengths, dtype=cp.uint32)
        output_arr = cp.zeros(len(strings), dtype=cp.uint32)
        
        # Launch kernel
        block_size = 256
        grid_size = (len(strings) + block_size - 1) // block_size
        
        self.xxhash_kernel(
            (grid_size,), (block_size,),
            (input_data, output_arr, offsets_arr, lengths_arr, 
                cp.uint32(seed), cp.int32(len(strings)))
        )
        
        # Synchronize device to ensure computation is complete
        cp.cuda.Stream.null.synchronize()
        
        # Convert results to Python list
        return output_arr.get().tolist()
    
    def compute_single(self, data, seed=0):
        """Compute XXHash32 for a single data"""
        return self.compute_batch([data], seed)[0]


class PureGPUAccelerator:
    """Pure GPU-accelerated seed search accelerator"""
    
    def __init__(self):
        self.gpu_available = GPU_AVAILABLE
        self.device = None
        self.xxhash = None
        
        if self.gpu_available:
            try:
                import cupy as cp
                self.device = cp.cuda.Device()
                self.xxhash = CuPyXXHash32()
                logger.info(f"Using pure GPU device: {self.device}")
            except Exception as e:
                logger.error(f"Failed to initialize pure GPU: {e}")
                self.gpu_available = False
    
    def is_available(self) -> bool:
        """Check if pure GPU acceleration is available"""
        return self.gpu_available and self.xxhash is not None
    
    def get_device_info(self) -> dict:
        """Get GPU device information"""
        if not self.gpu_available:
            return {"available": False}
        
        try:
            import cupy as cp
            device = cp.cuda.Device()
            return {
                "available": True,
                "device_name": str(device),
                "compute_capability": "Unknown",
                "memory_total": device.mem_info[1] if hasattr(device, 'mem_info') else "Unknown",
                "xxhash_available": self.xxhash is not None
            }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {"available": False, "error": str(e)}


class PureGPUSeedSearcher:
    """Pure GPU-accelerated seed searcher with XXHash32"""
    
    def __init__(self, weather_conditions: List[WeatherCondition], use_legacy_random: bool = False):
        self.weather_conditions = weather_conditions
        self.use_legacy_random = use_legacy_random
        self.accelerator = PureGPUAccelerator()
        
        # Prepare weather condition data for GPU
        self._prepare_weather_data()
    
    def _prepare_weather_data(self):
        """Prepare weather condition data for GPU processing"""
        if not self.accelerator.is_available():
            return
        
        try:
            import cupy as cp
            # Convert weather conditions to arrays for GPU processing
            self.weather_conditions_array = cp.array([1] * len(self.weather_conditions), dtype=cp.int32)
            self.season_offsets = cp.array([self._get_season_offset(cond.season) for cond in self.weather_conditions], dtype=cp.int32)
            self.start_days = cp.array([cond.start_day for cond in self.weather_conditions], dtype=cp.int32)
            self.end_days = cp.array([cond.end_day for cond in self.weather_conditions], dtype=cp.int32)
            self.min_rain_days = cp.array([cond.min_rain_days for cond in self.weather_conditions], dtype=cp.int32)
            
            logger.info(f"Prepared {len(self.weather_conditions)} weather conditions for pure GPU processing")
        except Exception as e:
            logger.error(f"Failed to prepare weather data for pure GPU: {e}")
            self.accelerator.gpu_available = False
    
    def _get_season_offset(self, season: Season) -> int:
        """Get season offset for hash calculation"""
        season_offsets = {
            Season.SPRING: 0,
            Season.SUMMER: 1,
            Season.FALL: 2
        }
        return season_offsets.get(season, 0)
    
    async def search_seeds_pure_gpu(self, start_seed: int, end_seed: int, output_limit: int = 100) -> List[int]:
        """Search seeds using pure GPU acceleration with batch processing"""
        if not self.accelerator.is_available():
            logger.warning("Pure GPU not available, falling back to CPU")
            return await self._search_seeds_cpu_fallback(start_seed, end_seed, output_limit)
        
        try:
            import cupy as cp
            total_seeds = end_seed - start_seed + 1
            batch_size = 100_000_000  # 1亿个种子一批
            
            logger.info(f"Starting pure GPU search with batch processing: {start_seed}-{end_seed} ({total_seeds} seeds)")
            logger.info(f"Batch size: {batch_size:,} seeds per batch")
            
            all_results = []
            current_output_count = 0
            
            # Process in batches
            for batch_start in range(start_seed, end_seed + 1, batch_size):
                batch_end = min(batch_start + batch_size - 1, end_seed)
                batch_seeds = batch_end - batch_start + 1
                
                logger.info(f"Processing batch: {batch_start}-{batch_end} ({batch_seeds:,} seeds)")
                
                with cp.cuda.Device():
                    # Create seed array for this batch
                    seeds = cp.arange(batch_start, batch_end + 1, dtype=cp.uint64)
                    results = cp.zeros(len(seeds), dtype=cp.int32)
                    
                    # Configure CUDA grid and block sizes
                    threads_per_block = min(256, batch_seeds)
                    blocks = max(1, (batch_seeds + threads_per_block - 1) // threads_per_block)
                    
                    # Launch GPU kernel for this batch
                    self.accelerator.xxhash.weather_kernel(
                        (blocks,), (threads_per_block,),
                        (seeds, results, self.season_offsets, self.start_days, 
                         self.end_days, self.min_rain_days, 
                         cp.uint32(len(self.weather_conditions)), 
                         cp.int32(1 if self.use_legacy_random else 0),
                         cp.int32(batch_seeds))
                    )
                    
                    # Get matching seeds for this batch
                    matching_indices = cp.where(results == 1)[0]
                    matching_seeds = seeds[matching_indices]
                    
                    # Convert to CPU and add to results
                    batch_results = matching_seeds.get().tolist()
                    all_results.extend(batch_results)
                    current_output_count += len(batch_results)
                    
                    logger.info(f"Batch completed: found {len(batch_results)} matching seeds (total: {current_output_count})")
                    
                    # Check if we've reached the output limit
                    if current_output_count >= output_limit:
                        logger.info(f"Reached output limit of {output_limit}, stopping search")
                        break
            
            # Limit final results
            if len(all_results) > output_limit:
                all_results = all_results[:output_limit]
            
            logger.info(f"Pure GPU search completed: found {len(all_results)} matching seeds total")
            return all_results
                    
        except Exception as e:
            logger.error(f"Pure GPU search failed: {e}")
            logger.info("Falling back to CPU search")
            return await self._search_seeds_cpu_fallback(start_seed, end_seed, output_limit)
    
    async def _search_seeds_cpu_fallback(self, start_seed: int, end_seed: int, output_limit: int) -> List[int]:
        """CPU fallback when pure GPU is not available"""
        from internal.features import WeatherPredictor
        
        predictor = WeatherPredictor()
        predictor.set_enabled(True)
        
        for condition in self.weather_conditions:
            predictor.add_condition(condition)
        
        results = []
        for seed in range(start_seed, end_seed + 1):
            if len(results) >= output_limit:
                break
            
            if predictor.check(seed, self.use_legacy_random):
                results.append(seed)
        
        return results


def get_pure_gpu_info() -> dict:
    """Get pure GPU information for debugging"""
    accelerator = PureGPUAccelerator()
    return accelerator.get_device_info()
