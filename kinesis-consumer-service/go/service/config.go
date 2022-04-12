package service

import "os"

// AWSKinesis struct contain all field needed in kinesis stream
type AWSKinesis struct {
	stream          string
	region          string
	endpoint        string
	accessKeyID     string
	secretAccessKey string
	sessionToken    string
}

// GetKinesisConfig ...
func GetKinesisConfig() AWSKinesis {
	return AWSKinesis{
		stream:          os.Getenv("KINESIS_STREAM_NAME"),
		region:          os.Getenv("KINESIS_REGION"),
		endpoint:        os.Getenv("AWS_ENDPOINT"),
		accessKeyID:     os.Getenv("AWS_ACCESS_KEY_ID"),
		secretAccessKey: os.Getenv("AWS_SECRET_ACCESS_KEY"),
		sessionToken:    os.Getenv("AWS_SESSION_TOKEN"),
	}
}

