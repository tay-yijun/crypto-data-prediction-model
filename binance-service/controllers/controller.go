package controllers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"

	"binance-service/configs"
	helpers "binance-service/helper"
	"binance-service/models"
	"binance-service/responses"
	log "github.com/sirupsen/logrus"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

var coinPriceCollection *mongo.Collection = configs.GetCollection(configs.DB, "transactions")

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
		var posts []models.TransactionRecord
		defer cancel()

		results, err := coinPriceCollection.Find(ctx, bson.M{})

		if err != nil {
			c.JSON(http.StatusInternalServerError, responses.TransactionRecordResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			return
		}

		//reading from the db in an optimal way
		defer results.Close(ctx)
		for results.Next(ctx) {
			var singleTransactionRecord models.TransactionRecord
			if err = results.Decode(&singleTransactionRecord); err != nil {
				c.JSON(http.StatusInternalServerError, responses.TransactionRecordResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			}

			posts = append(posts, singleTransactionRecord)
		}

		c.JSON(http.StatusOK,
			responses.TransactionRecordResponse{Status: http.StatusOK, Message: "success", Data: map[string]interface{}{"data": posts}},
		)
	}

}

// GetAllDailyPrice ...
func GetAllDailyPrice() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		var posts []models.PriceStatistics
		defer cancel()

		results, err := coinPriceCollection.Find(ctx, bson.M{})

		if err != nil {
			c.JSON(http.StatusInternalServerError, responses.TransactionRecordResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			return
		}

		//reading from the db in an optimal way
		defer results.Close(ctx)
		for results.Next(ctx) {
			var singleTransactionRecord models.PriceStatistics
			if err = results.Decode(&singleTransactionRecord); err != nil {
				c.JSON(http.StatusInternalServerError, responses.TransactionRecordResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			}

			posts = append(posts, singleTransactionRecord)
		}

		c.JSON(http.StatusOK,
			responses.TransactionRecordResponse{Status: http.StatusOK, Message: "success", Data: map[string]interface{}{"data": posts}},
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
	if os.Getenv("DATA_TYPE") == "daily_price" {
		coinPriceCollection = configs.GetCollection(configs.DB, "daily_price")
		var tradeResponse models.PriceStatistics
		err = json.Unmarshal(responseData, &tradeResponse)
		if err != nil {
			log.Printf("Unmarshal err: %v", err)
			return err
		}
		tradeResponse.ID = json.Number(strconv.FormatInt(time.Now().Unix(), 10))
		_, err = coinPriceCollection.InsertOne(cxt, tradeResponse)
		if err != nil {
			log.Printf("failed to save into DB %v", err)
			return err
		}
	} else {
		var tradeResponse []models.TransactionRecord
		err = json.Unmarshal(responseData, &tradeResponse)
		if err != nil {
			log.Printf("Unmarshal err: %v", err)
			return err
		}
		tradeResponseBytes := make([]interface{}, len(tradeResponse))
		for i := range tradeResponse {
			tradeResponseBytes[i] = tradeResponse[i]
		}
		log.Printf("PerPAGE: %s, total retrieved: %d", PerPAGE, len(tradeResponse))
		_, err = coinPriceCollection.InsertMany(cxt, tradeResponseBytes)
		if err != nil {
			log.Printf("failed to save into DB %v", err)
			return err
		}
	}
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
