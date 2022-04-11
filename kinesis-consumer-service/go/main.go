package main

import (
	"context"
	"fmt"
	"kinesis_consumer_service/controller"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	log "github.com/sirupsen/logrus"
)

// HandleRequest ...
func HandleRequest(ctx context.Context, name App) (string, error) {
	log.SetFormatter(&log.JSONFormatter{})
	log.WithFields(
		log.Fields{
			"AppName":    "AWS Kinesis Consumer",
			"AppVersion": "v1",
		}).Info("Starting the app...")
	log.Printf("Job is started at %s", time.Now().Local().String())
	err := controller.GetKinesisConsumer()
	if err != nil {
		return "", err
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
