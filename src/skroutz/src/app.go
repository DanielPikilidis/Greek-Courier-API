package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/url"
	"os"

	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

var logger *logrus.Logger
var proxyHost string

func main() {
	logger, _ = NewLogger()
	logger.Info("Initialized logger")

	router := mux.NewRouter()
	router.HandleFunc("/track-one/{id}", track_one_handler)
	router.HandleFunc("/track-many/{ids}", track_many_handler)

	useProxy := getEnvCustom("USE_PROXY", "false")
	if useProxy == "true" {
		err := requestProxy()
		if err != nil {
			logger.Error("Failed to get proxy: ", err)
		}
		defer releaseProxy()
	}

	port := getEnvCustom("PORT", "8000")
	logger.Info("Starting server on port " + port)
	http.ListenAndServe(":"+port, router)
}

type TrackingError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type ResponseError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type Response struct {
	Success bool           `json:"success"`
	Data    interface{}    `json:"data"`
	Error   *ResponseError `json:"error"`
}

func track_one_handler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	w.Header().Set("Content-Type", "application/json")

	trackingInfo, err := trackOne(id)
	if err != nil {
		response := Response{
			Success: false,
			Data:    nil,
			Error: &ResponseError{
				Code:    err.Code,
				Message: err.Message,
			},
		}
		resp, _ := json.Marshal(response)
		w.Write(resp)
	} else {
		response := Response{
			Success: true,
			Data:    trackingInfo,
			Error: &ResponseError{
				Code:    200,
				Message: "",
			},
		}
		resp, _ := json.Marshal(response)
		w.Write(resp)
	}
}

func track_many_handler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	ids := vars["ids"]

	packages, _ := trackMany(ids)

	response := Response{
		Success: true,
		Data:    packages,
		Error: &ResponseError{
			Code:    200,
			Message: "",
		},
	}

	resp, _ := json.Marshal(response)

	w.Header().Set("Content-Type", "application/json")
	w.Write(resp)
}

func requestProxy() error {
	type Proxy struct {
		Type     string `json:"type"`
		Host     string `json:"host"`
		Username string `json:"username"`
		Password string `json:"password"`
	}

	pmPort := getEnvCustom("PM_PORT", "80")

	resp, err := http.Get("http://proxy-manager-service:" + string(pmPort) + "/request-proxy/skroutz")
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	proxy := &Proxy{}
	err = json.NewDecoder(resp.Body).Decode(proxy)
	if err != nil {
		return err
	}

	logger.Info("Got proxy: ", proxy.Host)

	proxyUrl, _ := url.Parse(proxy.Type + "://" + proxy.Username + ":" + proxy.Password + "@" + proxy.Host)
	http.DefaultTransport = &http.Transport{Proxy: http.ProxyURL(proxyUrl)}
	proxyHost = proxy.Host

	return nil
}

func releaseProxy() {
	body := []byte(`{
		"host": ` + proxyHost + `
	}`)

	logger.Info("Release proxy: ", proxyHost)
	pmPort := getEnvCustom("PM_PORT", "80")
	http.Post("http://proxy-manager-service:"+string(pmPort)+"/release-proxy/skroutz", "application/json", bytes.NewBuffer(body))
}

func getEnvCustom(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
