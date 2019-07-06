from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, render_template

import config

app = Flask(__name__)

DATE_MAP = {0: "maanantai", 1: "tiistai", 2: "keskiviikko", 3: "torstai", 4: "perjantai", 5: "lauantai", 6: "sunnuntai"}


def crawl_garam_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    wrapper = soup.find_all(class_="text-content")[2]
    if not wrapper or not wrapper.p or "VIIKKO" not in wrapper.p.text:
        return None

    today = DATE_MAP[date.weekday(date.today())].upper()
    tomorrow = DATE_MAP[date.weekday(date.today() + timedelta(1))].upper()

    all_p = wrapper.find_all("p")
    today_index = next(iter([i for i, s in enumerate(all_p) if today in s.text]), None)
    tomorrow_index = next(iter([i for i, s in enumerate(all_p) if tomorrow in s.text]), None)

    if today_index and tomorrow_index:
        return [p.text for p in all_p[today_index + 1 : tomorrow_index]]

    return None


def crawl_oikeus():
    return crawl_garam_page("https://www.cafeteria.fi/ravintola-oikeus/")


def crawl_silta():
    return crawl_garam_page("https://www.cafeteria.fi/silta-itamerentalo/")


@app.route("/")
def index():
    return render_template("index.html", silta=crawl_silta(), oikeus=crawl_oikeus())


@app.route("/_health")
def health():
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=config.PORT, debug=config.DEBUG_MODE)
