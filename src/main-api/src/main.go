package main

import (
	"os"

	docs "main-api/docs"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	swaggerfiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
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
	docs.SwaggerInfo.BasePath = "/"

	addRoutes(router)

	port := getEnvCustom("PORT", "8000")
	logger.Info("Starting server on port ", port)
	router.Run("0.0.0.0:" + port)
}

func addRoutes(router *gin.Engine) {
	router.GET("/track-one/:courier/:id", trackOneHandler)
	router.GET("/track-many/:courier/:ids", trackManyHandler)
	router.GET("/docs/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))
	router.GET("/", func(c *gin.Context) {
		c.Redirect(302, "/docs/index.html")
	})
}

func getEnvCustom(key string, defaultValue string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return defaultValue
	}
	return value
}
