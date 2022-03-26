package main

import (
	"streaming-service/configs"
	"streaming-service/routes"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	//run database
	configs.ConnectDB()
	//routes
	routes.Routes(router)

	err := router.Run("localhost:8000")
	if err != nil {
		return 
	}
}
