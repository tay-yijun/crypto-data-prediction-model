package models

import (
	"encoding/json"
	"time"
)

// TransactionRecord ...
type TransactionRecord struct {
	ID       json.Number `json:"id,omitempty"`
	Price    string      `json:"price"`
	Time     json.Number `json:"time"`
	QTY      string      `json:"qty"`
	QuoteQTY string      `json:"quoteQty"`
}

type CurrentPrice struct {
	Price string `json:"price"`
}

type TickerPrice struct {
	Price string    `json:"price"`
	Time  time.Time `json:"time"`
}
