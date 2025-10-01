package main

import (
	"log"
	"os"
	"stardew-seed-searcher/pkg/server"
)

func main() {
	// 创建日志文件
	logFile, err := os.OpenFile("stardew-seed-searcher.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		log.Fatal("无法创建日志文件:", err)
	}
	defer logFile.Close()

	// 设置日志输出到文件
	log.SetOutput(logFile)
	log.SetFlags(log.LstdFlags)

	// 创建服务器实例
	srv := server.NewServer()

	// 获取端口
	port := os.Getenv("PORT")
	if port == "" {
		port = "5000" // 默认端口
	}

	log.Println("╔════════════════════════════════════════╗")
	log.Println("║  🌾 星露谷种子搜索器 - Web 服务启动  ║")
	log.Println("╚════════════════════════════════════════╝")
	log.Println()
	log.Printf("✓ 服务器地址: http://localhost:%s", port)
	log.Printf("✓ WebSocket: ws://localhost:%s/ws", port)
	log.Println()
	log.Println("📝 请打开 index.html 开始使用")
	log.Println("⚠️  按 Ctrl+C 停止服务器")
	log.Println()

	// 启动服务器
	if err := srv.Start(":" + port); err != nil {
		log.Fatal("服务器启动失败:", err)
	}
}
