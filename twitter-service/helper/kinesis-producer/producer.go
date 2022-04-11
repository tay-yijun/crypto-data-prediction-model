package kinesis_producer

import (
	log "github.com/sirupsen/logrus"
	"os"

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
func GetKinesis() AWSKinesis {
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
	mySession := session.Must(session.NewSession())
	kc := kinesis.New(mySession, &aws.Config{
		Region:      aws.String(producer.region),
		Endpoint:    aws.String(producer.endpoint),
		Credentials: credentials.NewStaticCredentials(producer.accessKeyID, producer.secretAccessKey, producer.sessionToken),
	})
	streamName := aws.String(producer.stream)
	_, err := kc.DescribeStream(&kinesis.DescribeStreamInput{StreamName: streamName})
	//if no stream name in AWS
	if err != nil {
		log.Printf("Stream is: %s", err.Error())
		return nil, err
	}
	return kc, nil
}
