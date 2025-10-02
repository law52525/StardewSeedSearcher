package handler

import (
	"fmt"
	"log"
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
	// 添加调试信息
	log.Printf("Vercel Handler: 请求路径 = %s", r.URL.Path)

	// 如果是根路径，提供 index.html
	if r.URL.Path == "/" {
		log.Printf("尝试提供 index.html 文件")

		// 设置正确的 Content-Type
		w.Header().Set("Content-Type", "text/html; charset=utf-8")

		// 尝试不同的路径来找到 index.html
		possiblePaths := []string{
			"index.html",
			"./index.html",
			"/index.html",
			"public/index.html",
			"./public/index.html",
		}

		for _, path := range possiblePaths {
			log.Printf("尝试路径: %s", path)
			// 检查文件是否存在
			if _, err := os.Stat(path); err == nil {
				log.Printf("找到文件: %s", path)
				http.ServeFile(w, r, path)
				return
			} else {
				log.Printf("文件不存在: %s, 错误: %v", path, err)
			}
		}

		// 如果都找不到，返回一个简单的 HTML 页面
		log.Printf("所有路径都失败，返回默认 HTML")
		w.WriteHeader(http.StatusOK)
		fmt.Fprint(w, `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>星露谷种子搜索器</title>
</head>
<body>
    <h1>星露谷种子搜索器</h1>
    <p>服务器正在运行，但无法找到 index.html 文件。</p>
    <p>请检查 Vercel 部署配置。</p>
</body>
</html>`)
		return
	}

	// 其他路径由服务器处理
	srv.ServeHTTP(w, r)
}
