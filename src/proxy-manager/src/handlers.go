package main

import (
	"fmt"

	"github.com/gin-gonic/gin"
)

func getProxyHandler(c *gin.Context) {
	deployment := c.Param("deployment")
	logger.Info("Selecting proxy for deployment " + deployment)
	proxy := selectProxy(deployment)
	logger.Info("Selected proxy " + proxy.Host + " for deployment " + deployment)
	useProxy(proxy, deployment)
	logger.Debug(fmt.Sprintf("Proxy list after selection: %+v", proxyRegistry))
	c.JSON(200, proxy)
}

func releaseProxyHandler(c *gin.Context) {
	deployment := c.Param("deployment")

	type Proxy struct {
		Host string `json:"host"`
	}

	var proxy Proxy
	err := c.BindJSON(&proxy)
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	releaseProxy(proxy.Host, deployment)
	logger.Info("Released proxy " + proxy.Host + " for deployment " + deployment)
	logger.Debug(fmt.Sprintf("Proxy list after release: %+v", proxyRegistry))
	c.JSON(200, gin.H{"status": "ok"})
}
