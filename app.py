from flask import Flask, Response, render_template
import config

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/_health")
def health():
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=config.PORT, debug=config.DEBUG_MODE)
