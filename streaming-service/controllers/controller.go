package controllers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/kinesis"

	log "github.com/sirupsen/logrus"
	"streaming-service/configs"
	helpers "streaming-service/helper"
	"streaming-service/models"
	"streaming-service/responses"

	kinesis_producer "streaming-service/kinesis-producer"
)

var coinPriceCollection *mongo.Collection = configs.GetCollection(configs.DB, "priceRecords")

// PerPAGE ...
const PerPAGE = "100"

// SyncRecords ...
func SyncRecords() gin.HandlerFunc {
	return func(c *gin.Context) {
		err := Sync()
		if err != nil {
			c.JSON(http.StatusBadRequest, responses.TransactionRecordResponse{Status: http.StatusCreated, Message: err.Error()})
			return
		}
		c.JSON(http.StatusCreated, responses.TransactionRecordResponse{Status: http.StatusCreated, Message: "success"})
	}
}

// GetAllTRecords ...
func GetAllTRecords() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		var currentPrices []models.TickerPrice
		defer cancel()

		results, err := coinPriceCollection.Find(ctx, bson.M{})

		if err != nil {
			c.JSON(http.StatusInternalServerError, responses.TransactionRecordResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			return
		}

		//reading from the db in an optimal way
		defer results.Close(ctx)
		for results.Next(ctx) {
			var singleTransactionRecord models.TickerPrice
			if err = results.Decode(&singleTransactionRecord); err != nil {
				c.JSON(http.StatusInternalServerError, responses.TransactionRecordResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			}

			currentPrices = append(currentPrices, singleTransactionRecord)
		}

		c.JSON(http.StatusOK,
			responses.TransactionRecordResponse{Status: http.StatusOK, Message: "success", Data: map[string]interface{}{"data": currentPrices}},
		)
	}

}

func saveIntoDB(cxt context.Context, binanceClient helpers.HTTPClient, path *url.URL) error {
	searchPathQ := path.Query()
	searchPathQ.Set("symbol", os.Getenv("COIN_SYMBOL"))
	path.RawQuery = searchPathQ.Encode()
	responseData, responseStatusCode, err := binanceClient.MakeRequest(cxt, "GET", path, nil)
	if responseStatusCode != 200 {
		var errResponse responses.ErrorResponse
		_ = json.Unmarshal(responseData, &errResponse)
		log.Printf("reponse %v", string(responseData))
		return fmt.Errorf("bad Request")
	}
	var tradeResponse models.CurrentPrice
	err = json.Unmarshal(responseData, &tradeResponse)
	if err != nil {
		log.Printf("Unmarshal err: %v", err)
		return err
	}

	_, err = coinPriceCollection.InsertOne(cxt, &models.TickerPrice{
		Price: tradeResponse.Price,
		Time:  time.Now().UTC(),
	})
	if err != nil {
		log.Printf("failed to save into DB %v", err)
		return err
	}
	kc, err := kinesis_producer.GetProducer()
	if err != nil {
		log.Printf("failed to produceer create AWS  %v", err)
	}
	streamName := aws.String(os.Getenv("KINESIS_STREAM_NAME"))
	putOutput, err := kc.PutRecord(&kinesis.PutRecordInput{
		Data:         responseData,
		StreamName:   streamName,
		PartitionKey: aws.String("key1"),
	})
	if err != nil {
		log.Printf("failed to send data to producer %v", err)
	}
	log.Printf("AWS kinesis output: %s", putOutput.String())
	return nil
}

// Sync ...
func Sync() error {
	cxt, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	config := helpers.HttPConfig{
		RequestTimeout: 30,
		SSLEnabled:     false,
		Username:       os.Getenv("USERNAME"),
		Password:       os.Getenv("PASSWORD"),
	}
	defer cancel()
	binanceClient, err := helpers.NewHTTPClient(config)
	if err != nil {
		return err
	}
	binanceURL, _ := url.Parse(os.Getenv("BINANCE_URL"))
	searchPath := &url.URL{Path: os.Getenv("TRADE_PATH")}
	searchPathURL := binanceURL.ResolveReference(searchPath)
	err = saveIntoDB(cxt, binanceClient, searchPathURL)
	if err != nil {
		return err
	}
	return nil
}
