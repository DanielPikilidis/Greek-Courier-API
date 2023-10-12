## Introduction

This is an over-complicated API for Greek couriers. It is built with Kubernetes
and is scalable. Each courier is it's own application that can be scaled
based on load.
<br>
Currently the following couriers are supported:
- ACS
- CourierCenter
- EasyMail
- ELTA Courier
- Skroutz Last Mile
- Speedex Courier
- Geniki Taxydromiki

## Overview
The application can be broken in to the following parts:
- The trackers:
Each courier has it's own tracker. Each tracker exposes two HTTP endpoints which are used
by the main API. It doesn't matter what language is being used or what is going on exactly is each courier, the only
requirements are these 2 endpoints.

- The main-api:
This is responsible for getting the request from the user and forwarding it to the correct tracker. If Redis
caching is enabled it will also check in there first.

- The proxy-manager:
This is a program that gives proxies to the trackers. You might ask, why do we need this... And the answer is
we don't. At least for normal usage. From testing I found out that only ELTA courier will ban my IP after
a certain number of requests in a second (I don't know the exact number but it's probably around 3-4 requests
per second). Each tracker on startup will request a proxy (or more than one proxies) from the proxy manager and
it will use that for all of its requests to the courier.

From some testing this can handle over 100 requests / second (mixed traffic for all couriers with no cached IDs). Currently the rate limit is set to 1 request / second.

## Usage
To track one package use this:
`https://courier-api.danielpikilidis.com/track-one/[courier]/[id]`

And to track many package at the same time use this:
`https://courier-api.danielpikilidis.com/track-many/[courier]/[id1]&[id2]&[id3]&...`

The courier options are acs, couriercenter, easymail, elta, skroutz, speedex, and geniki.

## Installation
These instructions will also show how to install microk8s. If you already have Kubernetes environment then
you can skip to step 4.

1) Install microk8s.<br>
```
sudo snap install microk8s --classic
```
You will obviously need snap for this.

2) Configure MetalLB
```
sudo microk8s enable metallb
```
And enter the IP range you want. For example 10.10.0.0/16 (2^16 IPs)

3) (Optional) If you need vertical pod autoscaling you will also have to set that up.
4) Clone the repository
```
git clone https://github.com/DanielPikilidis/Greek-Courier-API
cd Greek-Courier-API
```
6) Configure everything (scroll down for details)
7) If you did everything correct then the following command should have everything up and running:

```
microk8s helm3 install helm/ courier-api -n courier-api --create-namespace
```
Note: the `--create-namespace` is only required the first time and should be removed if the namespace already exists.

## Configuration

All configuration is made in the values.yaml files.

- helm/values.yaml:
  - `global.node_port`: This is the port that will be opened on the host (or hosts) and will be used to access
  the API.
  - `global.api_port`, `global.tracker_port` and `global.pm_port`: These are internal ports that don't really affect the application.
  - `global.redis.enabled`: Enables / Disables the Redis database
  - `global.redis.address`, `global.redis.port` and `global.redis.password`: <u>DO NOT</u> change them. I'm planning to make the Redis
  database more configurable later, but if you change them now things will break.
  - `global.redis.cache_duration`: For how many minutes should the IDs be cached.
- helm/proxy-manager/values.yaml:
  - `pm.enabled`: Enables / Disables the proxy manager. By default this is false and the trackers won't use proxies.
  - `pm.base64_proxies`: With this you pass the a JSON proxy list encoded in base64. The JSON should have the
  following format:
  ```json
  [
    {
      "type": "http",
      "host": "0.0.0.0:10000",
      "username": "test",
      "password": "test",
    },
    ...
  ]
  ```
  type can be http or socks5, depening on the proxy.<br>
  Then you can encode the json with
  ```
  cat proxy_file.json | base64 -w 0
  ```
  And paste the result as a value for base64_proxies.
- helm/[tracker]/values.yaml (same for main-api as well):
  - `[tracker].enabled`: enable or disable the tracker
  - `[tracker].use_proxy`: should the tracker request and use a proxy. If you enable this make sure that the proxy manager is enabled as well (in helm/proxy-manager/values.yaml). If you enable this and the proxy-manage is disabled the the tracker
  will not be able to start!
  - `[tracker].name`: Not important
  - `[tracker].image`: From where to pull the image.
  - `[tracker].logpath`: Where the logs will be stored in the container
  - `[tracker].logname`: The name of the log file.
  - `[tracker].loglevel`: Logging level. DEBUG, INFO, WARNING or ERROR
  - `autoscaling.horizontal.min_replicas`: The minimum number of active trackers for that courier
  - `autoscaling.horizontal.max_replicas`: The maximum number of active trackers for that courier
  - `autoscaling.vertical.enabled`: enable or disable vertical pod autoscaling. By default it's disabled
  - `autoscaling.vertical.mode`: What should the vpa do. Auto, Off, Initial or Recreate
  <br>


## How is this hosted
Right now this is hosted on a high availability microk8s cluster with 3 nodes. Total 16 cores and 48GB RAM. I'm not renting
this, but using my own server that has a lot of unused resources. Obviously the resource usage is much lower than
what I have allocated, this cluster is also used for other purposes. Currently it's using about 800mb of RAM
with the default 2 pods per tracker. An external caddy reverse proxy is used to load balance the requests
between these 3 nodes. For security purposes I also have a VPS (from pointer) that filters the traffic
before forwarding to the actual server. So if for any reason the VPS stops working, the API will not
be accessible. Because this is hosted on my own home server, in case of an internet outage nothing will work.
And in case of a power outage it can continue running for about 20 minutes before shutting down.

TLDR: It's self-hosted and will not have 100% up-time, so don't start opening issues when it's not working.

## TODO
There are a few changes that I want to make whenever I have time:<br>
- Make this deployable on a cloud provider like AWS. I haven't tested it but I don't expect this to
work with a cloud provider. Will probably need an ingress controller instead of node port.
- Find a better way to pass a proxy list to the proxy manager.
- Improve the Redis deployment configuration.
- Setup a high availability Redis deployment.
- Setup fluentbit
- Setup prometheus and collect stats.
- Change the domain name. Not really a fan of using a personal domain name for this.
- Add swagger UI.


## Contributing
I'm open to any improvement / new features.
