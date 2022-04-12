package service

import (
	"encoding/json"
	"os"
	"strconv"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/kinesis"
	log "github.com/sirupsen/logrus"
)

func GetKinesisConsumer() error {
	// connect to aws-kinesis
	config := GetKinesisConfig()
	mySession := session.Must(session.NewSession())
	kc := kinesis.New(mySession, &aws.Config{
		Region:      aws.String(config.region),
		Endpoint:    aws.String(config.endpoint),
		Credentials: credentials.NewStaticCredentials(config.accessKeyID, config.secretAccessKey, config.sessionToken),
	})
	streamName := aws.String(config.stream)
	streams, err := kc.DescribeStream(&kinesis.DescribeStreamInput{StreamName: streamName})
	if err != nil {
		log.WithError(err).Infof("Failed to listen to stream: %s", config.stream)
		return err
	}
	// retrieve iterator
	iteratorOutput, err := kc.GetShardIterator(&kinesis.GetShardIteratorInput{
		ShardId: aws.String(*streams.StreamDescription.Shards[0].ShardId),
		// TRIM_HORIZON - Start reading at the last untrimmed record in the shard in the system, which is the oldest data record in the shard.
		ShardIteratorType:      aws.String("TRIM_HORIZON"),
		StreamName:             streamName,
	})
	if err != nil {
		log.WithError(err).Infof("Failed to read from shareds: %s", *streams.StreamDescription.Shards[0].ShardId)
		return err
	}

	shardIterator := iteratorOutput.ShardIterator
	var a *string

	var limit = os.Getenv("KINESIS_RECORD_LIMIT")
	if limit == "" {
		limit = "1000"
	}
	limitInt, _ := strconv.ParseInt(limit, 10, 64)
	// get data using infinity looping
	// we will attempt to consume data every 1 seconds, if no data, nothing will be happened
	for {
		// get records use shard iterator for making request
		records, err := kc.GetRecords(&kinesis.GetRecordsInput{
			Limit:         aws.Int64(limitInt),
			ShardIterator: shardIterator,
		})

		// if error, wait until 1 seconds and continue the looping process
		if err != nil {
			time.Sleep(1000 * time.Millisecond)
			log.WithError(err).Info("Failed get records from ShardIterator")
			continue
		}

		// process the data
		if len(records.Records) > 0 {
			for _, d := range records.Records {
				m := make(map[string]interface{})
				err := json.Unmarshal(d.Data, &m)
				if err != nil {
					log.WithError(err).Infof("failed unmarshal data: %v", d.Data)
					continue
				}
				log.Printf("GetRecords Data: %v\n", m)
			}
		} else if records.NextShardIterator == a || shardIterator == records.NextShardIterator || err != nil {
			log.WithError(err).Printf("GetRecords ERROR: %v\n", err)
			break
		}
		shardIterator = records.NextShardIterator
		time.Sleep(1000 * time.Millisecond)
	}
	return nil
}
