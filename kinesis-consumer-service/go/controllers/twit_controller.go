package controllers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	log "github.com/sirupsen/logrus"
	"kinesis_consumer_service/helpers"
	"kinesis_consumer_service/pkg/config"
	"kinesis_consumer_service/pkg/models"
	"kinesis_consumer_service/pkg/persistence"
	"net/url"
	"os"
)

// TwitterInstance ...
type TwitterInstance struct{}

// TwitterI ...
//go:generate mockery --name=TwitterI --inpackage=false --output=./mocks
// TwitterI interface helps us to mock sync api call
type TwitterI interface {
	SyncTwitterResource()
}

// PerPAGE ...
const PerPAGE = 100

// Run ...
func Run(data []byte ) error {
	myConfig := config.GetConfig()

	var httPConfig = helpers.HttPConfig{
		RequestTimeout: 30,
		SSLEnabled:     false,
		Username:       os.Getenv(myConfig.Database.TwitterToken),
	}
	var err error
	baseURL, _ := url.Parse(os.Getenv("SENTIMENT_BASE_URL"))

	var reports []models.Report
	sourcePath := &url.URL{Path: os.Getenv("SENTIMENT_PATH")}
	sourcePathURL := baseURL.ResolveReference(sourcePath)
	err = saveTwits(httPConfig, sourcePathURL, data)
	if err != nil {
		reports = append(reports, models.Report{
			TaskName: "sources",
			Status:   "Failed",
			Message:  fmt.Sprintf("Failed to save sources to DB: %s", err.Error()),
		})
	} else {
		reports = append(reports, models.Report{
			TaskName: "Sources",
			Status:   "Completed",
		})
	}
	return nil
}

func saveTwits(config helpers.HttPConfig, path *url.URL, data []byte) error {
	log.Printf("sourcePathURL:%s", path)
	var response helpers.APIResponse
	twitterClient, err := helpers.NewHTTPClient(config)
	if err != nil {
		return err
	}
	responseData, responseStatusCode, err := twitterClient.MakeRequest(context.Background(), "POST", path, data)
	if err != nil {
		return err
	}
	if responseStatusCode != 200 {
		return errors.New("invalid request")
	}
	err = json.Unmarshal(responseData, &response)
	if err != nil {
		return err
	}
	persistence.CreateOrUpdate(&response.Data)
	return nil
}