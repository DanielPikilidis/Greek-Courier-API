package main

import (
	"strings"
	"testing"
)

func TestTrackOne(t *testing.T) {
	validID := "Q8DNX1JMX6K0R"
	invalidID := "Q8DNX1JMX6K0X"

	logger, _ := NewLogger()

	packages, err := trackOne(validID, logger)

	if err != nil {
		t.Error("Error while tracking valid ID: ", err)
	}

	if packages[validID].Found != true {
		t.Error("Expected found to be true")
	}

	packages, err = trackOne(invalidID, logger)

	if err != nil {
		t.Error("Error while tracking invalid ID: ", err)
	}

	if packages[invalidID].Found != false {
		t.Error("Expected found to be false")
	}
}

func TestTrackMany(t *testing.T) {
	validIDs := "N3OKM1X0Z0D8J&N3OKM6PNXVG8J&N3OKMR30Q4D8J"
	invalidIDs := "N4OKM1X0Z0D8J&N5OKM1X0Z0D8J&N6OKM1X0Z0D8J"

	logger, _ := NewLogger()

	packages, err := trackMany(validIDs, logger)

	if err != nil {
		t.Error("Error while tracking valid IDs: ", err)
	}

	for _, id := range strings.Split(validIDs, "&") {
		if packages[id].Found != true {
			t.Error("Expected found to be true")
		}
	}

	packages, err = trackMany(invalidIDs, logger)

	if err != nil {
		t.Error("Error while tracking invalid IDs: ", err)
	}

	for _, id := range strings.Split(invalidIDs, "&") {
		if packages[id].Found != false {
			t.Error("Expected found to be false")
		}
	}
}
