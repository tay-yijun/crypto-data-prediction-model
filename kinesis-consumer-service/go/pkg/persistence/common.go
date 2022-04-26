package persistence

import (
	"fmt"
	"gorm.io/gorm/clause"

	"kinesis_consumer_service/pkg/db"
)

// Create ...
func Create(value interface{}) error {
	return db.GetDB().Create(value).Error
}

// Save ...
func Save(value interface{}) error {
	return db.GetDB().Save(value).Error
}

// DeleteByWhere ...
func DeleteByWhere(model, where interface{}) (count int64, err error) {
	db := db.GetDB().Where(where).Delete(model)
	err = db.Error
	if err != nil {
		return
	}
	count = db.RowsAffected
	return
}

// DeleteByID ...
func DeleteByID(model interface{}, id int) (count int64, err error) {
	db := db.GetDB().Where("id=?", id).Delete(model)
	err = db.Error
	if err != nil {
		return
	}
	count = db.RowsAffected
	return
}

// DeleteByIDS ...
func DeleteByIDS(model interface{}, ids []int) (count int64, err error) {
	db := db.GetDB().Where("id in (?)", ids).Delete(model)
	err = db.Error
	if err != nil {
		return
	}
	count = db.RowsAffected
	return
}

// FirstByID ...
func FirstByID(out interface{}, id int) (notFound bool, err error) {
	err = db.GetDB().First(out, id).Error
	if err != nil {
		notFound = false
		return notFound, fmt.Errorf("record not found, inserting new record")
	}
	return
}

// First ...
func First(where interface{}, out interface{}, associations []string) (notFound bool, err error) {
	db := db.GetDB()
	for _, a := range associations {
		db = db.Preload(a)
	}
	err = db.Where(where).First(out).Error
	if err != nil {
		notFound = false
		return notFound, fmt.Errorf("record not found, inserting new record")
	}
	return
}

// Find ...
func Find(where interface{}, out interface{}, associations []string, orders ...string) error {
	db := db.GetDB()
	for _, a := range associations {
		db = db.Preload(a)
	}
	db = db.Where(where)
	if len(orders) > 0 {
		for _, order := range orders {
			db = db.Order(order)
		}
	}
	return db.Find(out).Error
}

// Scan ...
func Scan(model, where interface{}, out interface{}) (notFound bool, err error) {
	err = db.GetDB().Model(model).Where(where).Scan(out).Error
	if err != nil {
		notFound = false
		return notFound, fmt.Errorf("record not found, inserting new record")
	}
	return
}

// ScanList ...
func ScanList(model, where interface{}, out interface{}, orders ...string) error {
	db := db.GetDB().Model(model).Where(where)
	if len(orders) > 0 {
		for _, order := range orders {
			db = db.Order(order)
		}
	}
	return db.Scan(out).Error
}

// CreateOrUpdate ...
func CreateOrUpdate(model interface{}) {
	db.GetDB().Clauses(clause.OnConflict{
		UpdateAll: true,
	}).Create(model)
}