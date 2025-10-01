package websocket

import (
	"log"
	"sync"
)

// Hub 维护活跃客户端集合并向客户端广播消息
type Hub struct {
	// 已注册的客户端
	clients map[*Client]bool

	// 来自客户端的入站消息
	broadcast chan []byte

	// 来自客户端的注册请求
	register chan *Client

	// 来自客户端的注销请求
	unregister chan *Client

	// 用于线程安全操作的互斥锁
	mutex sync.RWMutex
}

// NewHub 创建新的 Hub
func NewHub() *Hub {
	return &Hub{
		clients:    make(map[*Client]bool),
		broadcast:  make(chan []byte),
		register:   make(chan *Client),
		unregister: make(chan *Client),
	}
}

// Run 启动 hub
func (h *Hub) Run() {
	for {
		select {
		case client := <-h.register:
			h.mutex.Lock()
			h.clients[client] = true
			h.mutex.Unlock()
			log.Printf("Client connected. Total clients: %d", len(h.clients))

		case client := <-h.unregister:
			h.mutex.Lock()
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
			}
			h.mutex.Unlock()
			log.Printf("Client disconnected. Total clients: %d", len(h.clients))

		case message := <-h.broadcast:
			h.mutex.RLock()
			for client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
			h.mutex.RUnlock()
		}
	}
}

// Broadcast 向所有连接的客户端发送消息
func (h *Hub) Broadcast(message []byte) {
	// log.Printf("广播消息到 %d 个客户端: %s", len(h.clients), string(message))
	h.broadcast <- message
}

// GetClientCount 返回连接的客户端数量
func (h *Hub) GetClientCount() int {
	h.mutex.RLock()
	defer h.mutex.RUnlock()
	return len(h.clients)
}
