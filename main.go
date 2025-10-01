package handler

import (
	"log"
	"net/http"
	"os"
	"stardew-seed-searcher/internal/server"
)

// 全局服务器实例，用于Vercel
var srv *server.Server

func init() {
	// 创建日志文件（仅在非Vercel环境下）
	if os.Getenv("VERCEL") == "" {
		logFile, err := os.OpenFile("stardew-seed-searcher.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
		if err != nil {
			log.Fatal("无法创建日志文件:", err)
		}
		defer logFile.Close()

		// 设置日志输出到文件
		log.SetOutput(logFile)
		log.SetFlags(log.LstdFlags)
	}

	// 创建服务器实例
	srv = server.NewServer()
}

// Handler 是Vercel的入口点
func Handler(w http.ResponseWriter, r *http.Request) {
	srv.ServeHTTP(w, r)
}
