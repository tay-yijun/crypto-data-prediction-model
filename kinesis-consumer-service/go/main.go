package main

import (
	"context"
	"fmt"
	"github.com/aws/aws-lambda-go/events"
	"kinesis_consumer_service/controllers"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	log "github.com/sirupsen/logrus"
)

// HandleRequest ...
func HandleRequest(ctx context.Context, kinesisEvent events.KinesisEvent) (string, error) {
	log.SetFormatter(&log.JSONFormatter{})
	log.WithFields(
		log.Fields{
			"AppName":    "AWS Kinesis Consumer",
			"AppVersion": "v1",
		}).Info("Starting the app...")
	log.Printf("Job is started at %s", time.Now().Local().String())
	for _, record := range kinesisEvent.Records {
		kinesisRecord := record.Kinesis
		dataBytes := kinesisRecord.Data
		dataText := string(dataBytes)
		fmt.Printf("%s Data = %s \n", record.EventName, dataText)
		if err := controllers.Run(kinesisRecord.Data); err != nil {
			return "", err
		}
	}
	log.Printf("At the end of my job, let's rest now! Completed time %s", time.Now().Local().String())
	return fmt.Sprintf("Resources are saved,!"), nil
}

func main() {
	lambda.Start(HandleRequest)
}
