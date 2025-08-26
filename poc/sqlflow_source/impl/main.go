package main

import (
	"log"
	"time"

	"github.com/nats-io/nats.go"
)

func main() {
	// Minimal runner for Pull-based JetStream consumer (PoC)
	nc, err := nats.Connect(nats.DefaultURL)
	if err != nil {
		log.Fatalf("nats connect: %v", err)
	}
	defer nc.Close()

	js, err := nc.JetStream()
	if err != nil {
		log.Fatalf("jetstream context: %v", err)
	}

	sub, err := js.PullSubscribe("battery.telemetry", "sqlflow_durable")
	if err != nil {
		log.Fatalf("pull subscribe: %v", err)
	}

	log.Println("sqlflow-nats-source: started pull consumer")

	for {
		msgs, err := sub.Fetch(100, nats.MaxWait(2*time.Second))
		if err != nil && err != nats.ErrTimeout {
			log.Printf("fetch err: %v", err)
			time.Sleep(time.Second)
			continue
		}
		if len(msgs) == 0 {
			// idle wait
			time.Sleep(500 * time.Millisecond)
			continue
		}

		// For PoC: hand off to a synchronous sink call and ack on success
		err = sendToSqlFlowSink(msgs)
		if err == nil {
			for _, m := range msgs {
				m.Ack()
			}
		} else {
			log.Printf("sink error: %v", err)
			// PoC simple: no ack -> will be redelivered per JetStream policy, or implement DLQ here
		}
	}
}

// sendToSqlFlowSink represents the synchronous batch handoff to sql-flow's processing/sink.
// For PoC this is a placeholder that should call into sql-flow pipeline and return nil on success.
func sendToSqlFlowSink(msgs []*nats.Msg) error {
	// ...existing code...
	// convert msgs to records, invoke SQL-Flow ingestion pipeline, wait for commit
	// For the PoC skeleton, just log and simulate success
	log.Printf("sendToSqlFlowSink: received %d msgs", len(msgs))
	// simulate processing time
	time.Sleep(100 * time.Millisecond)
	return nil
}
