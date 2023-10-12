import asyncio, logging, queue
from dataclasses import dataclass, field
from typing import List
from dateutil import tz
from log_config import LogConfig
from logging.config import dictConfig
from requests import post, get, Timeout
from json import loads
from datetime import datetime
from fastapi import HTTPException
from os import getenv
from time import sleep
from concurrent.futures import ThreadPoolExecutor

@dataclass
class Location:
    datetime: datetime
    location: str
    description: str

@dataclass
class Package:
    found: bool = False
    courier_name: str = "ELTA"
    courier_icon: str = "https://i.imgur.com/6FU9iW7.png"
    locations: List[Location] = field(default_factory=list)
    delivered: bool = False


class Tracker:
    def __init__(self):
        self.tracking_url = "https://www.elta-courier.gr/track.php"
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_event_loop()
        self.proxy_queue = queue.Queue()
        dictConfig(LogConfig().dict())
        self.logger = logging.getLogger(getenv("LOG_NAME", "elta-tracker"))

    async def startup(self):
        use_proxy = getenv("USE_PROXY", "false").lower() == "true"
        if use_proxy:
            for _ in range(5):
                self.proxy_queue.put(self.__request_proxy())

    async def shutdown(self):
        self.__release_proxy()

    def __request_proxy(self):
        self.pm_port = getenv("PM_PORT", 80)
        while True:
            try:
                self.logger.info("Waiting for proxy...")
                response = get("http://proxy-manager-service:" + str(self.pm_port) + "/request-proxy/elta", timeout=2)
                break
            except:
                sleep(5)
                continue

        if response.status_code != 200:
            self.logger.warning("Failed to get proxy")
            self.proxies = None
            return

        proxy = response.json()
        self.logger.info("Got proxy: " + proxy["host"])
        self.proxy_host = proxy["host"]
        return {
            "http": f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}",
            "https": f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}",
        }

    def __release_proxy(self):
        while not self.proxy_queue.empty():
            proxy = self.proxy_queue.get()
            host = proxy["http"].split("@")[-1]
            self.logger.info("Releasing proxy: " + host)
            post("http://proxy-manager-service:" + str(self.pm_port) + "/release-proxy/elta", data={"host": host})

    def __track_one(self, id: str) -> Package:
        package = Package()

        data = {"number": id}

        try:
            proxy = self.proxy_queue.get(block=False)
        except queue.Empty:
            # If for any reason there are no proxies available (which I really doubt will ever happen), don't use one
            proxy = None

        self.logger.debug(proxy)
        try:
            response = post(self.tracking_url, data=data, proxies=proxy, timeout=3)
        except Timeout: 
            self.logger.warning(f"Timeout while tracking {id}")
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the ELTA website is down. If not, try again.")
        finally:
            if proxy != None:
                self.proxy_queue.put(proxy)

        if response.status_code >= 400:
            self.logger.warning(f"Error while retrieving info for {id}: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error while retrieving package info")

        response_json = loads(response.content)

        try:
            data = response_json["result"][id]
        except KeyError:
            self.logger.warning(f"Error while retrieving info for {id}")
            self.logger.debug(response_json['result'])
            raise HTTPException(status_code=500, detail="Failed to parse response.")

        if data["status"] == 0:
            return {id: package}
        
        package.found = True

        for status in data["result"]:
            date_str = status["date"] + " " + status["time"]
            try:
                dt = datetime.strptime(date_str, "%d-%m-%Y %H:%M").astimezone(tz=tz.gettz("Europe/Athens"))
            except ValueError:
                # Sometimes the minutes part is missing...
                dt = datetime.strptime(date_str, "%d-%m-%Y %H:").astimezone(tz=tz.gettz("Europe/Athens"))
            package.locations.append(
                Location(
                    datetime = dt,
                    location = status["place"],
                    description = status["status"]
                )
            )

        package.delivered = package.locations[-1].description == "Αποστολή παραδόθηκε"

        self.logger.info(f"Tracked {id} successfully")

        return {id: package}

    async def track_one(self, id: str) -> Package:
        future = self.executor.submit(self.__track_one, id)
        return await self.loop.run_in_executor(None, future.result)

    async def track_many(self, ids: List[str]):
        ids = list(set(ids))

        if len(ids) > 1:
            ids = "\n".join(ids)
        else:
            ids = ids[0]

        data = {"number": ids}
        
        try:
            proxy = self.proxy_queue.get(block=False)
        except queue.Empty:
            proxy = None

        try:
            response = post(self.tracking_url, data=data, proxies=proxy, timeout=3)
        except Timeout: 
            self.logger.warning(f"Timeout while tracking {id}")
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the ELTA website is down. If not, try again.")
        finally:
            if proxy != None:
                self.proxy_queue.put(proxy)

        if response.status_code >= 400:
            self.logger.warning(f"Error while retrieving info for {id}: {response.status_code}")
            self.logger.debug(response.content)
            raise HTTPException(status_code=response.status_code, detail="Error while retrieving package info")

        response_json = loads(response.content)

        try:
            data = response_json["result"]
        except KeyError:
            self.logger.warning(f"Error while retrieving info for {id}")
            self.logger.debug(response_json['result'])
            raise HTTPException(status_code=500, detail="Failed to parse response.")

        packages = dict()

        for id, package in data.items():
            if package["status"] == 0:
                packages[id] = Package()
                continue
            
            locations = []
            for status in package["result"]:
                date_str = status["date"] + " " + status["time"]
                locations.append(
                    Location(
                        datetime = datetime.strptime(date_str, "%d-%m-%Y %H:%M").astimezone(tz=tz.gettz("Europe/Athens")),
                        location = status["place"],
                        description = status["status"]
                    )
                )

            p = Package()
            p.found = True
            p.locations = locations
            p.delivered = locations[-1].description == "Αποστολή παραδόθηκε"
            packages[id] = p
        
        self.logger.info(f"Tracked {ids} successfully")

        return packages
    
