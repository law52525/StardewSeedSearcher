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
	// 如果是根路径，提供 index.html
	if r.URL.Path == "/" {
		// 在Vercel环境中，index.html在根目录
		http.ServeFile(w, r, "index.html")
		return
	}

	// 其他路径由服务器处理
	srv.ServeHTTP(w, r)
}
