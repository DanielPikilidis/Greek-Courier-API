package main

import (
	"os"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

var logger *logrus.Logger

func main() {
	logger, _ = NewLogger()
	logger.Info("Initialized logger")

	router := gin.Default()
	addRoutes(router)

	proxyListPath := getEnvCustom("PROXY_LIST_PATH", "/tmp/proxy_list.json")

	err := openProxyList(proxyListPath)
	if err != nil {
		logger.Fatal("Failed to open proxy list: " + err.Error())
	}

	port := getEnvCustom("PORT", "8000")
	logger.Info("Starting server on port " + port)
	router.Run("0.0.0.0:" + port)
}

func addRoutes(router *gin.Engine) {
	router.GET("/request-proxy/:deployment", getProxyHandler)
	router.POST("/release-proxy/:deployment", releaseProxyHandler)
}

func getEnvCustom(key string, defaultValue string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return defaultValue
	}
	return value
}
