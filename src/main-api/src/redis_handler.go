package main

import (
	"context"
	"fmt"
	"strconv"
	"time"

	jsoniter "github.com/json-iterator/go"
	"github.com/redis/go-redis/v9"
)

type redisHandler struct {
	enabled       bool
	client        *redis.Client
	cacheDuration time.Duration
}

func NewRedisHandler() (*redisHandler, error) {
	enabled := getEnvCustom("REDIS_ENABLED", "true")
	address := getEnvCustom("REDIS_ADDRESS", "localhost")
	port := getEnvCustom("REDIS_PORT", "6379")
	password := getEnvCustom("REDIS_PASSWORD", "")
	cacheDuration := getEnvCustom("REDIS_CACHE_DURATION", "5")

	enabledBool, err := strconv.ParseBool(enabled)
	if err != nil {
		return nil, err
	}

	if !enabledBool {
		return &redisHandler{
			enabled: false,
		}, nil
	}

	cacheDurationInt, err := strconv.Atoi(cacheDuration)
	if err != nil {
		return nil, err
	}

	return &redisHandler{
		enabled: enabledBool,
		client: redis.NewClient(&redis.Options{
			Addr:     fmt.Sprintf("%s:%s", address, port),
			Password: password,
		}),
		cacheDuration: time.Duration(cacheDurationInt) * time.Minute,
	}, nil
}

func (h *redisHandler) Get(key string) (Package, error) {
	var p Package

	if !h.enabled {
		return p, fmt.Errorf("not found")
	}

	ctx := context.Background()
	value, err := h.client.Get(ctx, key).Result()
	if err == redis.Nil {
		logger.Debug("Did not find ", key, " in cache")
		return p, fmt.Errorf("not found")
	} else if err != nil {
		logger.Error("Error while getting ", key, " from cache: ", err)
		return p, err
	}

	err = jsoniter.UnmarshalFromString(value, &p)
	if err != nil {
		logger.Debug("Error while unmarshalling ", key, " from cache: ", err)
		return p, err
	}
	logger.Debug("Found ", key, " in cache")
	return p, nil
}

func (h *redisHandler) Set(key string, p Package) error {
	if !h.enabled {
		return nil
	}

	value, err := jsoniter.MarshalToString(p)
	if err != nil {
		logger.Error("Error while marshalling ", key, " to cache: ", err)
		return err
	}

	ctx := context.Background()
	err = h.client.Set(ctx, key, value, h.cacheDuration).Err()
	if err != nil {
		logger.Error("Error while setting ", key, " in cache: ", err)
		return err
	}
	logger.Debug("Added ", key, " to cache with value: ", value)
	return nil
}

func (h *redisHandler) Close() error {
	if h.enabled {
		return h.client.Close()
	}
	return nil
}
