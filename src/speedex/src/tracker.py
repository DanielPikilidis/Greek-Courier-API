import asyncio, logging
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
    courier_name: str = "Speedex"
    courier_icon: str = "https://i.imgur.com/Rt380x2.png"
    locations: List[Location] = field(default_factory=list)
    delivered: bool = False


class Tracker:
    def __init__(self):
        self.tracking_url = "http://www.speedex.gr/speedex/NewTrackAndTrace.aspx?number="
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.loop = asyncio.get_event_loop()
        dictConfig(LogConfig().dict())
        self.logger = logging.getLogger(getenv("LOG_NAME", "speedex-tracker"))

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
                response = get("http://proxy-manager-service:" + self.pm_port + "/request-proxy/speedex", timeout=2)
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
        post("http://proxy-manager-service:" + self.pm_port + "/release-proxy/speedex", data={"host": self.proxy_host})

    def __track_one(self, id: str) -> Package:
        package = Package()

        self.logger.debug(self.proxies)
        try:
            response = get(f"{self.tracking_url}{id}", proxies=self.proxies, timeout=3)
        except Timeout:
            self.logger.warning(f"Timeout while tracking {id}")
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the EasyMail website is down. If not, try again.")

        soup = bs(response.text, "html.parser")

        if soup.find("div", {"class": "alert-warning"}):
            # Package not found
            return {id: package}

        package.found = True

        for status in soup.find_all("div", {"class": "timeline-card"}):
            items = status.find("span", {"class": "font-small-3"}).contents[0].split(", ")
            location = items[0]
            date = items[1]
            description = status.find("h4", {"class": "card-title"}).contents[0].text

            package.locations.append(
                Location(
                    datetime = datetime.strptime(date, "%d/%m/%Y στις %H:%M").astimezone(tz=tz.gettz("Europe/Athens")),
                    location = str(location),
                    description = str(description)
                )
            )

        self.logger.info(f"Tracked {id} successfully")

        package.delivered = package.locations[-1].description == "Η ΑΠΟΣΤΟΛΗ ΠΑΡΑΔΟΘΗΚΕ"

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
    