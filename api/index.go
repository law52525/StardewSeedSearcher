package main

import (
	"net/http"
	"stardew-seed-searcher/internal/server"
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

// main函数用于Vercel (Vercel会直接调用Handler函数，不会执行main)
func main() {
	// 空函数 - Vercel使用Handler作为入口点
}
