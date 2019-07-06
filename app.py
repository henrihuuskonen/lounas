from flask import Flask, Response
import config

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/_health")
def health():
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=config.PORT, debug=config.DEBUG_MODE)
