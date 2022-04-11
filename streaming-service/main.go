package main

import (
	"context"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/kinesis"
	"os"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	log "github.com/sirupsen/logrus"

	"streaming-service/controllers"
	kinesisProducer "streaming-service/kinesis-producer"
)

// HandleRequest ...
func HandleRequest(ctx context.Context, name App) (string, error) {
	log.SetFormatter(&log.JSONFormatter{})
	log.WithFields(
		log.Fields{
			"AppName":   "Coin Market Migration",
			"AppVersion": "v1",
		}).Info("Starting the app...")
	log.Printf("Job is started at %s", time.Now().Local().String())
	err, data := controllers.Sync()
	if err != nil {
		return "", err
	}
	if os.Getenv("KINESIS_PRODUCER_ENABLED") == "enabled" {
		kc, err := kinesisProducer.GetProducer()
		if err != nil {
			log.Printf("failed to producer create AWS  %v", err)
		}
		streamName := aws.String(os.Getenv("KINESIS_STREAM_NAME"))
		putOutput, recordErr := kc.PutRecord(&kinesis.PutRecordInput{
			Data:         data,
			StreamName:   streamName,
			PartitionKey: aws.String(os.Getenv("PARTITION_KEY")),
		})
		if recordErr != nil {
			log.Printf("failed to put data to producer:  %v", err)
		} else {
			log.Printf("Data is sent to stream %s successfully, AWS kinesis output: %s", os.Getenv("KINESIS_STREAM_NAME"), putOutput.String())
		}
	}
	log.Printf("At the end of my job, let's rest now! Completed time %s", time.Now().Local().String())
	return fmt.Sprintf("Resources are saved %s by!", name.Name), nil
}

// App - the struct which contains information about our app
type App struct {
	Name    string
	Version string
}

func main() {
	lambda.Start(HandleRequest)
}