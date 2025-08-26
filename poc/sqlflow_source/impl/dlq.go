package main

import "log"

// Simple DLQ recorder for PoC (in-memory counter)
var dlqCount int

func recordDLQ(msg []byte) {
	dlqCount++
	log.Printf("DLQ recorded, total=%d", dlqCount)
}
