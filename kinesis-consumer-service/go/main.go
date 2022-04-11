package main

import (
	"context"
	"fmt"
	"github.com/aws/aws-lambda-go/events"
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
		// todo:
		// 1. result := GetPredictionResult(kinesisRecord.Data) -> Call sentiment/prediction model get result
		// 2. SaveIntoDB(result) -> save prediction result in to postgres
	}
	log.Printf("At the end of my job, let's rest now! Completed time %s", time.Now().Local().String())
	return fmt.Sprintf("Resources are saved,!"), nil
}

func main() {
	lambda.Start(HandleRequest)
}
