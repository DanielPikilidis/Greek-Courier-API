package main

import (
	"encoding/json"
	"os"

	"golang.org/x/exp/slices"
)

type Proxy struct {
	Type     string `json:"type"` // "http" or "socks5"
	Host     string `json:"host"`
	Username string `json:"username"`
	Password string `json:"password"`
}

type ProxyUsage struct {
	Proxy       Proxy
	Deployments []string
}

var proxyRegistry map[string]ProxyUsage

func openProxyList(path string) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()

	proxyList := make([]Proxy, 0)
	err = json.NewDecoder(file).Decode(&proxyList)
	if err != nil {
		return err
	}

	proxyRegistry = make(map[string]ProxyUsage)
	for _, proxy := range proxyList {
		proxyRegistry[proxy.Host] = ProxyUsage{
			Proxy:       proxy,
			Deployments: make([]string, 0),
		}
	}

	return nil
}

func selectProxy(deployment string) Proxy {
	bestAvailableProxyCount := -1
	bestAvailableProxy := Proxy{}
	leastDeployments := -1
	leastDeploymentsProxy := Proxy{}
	for _, proxyUsage := range proxyRegistry {
		if leastDeployments == -1 || len(proxyUsage.Deployments) < leastDeployments {
			// If we don't find a proxy that isn't used by this deployment, return the one with the least uses
			leastDeployments = len(proxyUsage.Deployments)
			leastDeploymentsProxy = proxyUsage.Proxy
		}
		if slices.Contains(proxyUsage.Deployments, deployment) {
			continue
		} else {
			// If there is more than one proxy that isn't used by this deployment, return the one with the least uses
			if bestAvailableProxyCount == -1 || len(proxyUsage.Deployments) < bestAvailableProxyCount {
				bestAvailableProxyCount = len(proxyUsage.Deployments)
				bestAvailableProxy = proxyUsage.Proxy
			}
		}
	}
	if bestAvailableProxyCount == -1 {
		// Didn't find a proxy that isn't used by this deployment, return the one with the least uses
		return leastDeploymentsProxy
	}

	// Found a proxy that isn't used by this deployment, return it
	return bestAvailableProxy
}

func useProxy(proxy Proxy, deployment string) {
	proxyUsage := proxyRegistry[proxy.Host]
	proxyUsage.Deployments = append(proxyUsage.Deployments, deployment)
	proxyRegistry[proxy.Host] = proxyUsage
}

func releaseProxy(proxy string, deployment string) {
	proxyUsage := proxyRegistry[proxy]
	for i, d := range proxyUsage.Deployments {
		if d == deployment {
			proxyUsage.Deployments = append(proxyUsage.Deployments[:i], proxyUsage.Deployments[i+1:]...)
			break
		}
	}
	proxyRegistry[proxy] = proxyUsage
}
