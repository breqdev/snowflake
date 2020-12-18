import os
import sys
import time
import threading

from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin

import snowcloud


app = Flask(__name__)
CORS(app)

cloud = snowcloud.SnowCloud(os.getenv("SNOWCLOUD_URL"))
cloud.register()

renew_thread = threading.Thread(target=cloud.keep_renewed)
renew_thread.start()

EPOCH = 1577836800  # Jan 1, 2020
worker_increment = 0


def make_snowflake(worker_id):
    timestamp = int((time.time() - EPOCH) * 1000)
    global worker_increment

    snowflake = timestamp << 22
    snowflake |= worker_id << 12
    snowflake |= worker_increment

    worker_increment = (worker_increment + 1) & 0xFFF

    return snowflake


@app.route("/", methods=["GET", "POST"])
@cross_origin()
def index():
    if request.method == "GET":
        return redirect("https://breq.dev/showcase/snowflake")

    else:
        snowflake = make_snowflake(cloud.worker_id)
        return jsonify({"snowflake": snowflake,
                        "snowflake_str": str(snowflake)})


if __name__ == "__main__":
    app.run("0.0.0.0", port=int(sys.argv[1]) if len(sys.argv) > 1 else 4000)
