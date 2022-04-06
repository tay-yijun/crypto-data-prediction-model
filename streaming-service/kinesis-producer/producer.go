package kinesis_producer

import (
	"os"
	log "github.com/sirupsen/logrus"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/kinesis"
)



// AWSKinesis struct contain all field needed in kinesis stream
type AWSKinesis struct {
	stream          string
	region          string
	endpoint        string
	accessKeyID     string
	secretAccessKey string
	sessionToken    string
}

// GetKinesis ...
func GetKinesis()  AWSKinesis {
	return AWSKinesis{
		stream:          os.Getenv("KINESIS_STREAM_NAME"),
		region:          os.Getenv("KINESIS_REGION"),
		endpoint:        os.Getenv("AWS_ENDPOINT"),
		accessKeyID:     os.Getenv("AWS_ACCESS_KEY_ID"),
		secretAccessKey: os.Getenv("AWS_SECRET_ACCESS_KEY"),
		sessionToken:    os.Getenv("AWS_SESSION_TOKEN"),
	}
}

func GetProducer() (*kinesis.Kinesis, error) {
	producer := GetKinesis()
	s := session.New(&aws.Config{
		Region:      aws.String(producer.region),
		Endpoint:    aws.String(producer.endpoint),
		Credentials: credentials.NewStaticCredentials(producer.accessKeyID, producer.secretAccessKey, producer.sessionToken),
	})
	kc := kinesis.New(s)
	streamName := aws.String(producer.stream)
	_, err := kc.DescribeStream(&kinesis.DescribeStreamInput{StreamName: streamName})
	//if no stream name in AWS
	if err != nil {
		return nil, err
	}
	out, err := kc.CreateStream(&kinesis.CreateStreamInput{
		ShardCount: aws.Int64(1),
		StreamName: streamName,
	})
	if out.GoString() == "ACTIVE" {
		log.Printf("Streamnames was created, and status is: %s", out.GoString())
	} else if out.GoString() == "CREATING_FAILED" {
		log.Printf("Streamnames was falied to create, and status is: %s", out.GoString())
	}
	//if no stream name in AWS
	if err != nil {
		return nil, err
	}

	return kc, nil
}
