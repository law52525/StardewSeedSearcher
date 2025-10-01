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
	srv.ServeHTTP(w, r)
}
