package handler

import (
	"net/http"
	"stardew-seed-searcher/pkg/server"
)

// 全局服务器实例
var srv *server.Server

func init() {
	// 创建服务器实例
	srv = server.NewServer()
}

// Handler 是Vercel的入口点
func Handler(w http.ResponseWriter, r *http.Request) {
	// 所有请求都由服务器处理（根路径现在由 Vercel 静态文件处理）
	srv.ServeHTTP(w, r)
}
