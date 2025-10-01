package websocket

import (
	"log"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
)

const (
	// 允许向对等方写入消息的时间
	writeWait = 10 * time.Second

	// 允许从对等方读取下一个 pong 消息的时间
	pongWait = 60 * time.Second

	// 向对等方发送 ping 的周期。必须小于 pongWait
	pingPeriod = (pongWait * 9) / 10

	// 允许从对等方接收的最大消息大小
	maxMessageSize = 512
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // 本地开发允许所有来源
	},
}

// Client 是 WebSocket 连接和 hub 之间的中间人
type Client struct {
	hub *Hub

	// WebSocket 连接
	conn *websocket.Conn

	// 出站消息的缓冲通道
	send chan []byte
}

// NewClient 创建新的客户端
func NewClient(conn *websocket.Conn, hub *Hub) *Client {
	client := &Client{
		hub:  hub,
		conn: conn,
		send: make(chan []byte, 256),
	}
	client.Register()
	return client
}

// Register 将客户端注册到 hub
func (c *Client) Register() {
	c.hub.register <- c
}

// Unregister 从 hub 注销客户端
func (c *Client) Unregister() {
	c.hub.unregister <- c
}

// ReadPump 从 WebSocket 连接向 hub 泵送消息
func (c *Client) ReadPump() {
	defer func() {
		c.Unregister()
		c.conn.Close()
	}()

	c.conn.SetReadLimit(maxMessageSize)
	c.conn.SetReadDeadline(time.Now().Add(pongWait))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		_, _, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("WebSocket error: %v", err)
			}
			break
		}
	}
}

// WritePump 从 hub 向 WebSocket 连接泵送消息
func (c *Client) WritePump() {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			// 直接发送单条消息，不合并
			if err := c.conn.WriteMessage(websocket.TextMessage, message); err != nil {
				return
			}

		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}
