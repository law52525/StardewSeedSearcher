package server

import (
	"context"
	"log"
	"net/http"
	"stardew-seed-searcher/pkg/handlers"
	"stardew-seed-searcher/pkg/websocket"
	"time"

	gorilla "github.com/gorilla/websocket"
)

// Server 表示 Web 服务器
type Server struct {
	httpServer *http.Server
	hub        *websocket.Hub
}

// NewServer 创建新的服务器实例
func NewServer() *Server {
	hub := websocket.NewHub()
	go hub.Run()

	mux := http.NewServeMux()

	// CORS 中间件
	corsHandler := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}

			next.ServeHTTP(w, r)
		})
	}

	// WebSocket 端点
	mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		upgrader := gorilla.Upgrader{
			CheckOrigin: func(r *http.Request) bool {
				return true // 本地开发允许所有来源
			},
		}

		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			log.Printf("WebSocket 升级错误: %v", err)
			return
		}

		client := websocket.NewClient(conn, hub)
		go client.ReadPump()
		go client.WritePump()
	})

	// API 端点
	searchHandler := handlers.NewSearchHandler(hub)
	mux.HandleFunc("/api/search", searchHandler.HandleSearch)
	mux.HandleFunc("/api/health", handlers.HandleHealth)
	mux.HandleFunc("/api/status", searchHandler.HandleStatus)

	// 根端点 - 提供 HTML 页面
	mux.HandleFunc("/", handlers.HandleRoot)

	server := &http.Server{
		Addr:         ":5000",
		Handler:      corsHandler(mux),
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
	}

	return &Server{
		httpServer: server,
		hub:        hub,
	}
}

// Start 启动 HTTP 服务器
func (s *Server) Start(addr string) error {
	s.httpServer.Addr = addr
	return s.httpServer.ListenAndServe()
}

// ServeHTTP 实现 http.Handler 接口，用于Vercel
func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.httpServer.Handler.ServeHTTP(w, r)
}

// Shutdown 优雅地关闭服务器
func (s *Server) Shutdown(ctx context.Context) error {
	return s.httpServer.Shutdown(ctx)
}
