package routes

import (
	"streaming-service/controllers"

	"github.com/gin-gonic/gin"
)

// Routes ...
func Routes(router *gin.Engine) {
	router.GET("/sync", controllers.SyncRecords())
	router.GET("/transaction-records", controllers.GetAllTRecords())
}
