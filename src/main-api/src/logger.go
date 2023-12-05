package main

import (
	"io"
	"os"
	"strings"

	"github.com/sirupsen/logrus"
)

var LogLevels map[string]logrus.Level = map[string]logrus.Level{
	"debug":   logrus.DebugLevel,
	"info":    logrus.InfoLevel,
	"warning": logrus.WarnLevel,
	"error":   logrus.ErrorLevel,
}

func NewLogger() (*logrus.Logger, error) {
	logLevel := getEnvCustom("LOG_LEVEL", "info")

	logger := logrus.New()

	logWriter := io.Writer(os.Stdout)
	logger.SetOutput(logWriter)

	logger.SetLevel(LogLevels[strings.ToLower(logLevel)])

	return logger, nil
}
