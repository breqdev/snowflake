import os
import uuid
import time
import logging

import requests


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

    def check_renew(self):
        if (time.time() + self.ttl/2) > self.expires:
            self.renew()

    def keep_renewed(self):
        while True:
            self.renew()
            time.sleep(self.ttl/2)

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
