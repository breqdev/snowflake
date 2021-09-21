import os
import sys

from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin

from snowcloud.flask_ext import SnowcloudFlask


app = Flask(__name__)

app.config["SNOWCLOUD_KEY"] = os.environ["SNOWCLOUD_KEY"]
app.config["SNOWCLOUD_URL"] = os.environ["SNOWCLOUD_URL"]

CORS(app)
cloud = SnowcloudFlask(app)

@app.route("/", methods=["GET", "POST"])
@cross_origin()
def index():
    if request.method == "GET":
        return redirect("https://breq.dev/apps/snowflake.html")

    else:
        snowflake = cloud.generate()
        return jsonify({"snowflake": snowflake,
                        "snowflake_str": str(snowflake)})


if __name__ == "__main__":
    app.run("0.0.0.0", port=int(sys.argv[1]) if len(sys.argv) > 1 else 4000)
