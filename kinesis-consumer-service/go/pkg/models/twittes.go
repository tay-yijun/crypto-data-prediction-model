package models

import (
	"time"

	"gorm.io/gorm"
)

// Twit ...
type Twit struct {
	Model
	ID   int    `json:"id"`
	Text string `json:"text"`
	Time string `json:"time"`
	Sentiment string `json:"sentiment"`
}

// BeforeCreate ...
func (m *Twit) BeforeCreate(*gorm.DB) error {
	m.CreatedAt = time.Now()
	m.UpdatedAt = time.Now()
	return nil
}

// BeforeUpdate ...
func (m *Twit) BeforeUpdate(*gorm.DB) error {
	m.UpdatedAt = time.Now()
	return nil
}
