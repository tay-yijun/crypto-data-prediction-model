package models

import "encoding/json"

type PriceStatistics struct {
	ID                 json.Number `json:"id,omitempty"`
	Symbol             string      `json:"symbol"`
	PriceChange        string      `json:"priceChange"`
	PriceChangePercent string      `json:"priceChangePercent"`
	WeightedAvgPrice   string      `json:"weightedAvgPrice"`
	PrevClosePrice     string      `json:"prevClosePrice"`
	LastPrice          string      `json:"lastPrice"`
	LastQty            string      `json:"lastQty"`
	BidPrice           string      `json:"bidPrice"`
	BidQty             string      `json:"bidQty"`
	AskPrice           string      `json:"askPrice"`
	AskQty             string      `json:"askQty"`
	OpenPrice          string      `json:"openPrice"`
	HighPrice          string      `json:"highPrice"`
	LowPrice           string      `json:"lowPrice"`
	Volume             string      `json:"volume"`
	QuoteVolume        string      `json:"quoteVolume"`
	OpenTime           int64       `json:"openTime"`
	CloseTime          int64       `json:"closeTime"`
	FirstID            int         `json:"firstId"`
	LastID             int         `json:"lastId"`
	Count              int         `json:"count"`
}
