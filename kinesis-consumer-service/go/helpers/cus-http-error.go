package helpers

import "kinesis_consumer_service/pkg/models"

// Error example
type Error struct {
	Code    int    `json:"code" example:"400"`
	Message string `json:"message" example:"status bad request"`
}

// APIResponse example
type APIResponse struct {
	Data []models.Twit `json:"data"`
}


