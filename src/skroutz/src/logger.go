package main

import (
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/sirupsen/logrus"
	"gopkg.in/natefinch/lumberjack.v2"
)

var LogLevels map[string]logrus.Level = map[string]logrus.Level{
	"debug":   logrus.DebugLevel,
	"info":    logrus.InfoLevel,
	"warning": logrus.WarnLevel,
	"error":   logrus.ErrorLevel,
}

func NewLogger() (*logrus.Logger, error) {
	logPath := getEnvCustom("LOG_PATH", "/tmp")
	logFileName := getEnvCustom("LOG_NAME", "skroutz-tracker.log")
	logLevel := getEnvCustom("LOG_LEVEL", "info")

	logger := logrus.New()

	logFilePath := filepath.Join(logPath, logFileName)
	logFile := &lumberjack.Logger{
		Filename:  logFilePath,
		MaxSize:   100,
		MaxAge:    14,
		Compress:  true,
		LocalTime: true,
	}

	logWriter := io.MultiWriter(os.Stdout, logFile)
	logger.SetOutput(logWriter)

	logger.SetLevel(LogLevels[strings.ToLower(logLevel)])

	return logger, nil
}
