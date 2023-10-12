package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"sync"
	"time"
)

var trackingUrl string = "https://api.sendx.gr/user/hp/%s"

type Package struct {
	Found       bool       `json:"found"`
	CourierName string     `json:"courier_name"`
	CourierIcon string     `json:"courier_icon"`
	Locations   []Location `json:"locations"`
	Delivered   bool       `json:"delivered"`
}

func NewPackage() *Package {
	return &Package{
		Found:       false,
		CourierName: "Skroutz Last Mile",
		CourierIcon: "https://i.imgur.com/FmhZYBQ.png",
		Locations:   make([]Location, 0),
		Delivered:   false,
	}
}

type Location struct {
	Datetime    string `json:"datetime"`
	Location    string `json:"location"`
	Description string `json:"description"`
}

type SkroutzResponse struct {
	TrackingDetails []SkroutzLocation `json:"trackingDetails"`
	Delivered       interface{}       `json:"deliveredAt"`
}

type SkroutzLocation struct {
	UpdatedAt   string `json:"updatedAt"`
	Checkpoint  string `json:"checkpoint"`
	Description string `json:"description"`
}

func trackOne(id string) (map[string]*Package, *TrackingError) {
	p := NewPackage()

	url := fmt.Sprintf(trackingUrl, id)
	resp, err := http.Get(url)
	if err != nil {
		logger.Warning("Error while retrieving info for ", id, ": ", err)
		return nil, &TrackingError{Code: 500, Message: "Error while retrieving info for " + id}
	}

	if resp.StatusCode >= 400 {
		return map[string]*Package{id: p}, nil
	}
	defer resp.Body.Close()

	p.Found = true

	var skroutzResponse SkroutzResponse
	json.NewDecoder(resp.Body).Decode(&skroutzResponse)

	for _, status := range skroutzResponse.TrackingDetails {
		var location Location

		dt, err := time.Parse(time.RFC3339Nano, status.UpdatedAt)
		if err != nil {
			logger.Warning("Error while parsing date for ", id, ": ", err)
			return nil, &TrackingError{Code: 500, Message: "Failed to parse response."}
		}

		// Adding the fields for the response formatted the way we want
		loc, _ := time.LoadLocation("Europe/Athens")
		location.Datetime = dt.In(loc).Format(time.RFC3339)
		location.Location = status.Checkpoint
		location.Description = status.Description
		p.Locations = append(p.Locations, location)
	}

	if skroutzResponse.Delivered != nil {
		p.Delivered = true
	}

	logger.Info("Tracked ", id, " successfully")

	return map[string]*Package{id: p}, nil
}

func trackMany(ids string) (map[string]*Package, *TrackingError) {
	idsSlice := strings.Split(ids, "&") // Should probably also check for duplicates...

	packages := make(map[string]*Package)

	// There's no way get multiple packages with one request, so I have to make a request for each id by starting a lot of goroutines
	var wg sync.WaitGroup
	for _, id := range idsSlice {
		wg.Add(1)
		go func(id string) {
			trackingInfo, err := trackOne(id)
			if err != nil {
				packages[id] = NewPackage()
			} else {
				packages[id] = trackingInfo[id]
			}
			wg.Done()
		}(id)
	}
	wg.Wait()
	return packages, nil
}
