package main

import (
	"testing"
)

func TestConfigDefaults(t *testing.T) {
	if PullBatchSize <= 0 {
		t.Fatalf("PullBatchSize must be >0")
	}
	if PullWait <= 0 {
		t.Fatalf("PullWait must be >0")
	}
}
