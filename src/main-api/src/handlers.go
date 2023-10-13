package main

import (
	"fmt"
	"net/http"
	"strings"

	jsoniter "github.com/json-iterator/go"

	"github.com/gin-gonic/gin"
)

// @Summary Track one package
// @Description Track one package
// @Tags Tracking
// @Accept  json
// @Produce  json
// @Param courier path string true "Courier name"
// @Param id path string true "Package id"
// @Success 200 {object} Data
// @Failure 404 {object} TrackingError
// @Failure 500 Internal Server Error
// @Router /track-one/{courier}/{id} [get]
func trackOneHandler(c *gin.Context) {
	courier := c.Param("courier")
	id := c.Param("id")

	logger.Info("Tracking ", courier, "-", id)

	key := fmt.Sprintf("%s-%s", courier, id)
	if p, err := redisClient.Get(key); err == nil {
		// If the package is in the cache, return it
		packages := make(map[string]Package)
		packages[id] = p
		data := Data{
			Success: true,
			Data:    packages,
			Error: TrackingError{
				Code:    200,
				Message: "",
			},
		}
		c.JSON(200, data)
		return
	} else if err.Error() != "not found" {
		// If there's an error, log it
		logger.Error("Error while getting ", key, " from cache: ", err)
	}

	requestUrl := fmt.Sprintf("http://%s-tracker-service/track-one/%s", courier, id)
	response, err := http.Get(requestUrl)

	if err != nil {
		logger.Error(err)
		if strings.Contains(err.Error(), "no such host") {
			c.JSON(404, TrackingError{
				Code:    404,
				Message: "Courier not found",
			})
		} else {
			c.JSON(500, err)
		}
		return
	}
	defer response.Body.Close()

	var data Data
	err = jsoniter.NewDecoder(response.Body).Decode(&data)
	if err != nil {
		logger.Error("Error while unmarshalling response: ", err)
		c.JSON(500, err)
		return
	}

	if data.Data[id].Found {
		redisClient.Set(key, data.Data[id])
	}

	c.JSON(200, data)
}

// @Summary Track many packages
// @Description Track many packages
// @Tags Tracking
// @Accept  json
// @Produce  json
// @Param courier path string true "Courier name"
// @Param ids path string true "Package ids"
// @Success 200 {object} Data
// @Failure 404 {object} TrackingError
// @Failure 500 Internal Server Error
// @Router /track-many/{courier}/{ids} [get]
func trackManyHandler(c *gin.Context) {
	courier := c.Param("courier")
	ids := c.Param("ids")

	var idsToSearch []string
	cachedPackages := make(map[string]Package)
	for _, id := range strings.Split(ids, "&") {
		key := fmt.Sprintf("%s-%s", courier, id)
		if p, err := redisClient.Get(key); err == nil {
			// If the package is in the cache, add it to the list of cached packages
			cachedPackages[id] = p
		} else {
			// If there's any error, add the id to the list of ids to search
			idsToSearch = append(idsToSearch, id)
		}
	}

	var data Data

	if len(idsToSearch) > 0 {
		ids = strings.Join(idsToSearch, "&")

		requestUrl := fmt.Sprintf("http://%s-tracker-service/track-many/%s", courier, ids)
		response, err := http.Get(requestUrl)

		if err != nil {
			logger.Error(err)
			if strings.Contains(err.Error(), "no such host") {
				c.JSON(404, TrackingError{
					Code:    404,
					Message: "Courier not found",
				})
			} else {
				c.JSON(500, err)
			}
			return
		}

		err = jsoniter.NewDecoder(response.Body).Decode(&data)
		if err != nil {
			logger.Error("Error while unmarshalling response: ", err)
			data.Success = false
			data.Data = make(map[string]Package)
			data.Error = TrackingError{
				Code:    500,
				Message: err.Error(),
			}
		}
		response.Body.Close()
	} else {
		data = Data{
			Success: true,
			Data:    make(map[string]Package),
			Error: TrackingError{
				Code:    200,
				Message: "",
			},
		}
	}

	for id, p := range data.Data {
		// Adding all the new packages to the cache
		if p.Found {
			key := fmt.Sprintf("%s-%s", courier, id)
			redisClient.Set(key, p)
		}
	}

	for k, v := range cachedPackages {
		data.Data[k] = v
	}

	// Adding the cached packages to the list of packages to return
	c.JSON(200, data)
}
