package handler

import (
	_ "embed"
	"fmt"
	"net/http"
	"stardew-seed-searcher/pkg/server"
)

//go:embed index.html
var indexHTML string

// 全局服务器实例
var srv *server.Server

func init() {
	// 创建服务器实例
	srv = server.NewServer()
}

// Handler 是Vercel的入口点
func Handler(w http.ResponseWriter, r *http.Request) {
	// 如果是根路径，提供嵌入的 index.html
	if r.URL.Path == "/" {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		fmt.Fprint(w, indexHTML)
		return
	}

	// 其他路径由服务器处理
	srv.ServeHTTP(w, r)
}
