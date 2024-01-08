package main

import (
	"strings"
	"testing"
)

func TestTrackOne(t *testing.T) {
	invalidID := "1111111111111"

	logger, _ := NewLogger()

	packages, err := trackOne(invalidID, logger)

	if err != nil {
		t.Error("Error while tracking invalid ID: ", err)
	}

	if packages[invalidID].Found != false {
		t.Error("Expected found to be false")
	}
}

func TestTrackMany(t *testing.T) {
	invalidIDs := "1111111111111&1111111111112&1111111111113"

	logger, _ := NewLogger()

	packages, err := trackMany(invalidIDs, logger)

	if err != nil {
		t.Error("Error while tracking invalid IDs: ", err)
	}

	for _, id := range strings.Split(invalidIDs, "&") {
		if packages[id].Found != false {
			t.Error("Expected found to be false")
		}
	}
}
