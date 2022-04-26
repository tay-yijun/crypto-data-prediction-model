# Twitter Kinesis Consumer Service
1. Golang-Lambda Consumer
3. Golang Confluent Kafka Consumer
4. AWS Kinesis Consumer

##  Architecture Diagram
![Architecture Diagram](https://kinesis-consumer-service/blob/main/kinesis-consumerDiagram.png)

##  To deploy (1)
```shell script
1. GOOS=linux GOARCH=amd64 go build -o main main.go
2. zip -r ./main.zip  *
3. Upload to labmda function
```
## To deploy (2) via aws-cli
```shell script
1. Build Image: docker build -t kinesis-consumer-[version] .
2. Create RCR Repo: aws ecr create-repository --repository-name kinesis-consumer-[version] --image-scanning-configuration scanOnPush=true
3. Tag image to repo: docker tag  kinesis-consumer-[version]:latest [ecr_repo_id].dkr.ecr.ap-southeast-1.amazonaws.com/kinesis-consumer-kinesis-consumer-[version]:latest
4. Login to ECR: aws ecr get-login-password | docker login --username AWS --password-stdin [ecr_repo_id].dkr.ecr.ap-southeast-1.amazonaws.com
5. Push Image to ECR: docker push [ecr_repo_id].dkr.ecr.ap-southeast-1.amazonaws.com/kinesis-consumer-[version]:latest
6. To invoke: aws lambda invoke --function-name kinesis-consumer  output.txt 
```
6. Add env variables
```shell script
export MONGO_URI=
export TWITTER_TOKEN=
export TWITTER_URL=
export SEARCH_PATH=
export SENTIMENT_BASE_URL=
export SENTIMENT_PATH=
export GO_ENV=
export AWS_ENDPOINT=
export DB_NAME=
export USERNAME=
export DB_PASSWORD=
```

#### Contributed by: Tony
