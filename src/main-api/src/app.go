package main

import (
	"os"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

var redisClient *redisHandler
var logger *logrus.Logger

func main() {
	logger, _ = NewLogger()
	logger.Info("Initialized logger")

	var err error
	redisClient, err = NewRedisHandler()
	if err != nil {
		logger.Error(err)
		return
	}
	logger.Info("Initialized redis client")
	defer redisClient.Close()

	router := gin.Default()
	addRoutes(router)

	port := getEnvCustom("PORT", "8000")
	logger.Info("Starting server on port ", port)
	router.Run("0.0.0.0:" + port)
}

func addRoutes(router *gin.Engine) {
	router.GET("/track-one/:courier/:id", trackOneHandler)
	router.GET("/track-many/:courier/:ids", trackManyHandler)
}

func getEnvCustom(key string, defaultValue string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return defaultValue
	}
	return value
}
