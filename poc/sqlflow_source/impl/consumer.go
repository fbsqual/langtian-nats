package main

import (
	"log"
	"time"

	"github.com/nats-io/nats.go"
)

// Consumer encapsulates JetStream consumer interactions
type Consumer struct {
	js  nats.JetStreamContext
	sub *nats.Subscription
}

func NewConsumer(js nats.JetStreamContext, durable string) (*Consumer, error) {
	// Ensure durable consumer exists by PullSubscribe call
	sub, err := js.PullSubscribe("battery.telemetry", durable)
	if err != nil {
		return nil, err
	}
	return &Consumer{js: js, sub: sub}, nil
}

// FetchBatch fetches up to batchSize messages with timeout and returns slice
func (c *Consumer) FetchBatch(batchSize int, wait time.Duration) ([]*nats.Msg, error) {
	msgs, err := c.sub.Fetch(batchSize, nats.MaxWait(wait))
	if err != nil && err != nats.ErrTimeout {
		return nil, err
	}
	return msgs, nil
}

// AckBatch acknowledges messages on success
func (c *Consumer) AckBatch(msgs []*nats.Msg) {
	for _, m := range msgs {
		if err := m.Ack(); err != nil {
			log.Printf("ack failed: %v", err)
		}
	}
}

// SendToDLQ publishes a given message to a DLQ subject
func (c *Consumer) SendToDLQ(m *nats.Msg) {
	_, err := c.js.Publish("battery.dlq", m.Data)
	if err != nil {
		log.Printf("dlq publish failed: %v", err)
	}
}
