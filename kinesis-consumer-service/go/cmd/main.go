package main

import (
	log "github.com/sirupsen/logrus"
	"kinesis_consumer_service/controllers"
	"kinesis_consumer_service/pkg/config"
	"kinesis_consumer_service/pkg/db"
)

func main()  {
	payload := `{"data":[{"created_at": "2022-03-28T11:53:15.000Z","text": "Hello"},{"created_at": "2022-03-28T11:53:15.000Z","text": "Hello 2"}]}`
	err := config.Setup("config/config.yml")
	if err != nil {
		log.WithError(err).Info("Failed to setup db")
	}
	err = db.SetupDB()
	if err != nil {
		log.WithError(err).Info("Failed to connect db")
	}
	err = controllers.Run([]byte(payload))
	if err != nil {
		log.WithError(err)
	}
}
