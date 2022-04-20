package main

import (
	"binance-service/configs"
	"binance-service/routes"

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
