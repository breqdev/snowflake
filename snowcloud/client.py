import os
import uuid
import time
import logging
import threading

import requests


class SnowcloudRenewThread(threading.Thread):
    def __init__(self, snowcloud):
        super().__init__()
        self.cloud = snowcloud
        self.stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            self.stop_event.wait(self.cloud.ttl/2)
            if self.stopped():
                continue
            self.cloud.renew()

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.isSet()


class Snowcloud:
    EPOCH = 1577836800  # Jan 1, 2020

    def __init__(self, cloud, key=None):
        self.logger = logging.getLogger("snowcloud.SnowCloud")

        self.cloud = cloud

        if not key:
            key = os.getenv("SNOWCLOUD_KEY")

        self.key = key
        self.user = str(uuid.uuid4())

        self.increment = 0
        self.thread = None

    def register(self):
        self.logger.info("Registering for worker ID")
        result = requests.post(
            f"{self.cloud}", params={"key": self.key, "user": self.user})

        result.raise_for_status()
        result = result.json()

        self.worker_id = result["worker_id"]
        self.expires = result["expires"]
        self.ttl = result["ttl"]
        self.logger.info(
            f"Registered as {self.worker_id} "
            f"for {self.ttl} until {self.expires}")

    def renew(self):
        self.logger.info(f"Renewing registration as {self.worker_id}")
        result = requests.post(
            f"{self.cloud}",
            params={
                "key": self.key,
                "user": self.user,
                "renew": self.worker_id
            }
        )

        result.raise_for_status()
        result = result.json()

        assert result["worker_id"] == self.worker_id
        self.expires = result["expires"]
        self.ttl = result["ttl"]

        self.logger.info(
            f"Renewed as {self.worker_id} "
            f"for {self.ttl} until {self.expires}")

    def start_autorenew(self):
        self.thread = SnowcloudRenewThread(self)
        self.thread.start()

    def end_autorenew(self):
        self.thread.stop()

    def generate(self):
        timestamp = int((time.time() - self.EPOCH) * 1000)

        snowflake = timestamp << 22
        snowflake |= self.worker_id << 12
        snowflake |= self.increment

        self.increment = (self.increment + 1) & 0xFFF

        return snowflake


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    s = Snowcloud(os.getenv("SNOWCLOUD_URL"))
    s.register()

    s.keep_renewed()
