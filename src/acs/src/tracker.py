import asyncio, datetime, logging
from dataclasses import dataclass, field
from playwright.async_api import async_playwright
from playwright._impl._api_types import TimeoutError as playwrightTimeoutError
from typing import List
from dateutil import parser, tz
from log_config import LogConfig
from logging.config import dictConfig
from fastapi import HTTPException
from requests import get, post
from os import getenv
from time import sleep

@dataclass
class Location:
    datetime: datetime.datetime
    location: str
    description: str

@dataclass
class Package:
    found: bool = False
    courier_name: str = "ACS"
    courier_icon: str = "https://i.imgur.com/Yk1WIrQ.jpg"
    locations: List[Location] = field(default_factory=list)
    delivered: bool = False

class Tracker:
    def __init__(self, max_pages=5):
        self.tracking_url = "https://www.acscourier.net/"
        self.max_pages = max_pages
        dictConfig(LogConfig().dict())
        self.logger = logging.getLogger(getenv("LOG_NAME", "acs-tracker"))

    async def startup(self):
        use_proxy = getenv("USE_PROXY", "false").lower() == "true"
        if use_proxy:
            self.__request_proxy()
        else:
            self.proxy = None
        await self.__init_browser()
    
    async def shutdown(self):
        await self.__close_browser()
        if self.proxy:
            self.__release_proxy()

    async def __init_browser(self):
        self.logger.debug(f"Initializing browser with {self.max_pages} tabs")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            proxy = self.proxy,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-extensions",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--single-process",
                "--no-zygote",
                "--no-first-run",
                "--hide-scrollbars",
                "--disable-notifications",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-component-extensions-with-background-pages",
                "--disable-ipc-flooding-protection",
                "--disable-renderer-backgrounding",
            ]
        )

        self.browser_context = await self.browser.new_context()

        self.page_queue = asyncio.Queue()

        for _ in range(self.max_pages):
            page = await self.browser_context.new_page()
            await page.goto(self.tracking_url, wait_until="domcontentloaded")
            await self.__clear_popups(page)
            await self.page_queue.put(page)

        asyncio.create_task(self.__check_pages())
        asyncio.create_task(self.__restart_pages())

        self.logger.info("Browser initialized successfully")

    async def __close_browser(self):
        self.logger.debug("Closing browser")
        await self.browser.close()
        await self.playwright.stop()
        self.logger.info("Browser closed successfully")
    
    def __request_proxy(self):
        self.pm_port = getenv("PM_PORT", 80)
        while True:
            try:
                self.logger.info("Waiting for proxy...")
                response = get("http://proxy-manager-service:" + self.pm_port + "/request-proxy/acs")
                break
            except:
                sleep(5)
                continue

        if response.status_code != 200:
            self.logger.warning("Failed to get proxy")
            self.proxy = None
            return

        proxy = response.json()
        self.logger.info("Got proxy: " + proxy["host"])
        self.proxy_host = proxy["host"]
        self.proxy = {
            "server": proxy["host"],
            "username": proxy["username"],
            "password": proxy["password"],
        }

    def __release_proxy(self):
        self.logger.info("Releasing proxy: " + self.proxy_host)
        post("http://proxy-manager-service:" + self.pm_port + "/release-proxy/acs", data={"host": self.proxy_host})

    async def __clear_popups(self, page):
        try:
            await page.click("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=500)
        except:
            pass
        
        try:
            await page.click("#close_banner > i:nth-child(1)", timeout=500)
        except:
            pass

        try:
            await page.click("#close_banner_secondary > i:nth-child(1)", timeout=500)
        except:
            pass

    async def __check_pages(self):
        await asyncio.sleep(10)
        while True:
            page = await self.page_queue.get()
            await page.click(".mat-form-field-flex")
            await page.keyboard.type("123123123")
            try:
                async with page.expect_response(lambda response: response.url == f"https://api.acscourier.net/api/parcels/search/123123123" and response.status == 200, timeout=10000) as res:
                    await page.click(".d-sm-inline-block")
                await page.click(".btn-clear")
                await self.page_queue.put(page)
            except:
                await page.close()
                page = await self.browser_context.new_page()
                await page.goto(self.tracking_url, wait_until="domcontentloaded")
                await self.__clear_popups(page)
                await self.page_queue.put(page)
            
            await asyncio.sleep(15)


    async def __restart_pages(self):
        await asyncio.sleep(10)
        while True:
            page = await self.page_queue.get()
            await page.reload()
            await self.__clear_popups(page)
            await asyncio.sleep(5)  # Making sure the page is ready before putting it back in the queue
            await self.page_queue.put(page)
            await asyncio.sleep(180 / self.max_pages)

    async def track_one(self, id):
        package = Package()
        page = await self.page_queue.get()

        await page.bring_to_front()
        await page.click(".mat-form-field-flex")
        await page.keyboard.type(id)

        try:
            # I have to check if response.status is 200 because there's also a OPTIONS response that gets returned from the server and has the same url but 204 code...
            async with page.expect_response(lambda response: response.url == f"https://api.acscourier.net/api/parcels/search/{id}" and response.status == 200, timeout=10000) as res:
                await page.click(".d-sm-inline-block")
        except playwrightTimeoutError:
            self.logger.warning(f"Timeout while tracking {id}")
            await page.click(".btn-clear")
            await self.page_queue.put(page)
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the ACS website is down. If not, try again.")

        await page.click(".btn-clear")

        response = await res.value
        
        self.logger.debug(await response.json())

        await self.page_queue.put(page)

        if not response.ok:
            raise HTTPException(status_code=500, detail="Failed to retrieve tracking info.")

        try:
            response = (await response.json())["items"][0]
        except:
            raise HTTPException(status_code=500, detail="Failed to parse response.")

        if response["notes"] == "Η αποστολή δεν βρέθηκε":
            return {id: package}

        package.found = True

        for status in response["statusHistory"]:
            if "controlPointDate" not in status:
                continue
            
            try:
                package.locations.append(
                    Location(
                        datetime = parser.isoparse(status["controlPointDate"]).astimezone(tz=tz.gettz("Europe/Athens")),
                        location = status["controlPoint"],
                        description = status["description"],
                    )
                )
            except KeyError:
                package.locations.append(
                    Location(
                        datetime = datetime.datetime.now(),
                        location = status["controlPoint"],
                        description = status["description"],
                    )
                )

        package.delivered = response["isDelivered"]

        self.logger.info(f"Tracked {id} successfully")

        return {id: package}

    async def track_many(self, ids):
        ids = list(set(ids))

        page = await self.page_queue.get()

        await page.click(".mat-form-field-flex")
        await page.keyboard.type(" ".join(ids))

        if len(ids) > 1:
            ids = "%2C".join(ids)
        else:
            ids = ids[0]

        try:
            async with page.expect_response(lambda response: response.url == f"https://api.acscourier.net/api/parcels/search/{ids}" and response.status == 200, timeout=10000) as res:
                await page.click(".d-sm-inline-block")
        except playwrightTimeoutError:
            self.logger.warning(f"Timeout while tracking {ids}")
            await page.click(".btn-clear")
            await self.page_queue.put(page)
            raise HTTPException(status_code=503, detail="Timeout while retrieving tracking info. This might mean that the ACS website is down. If not, try again.")

        await page.click(".btn-clear")

        response = await res.value

        if not response.ok:
            raise HTTPException(status_code=404, detail="Package not found")

        self.logger.debug(await response.json())

        await self.page_queue.put(page)
        
        packages = dict()

        try:
            items = (await response.json())["items"]
        except:
            raise HTTPException(status_code=404, detail="Failed to parse response")

        for package in items:
            if package["notes"] == "Η αποστολή δεν βρέθηκε":
                packages[package["trackingNumber"]] = Package()
                continue

            locations = []
            for status in package["statusHistory"]:
                if "controlPointDate" not in status:
                    continue
                                
                try:
                    package.locations.append(
                        Location(
                            datetime = parser.isoparse(status["controlPointDate"]).astimezone(tz=tz.gettz("Europe/Athens")),
                            location = status["controlPoint"],
                            description = status["description"],
                        )
                    )
                except KeyError:
                    package.locations.append(
                        Location(
                            datetime = datetime.datetime.now(),
                            location = status["controlPoint"],
                            description = status["description"],
                        )
                    )

            p = Package()
            p.found = True
            p.locations = locations
            p.delivered = package["isDelivered"]
            packages[package["trackingNumber"]] = p

        self.logger.info(f"Tracked {ids} successfully")

        return packages
    