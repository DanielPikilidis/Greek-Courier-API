import asyncio, logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict
from log_config import LogConfig
from logging.config import dictConfig
from requests import get, post, Timeout
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
    courier_name: str = "CourierCenter"
    courier_icon: str = "https://i.imgur.com/w51MEA1.png"
    locations: List[Location] = field(default_factory=list)
    delivered: bool = False

class Tracker:
    def __init__(self):
        self.tracking_url = "https://courier.gr/track/result?tracknr="
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.loop = asyncio.get_event_loop()
        dictConfig(LogConfig().model_dump())
        self.logger = logging.getLogger(getenv("LOG_NAME", "couriercenter-tracker"))

    async def startup(self):
        use_proxy = getenv("USE_PROXY", "false").lower() == "true"
        if use_proxy:
            self.__request_proxy()
        else:
            self.proxies = None

    async def shutdown(self):
        if self.proxies:
            self.__release_proxy()

    def __request_proxy(self):
        self.pm_port = getenv("PM_PORT", 80)
        while True:
            try:
                self.logger.info("Waiting for proxy...")
                response = get("http://proxy-manager-service:" + self.pm_port + "/request-proxy/couriercenter")
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
        self.proxies = {
            "http": f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}",
            "https": f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}",
        }

    def __release_proxy(self):
        self.logger.info("Releasing proxy: " + self.proxy_host)
        post("http://proxy-manager-service:" + self.pm_port + "/release-proxy/couriercenter", data={"host": self.proxy_host})

    def __track_one(self, id: str) -> Package:
        package = Package()

        self.logger.debug(self.proxies)
        try:
            response = get(f"{self.tracking_url}{id}", proxies=self.proxies, timeout=3)
        except Timeout:
            self.logger.warning(f"Timeout while tracking {id}")
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the CourierCenter website is down. If not, try again.")

        soup = bs(response.text, "html.parser")

        if soup.find("h4", {"class": "error"}):
            return {id: package}
        
        package.found = True

        for status in soup.find_all("div", {"class": "tr"})[1:]:
            dt = status.find("div", {"id": "date"}).contents[0] + " " + status.find("div", {"id": "time"}).contents[0]
            package.locations.append(
                Location(
                    datetime = datetime.strptime(dt, "%d/%m/%Y %H:%M"),
                    location = str(status.find("div", {"id": "area"}).contents[0]),
                    description = str(status.find("div", {"id", "action"}).contents[0])
                )
            )

        package.delivered = soup.find("div", {"class": "status"}).contents[3].contents[0] == "(29) DeliveryCompleted"

        self.logger.info(f"Tracked {id} successfully")

        return {id: package}

    async def track_one(self, id: str) -> Package:
        future = self.executor.submit(self.__track_one, id)
        return await self.loop.run_in_executor(None, future.result)

    async def track_many(self, ids: List[str]) -> Dict[str, Package]:
        ids = list(set(ids))

        # There's no way get multiple packages with one request, so I have to make a request for each id.
        tasks = [asyncio.create_task(self.track_one(id)) for id in ids]
        results = await asyncio.gather(*tasks)
        packages = dict()
        for r in results:
            key, value = list(r.items())[0]
            packages[key] = value

        return packages