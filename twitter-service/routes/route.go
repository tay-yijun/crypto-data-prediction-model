package routes

import (
	"twitter-service/controllers"

	"github.com/gin-gonic/gin"
)

// TwitRoute ...
func TwitRoute(router *gin.Engine) {
	router.GET("/sync", controllers.SyncPosts())
	router.GET("/twits", controllers.GetAllTwits())
}
