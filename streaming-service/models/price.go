package models

import (
	"time"
)

// CurrentPrice ...
type CurrentPrice struct {
	Price string `json:"price"`
}

// TickerPrice ...
type TickerPrice struct {
	Price string    `json:"price"`
	Time  time.Time `json:"time"`
}
