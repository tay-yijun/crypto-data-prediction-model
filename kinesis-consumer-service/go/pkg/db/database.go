package db


import (
	"os"
	"time"

	"gorm.io/driver/postgres"

	log "github.com/sirupsen/logrus"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"kinesis_consumer_service/pkg/config"
	"kinesis_consumer_service/pkg/models"
)

// DB ...
var (
	DB  *gorm.DB
	err error
)

// Database ..
type Database struct {
	*gorm.DB
}

// SetupDB opens a database and saves the reference to `Database` struct.
func SetupDB() error {
	var db = DB

	configuration := config.GetConfig()
	driver := configuration.Database.Driver
	database := configuration.Database.Dbname
	username := configuration.Database.Username
	password := configuration.Database.Password
	host := configuration.Database.Host
	port := configuration.Database.Port

	if driver == "sqlite" { // SQLITE
		db, err = gorm.Open(sqlite.Open("gorm.db"), &gorm.Config{})
		if err != nil {
			log.WithError(err).Println("db err: ", err)
			return err
		}
	} else  { // POSTGRES
		var postgresInfo string
		if os.Getenv("GO_ENV") == "production" {
			postgresInfo = "host=" + os.Getenv(host) + " port=" + port + " user=" + os.Getenv(username) + " dbname=" + os.Getenv(database) + "  sslmode=disable password=" + os.Getenv(password)
		} else {
			postgresInfo = "host=" + host + " port=" + port + " user=" + username + " dbname=" + database + "  sslmode=disable password=" + password
		}
		db, err = gorm.Open(postgres.New(postgres.Config{
			DSN: postgresInfo,
		}), &gorm.Config{})

		if err != nil {

			log.WithError(err).Println("db err: ", err)
			return err
		}
	}
	// Change this to true if you want to see SQL queries
	myDB, err := db.DB()
	if err != nil {
		log.WithError(err).Println("db err: ", err)
		return err
	}
	myDB.SetMaxIdleConns(configuration.Database.MaxIdleConns)
	myDB.SetMaxOpenConns(configuration.Database.MaxOpenConns)
	myDB.SetConnMaxLifetime(time.Duration(configuration.Database.MaxLifetime) * time.Second)
	DB = db
	if err := migration(); err != nil {
		return err
	}
	return nil
}

// Auto migrate project models
func migration() error {
	err := DB.AutoMigrate(
		&models.Twit{},
	)
	if err != nil {
		log.WithError(err).Printf("failed to migrate")
		return err
	}
	return nil
}

// GetDB ...
func GetDB() *gorm.DB {
	return DB
}
