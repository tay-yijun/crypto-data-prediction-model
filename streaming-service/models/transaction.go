package models

import (
	"time"
)

// TransactionRecord ...
type TransactionRecord struct {
	ID       string `json:"id,omitempty"`
	Price    string  `json:"price"`
	CreatedAt time.Time  `json:"created_at"`
}
