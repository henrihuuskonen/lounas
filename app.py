from flask import Flask, Response
import config

app = Flask(__name__)


@app.route("/")
def hello():
    return Response("Hello World!", status=200)


@app.route("/_health")
def health():
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=config.PORT, debug=config.DEBUG_MODE)
