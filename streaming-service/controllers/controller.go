package controllers

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"

	"streaming-service/configs"
	helpers "streaming-service/helper"
	"streaming-service/models"
	"streaming-service/responses"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

var coinPriceCollection *mongo.Collection = configs.GetCollection(configs.DB, "posts")


// PerPAGE ...
const PerPAGE = "100"

// SyncRecords ...
func SyncRecords() gin.HandlerFunc {
	return func(c *gin.Context) {
		Sync()
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

func saveIntoDB(cxt context.Context, twitterClient helpers.HTTPClient, path *url.URL) error {
	searchPathQ := path.Query()
	//searchPathQ.Set("tweet.fields", "source,created_at")
	//searchPathQ.Set("max_results", "100")
	path.RawQuery = searchPathQ.Encode()
	responseData, responseStatusCode, err := twitterClient.MakeRequest(cxt, "GET", path, nil)
	if responseStatusCode != 200 {
		var errResponse responses.ErrorResponse
		_ = json.Unmarshal(responseData, &errResponse)
		log.Printf("reponse %v", string(responseData))
		return fmt.Errorf("bad Request")
	}
	var searchResponse responses.RecentSearchAPIResponse
	err = json.Unmarshal(responseData, &searchResponse)
	if err != nil {
		log.Printf("Unmarshal err: %v", err)
		return err
	}
	log.Printf("PerPAGE: %s, total retrieved: %d", PerPAGE, len(searchResponse.Data))
	_, err = coinPriceCollection.InsertMany(cxt, searchResponse.Data)
	if err != nil {
		log.Printf("failed to save into DB %v", err)
		return err
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
	twitterClient, err := helpers.NewHTTPClient(config)
	if err != nil {
		return err
	}
	twitURL, _ := url.Parse(os.Getenv("COIN_MARKET_URL"))
	searchPath := &url.URL{Path: os.Getenv("SEARCH_PATH")}
	searchPathURL := twitURL.ResolveReference(searchPath)
	err = saveIntoDB(cxt, twitterClient, searchPathURL)
	if err != nil {
		return err
	}
	return nil
}