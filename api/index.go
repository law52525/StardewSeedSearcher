package handler

import (
	"fmt"
	"net/http"
	"os"
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
		serveIndexHTML(w, r)
		return
	}

	// 其他路径由服务器处理
	srv.ServeHTTP(w, r)
}

// serveIndexHTML 提供 index.html 文件
func serveIndexHTML(w http.ResponseWriter, r *http.Request) {
	// 读取 index.html 文件
	content, err := os.ReadFile("index.html")
	if err != nil {
		// 如果文件不存在，返回一个简单的HTML页面
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		fmt.Fprintf(w, `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>星露谷种子搜索器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #2c5530; }
        .error { color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .info { color: #1976d2; background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌾 星露谷种子搜索器</h1>
        <div class="error">
            <h3>⚠️ 文件未找到</h3>
            <p>index.html 文件未找到，请确保文件存在于项目根目录。</p>
        </div>
        <div class="info">
            <h3>📋 API 端点</h3>
            <p><strong>健康检查:</strong> <a href="/api/health">/api/health</a></p>
            <p><strong>搜索接口:</strong> POST /api/search</p>
        </div>
    </div>
</body>
</html>`)
		return
	}

	// 设置正确的Content-Type
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Write(content)
}
