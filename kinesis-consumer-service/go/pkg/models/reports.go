package models

import (
	"time"

	"gorm.io/gorm"
)

// Report ...
type Report struct {
	Model
	TaskName string `gorm:"column:task_name;" json:"task_name"`
	Status   string `gorm:"column:status;" json:"status"`
	Message  string `gorm:"column:message;" json:"message"`
}

// BeforeCreate ...
func (m *Report) BeforeCreate(*gorm.DB) error {
	m.CreatedAt = time.Now()
	m.UpdatedAt = time.Now()
	return nil
}

// BeforeUpdate ...
func (m *Report) BeforeUpdate(*gorm.DB) error {
	m.UpdatedAt = time.Now()
	return nil
}