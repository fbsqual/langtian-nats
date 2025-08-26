package main

import (
	"time"
)

// PoC configuration
var (
	PullBatchSize = 100
	PullWait      = 2 * time.Second
	DurableName   = "sqlflow_durable"
)

// These could be later wired to env/config file
type Config struct {
	NatsURL string
}
