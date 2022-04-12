package models

import (
	"database/sql/driver"
	"encoding/json"
	"time"
)

// Model provides based for all models
type Model struct {
	ID       int    `gorm:"column:id;autosIncrement;primary_key;" json:"id" form:"id"`
	CreatedAt time.Time `gorm:"column:created_at;type:timestamp;not null;" json:"created_at"`
	UpdatedAt time.Time `gorm:"column:updated_at;type:timestamp;not null;" json:"updated_at"`
}

// JSONB custom type to store as an object
type JSONB map[string]interface{}

// Value ... gorm scanner for value
func (j JSONB) Value() (driver.Value, error) {
	valueString, err := json.Marshal(j)
	return string(valueString), err
}

// Scan ... gorm scanner for value
func (j *JSONB) Scan(value interface{}) error {
	if err := json.Unmarshal(value.([]byte), &j); err != nil {
		return err
	}
	return nil
}
