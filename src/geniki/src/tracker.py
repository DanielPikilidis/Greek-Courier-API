import asyncio, logging, queue
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict
from dateutil import tz
from log_config import LogConfig
from logging.config import dictConfig
from requests import post, get, Timeout
from bs4 import BeautifulSoup as bs
from os import getenv
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException

@dataclass
class Location:
    datetime: datetime
    location: str
    description: str

@dataclass
class Package:
    found: bool = False
    courier_name: str = "geniki"
    courier_icon: str = "https://i.imgur.com/JGaa8zk.png"
    locations: List[Location] = field(default_factory=list)
    delivered: bool = False


class Tracker:
    def __init__(self):
        self.tracking_url = "https://www.taxydromiki.com/track/"
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.loop = asyncio.get_event_loop()
        self.proxy_queue = queue.Queue()
        dictConfig(LogConfig().dict())
        self.logger = logging.getLogger(getenv("LOG_NAME", "geniki-tracker"))

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
                response = get("http://proxy-manager-service:" + self.pm_port + "/request-proxy/geniki", timeout=2)
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

        try:
            proxy = self.proxy_queue.get(block=False)
        except queue.Empty:
            # If for any reason there are no proxies available (which I really doubt will ever happen), don't use one
            proxy = None
        finally:
            if proxy != None:
                self.proxy_queue.put(proxy)

        self.logger.debug(proxy)
        try:
            response = get(f"{self.tracking_url}{id}", proxies=proxy, timeout=3)
        except Timeout:
            self.logger.warning(f"Timeout while tracking {id}")
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the EasyMail website is down. If not, try again.")

        soup = bs(response.text, "html.parser")

        if soup.find("div", {"class": "empty-text"}):
            # Package not found
            return {id: package}

        package.found = True

        for status in soup.find_all("div", {"class": "tracking-checkpoint"}):
            description = status.find("div", {"class": "checkpoint-status"}).contents[1].text
            try:
                location = status.find("div", {"class": "checkpoint-location"}).contents[1].text
            except AttributeError:
                package.delivered = True
                location = ""

            date = status.find("div", {"class": "checkpoint-date"}).contents[1].text
            time = status.find("div", {"class": "checkpoint-time"}).contents[1].text

            package.locations.append(
                Location(
                    datetime = datetime.strptime(f"{date} {time}".split(", ")[1], "%d/%m/%Y %H:%M").astimezone(tz=tz.gettz("Europe/Athens")),
                    location = str(location),
                    description = str(description)
                )
            )

        self.logger.info(f"Tracked {id} successfully")

        return {id: package}
    
    async def track_one(self, id: str) -> Package:
        future = self.executor.submit(self.__track_one, id)
        return await self.loop.run_in_executor(None, future.result)
        
    async def track_many(self, ids: List[str]) -> Dict[str, Package]:
        ids = list(set(ids))

        if len(ids) > 1:
            ids = "-".join(ids)
        else:
            ids = ids[0]

        try:
            proxy = self.proxy_queue.get(block=False)
        except queue.Empty:
            # If for any reason there are no proxies available (which I really doubt will ever happen), don't use one
            proxy = None

        try:
            response = get(f"{self.tracking_url}{ids}", proxies=proxy, timeout=3)
        except Timeout:
            self.logger.warning(f"Timeout while tracking {ids}")
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the Geniki website is down. If not, try again.")
        finally:
            if proxy != None:
                self.proxy_queue.put(proxy)

        soup = bs(response.text, "html.parser")

        packages = dict()

        for package in soup.find_all("div", {"class": "tracking-result"}):
            tracking_id = package.find("strong").text
            
            if package.find("div", {"class": "empty-text"}):
                # Package not found
                packages[id] = Package()
                continue
        
            p = Package()
            p.found = True
            for status in package.find_all("div", {"class": "tracking-checkpoint"}):

                description = status.find("div", {"class": "checkpoint-status"}).contents[1].text
                try:
                    location = status.find("div", {"class": "checkpoint-location"}).contents[1].text
                except AttributeError:
                    p.delivered = True
                    location = ""

                date = status.find("div", {"class": "checkpoint-date"}).contents[1].text
                time = status.find("div", {"class": "checkpoint-time"}).contents[1].text

                p.locations.append(
                    Location(
                        datetime = datetime.strptime(f"{date} {time}".split(", ")[1], "%d/%m/%Y %H:%M").astimezone(tz=tz.gettz("Europe/Athens")),
                        location = str(location),
                        description = str(description)
                    )
                )
            packages[tracking_id] = p            

        self.logger.info(f"Tracked {ids} successfully")

        return packages
    