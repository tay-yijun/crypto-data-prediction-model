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

	"twitter-service/configs"
	helpers "twitter-service/helper"
	"twitter-service/models"
	"twitter-service/responses"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

var twitPostCollection *mongo.Collection = configs.GetCollection(configs.DB, "posts")

// PerPAGE ...
const PerPAGE = "100"

// SyncPosts ...
func SyncPosts() gin.HandlerFunc {
	return func(c *gin.Context) {
		err, data := Sync()
		if err != nil {
			c.JSON(http.StatusForbidden, responses.TwitPostResponse{Status: http.StatusCreated, Message: "success", Data: err})
			return
		}
		c.JSON(http.StatusCreated, responses.TwitPostResponse{Status: http.StatusCreated, Message: "success", Data: string(data)})
	}
}

// GetAllTwits ...
func GetAllTwits() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		var posts []models.TwitPost
		defer cancel()

		results, err := twitPostCollection.Find(ctx, bson.M{})

		if err != nil {
			c.JSON(http.StatusInternalServerError, responses.TwitPostResponse{Status: http.StatusInternalServerError, Message: "error", Data: err})
			return
		}

		//reading from the db in an optimal way
		defer results.Close(ctx)
		for results.Next(ctx) {
			var singleTwitPost models.TwitPost
			if err = results.Decode(&singleTwitPost); err != nil {
				c.JSON(http.StatusInternalServerError, responses.TwitPostResponse{Status: http.StatusInternalServerError, Message: "error", Data: map[string]interface{}{"data": err.Error()}})
			}

			posts = append(posts, singleTwitPost)
		}

		c.JSON(http.StatusOK,
			responses.TwitPostResponse{Status: http.StatusOK, Message: "success", Data: map[string]interface{}{"data": posts}},
		)
	}
}

func saveTwitsIntoDB(cxt context.Context, twitterClient helpers.HTTPClient, path *url.URL, keyword string) (error, []byte) {
	searchPathQ := path.Query()
	searchPathQ.Set("query", keyword)
	searchPathQ.Set("tweet.fields", "source,created_at")
	searchPathQ.Set("max_results", "100")
	path.RawQuery = searchPathQ.Encode()
	responseData, responseStatusCode, err := twitterClient.MakeRequest(cxt, "GET", path, nil)
	if responseStatusCode != 200 {
		var errResponse responses.ErrorResponse
		_ = json.Unmarshal(responseData, &errResponse)
		log.Printf("reponse %v", string(responseData))
		return fmt.Errorf("bad Request"), nil
	}
	var searchResponse responses.RecentSearchAPIResponse
	err = json.Unmarshal(responseData, &searchResponse)
	if err != nil {
		log.Printf("Unmarshal err: %v", err)
		return err, nil
	}
	log.Printf("PerPAGE: %s, total retrieved: %d", PerPAGE, len(searchResponse.Data))
	_, err = twitPostCollection.InsertMany(cxt, searchResponse.Data)
	if err != nil {
		log.Printf("failed to save into DB %v", err)
		return err, nil
	}
	return nil, responseData
}

// Sync ...
func Sync() (error, []byte) {
	cxt, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	config := helpers.HttPConfig{
		RequestTimeout: 30,
		SSLEnabled:     false,
		Username:       os.Getenv("USERNAME"),
		Password:       os.Getenv("PASSWORD"),
	}
	twitterClient, err := helpers.NewHTTPClient(config)
	if err != nil {
		log.Printf("err %v", err)
	}
	twitURL, _ := url.Parse(os.Getenv("TWITTER_URL"))
	searchPath := &url.URL{Path: os.Getenv("SEARCH_PATH")}
	searchPathURL := twitURL.ResolveReference(searchPath)
	var coinsStr = os.Getenv("COINS")
	if os.Getenv("COINS") == "" {
		coinsStr = "bitcoin"
	}
	err, data := saveTwitsIntoDB(cxt, twitterClient, searchPathURL, coinsStr)
	defer cancel()
	if err != nil {
		return err, nil
	}
	return nil, data
}
