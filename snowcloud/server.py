import os
import sys
import threading

from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin

from snowcloud.client import Snowcloud


app = Flask(__name__)
CORS(app)

cloud = Snowcloud(os.getenv("SNOWCLOUD_URL"))
cloud.register()

renew_thread = threading.Thread(target=cloud.keep_renewed)
renew_thread.start()

@app.route("/", methods=["GET", "POST"])
@cross_origin()
def index():
    if request.method == "GET":
        return redirect("https://breq.dev/apps/snowflake")

    else:
        snowflake = cloud.generate()
        return jsonify({"snowflake": snowflake,
                        "snowflake_str": str(snowflake)})


if __name__ == "__main__":
    app.run("0.0.0.0", port=int(sys.argv[1]) if len(sys.argv) > 1 else 4000)
