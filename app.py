import re
import traceback
from datetime import date, timedelta
from collections import OrderedDict
from json import JSONDecodeError

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

DATE_MAP = {0: "maanantai", 1: "tiistai", 2: "keskiviikko", 3: "torstai", 4: "perjantai", 5: "lauantai", 6: "sunnuntai"}


def get_min():
    try:
        t = date.today()
        month = t.month if t.month > 10 else ("0" + str(t.month))
        day = t.day if t.day > 10 else ("0" + str(t.day))
        base_url = "https://www.sodexo.fi/ruokalistat/output/daily_json/70"
        r = requests.get(f"{base_url}/{t.year}-{month}-{day}")
        data = r.json()
        lst = []
        for _, number in data["courses"].items():
            lst.append("{} ({})".format(number["title_fi"], number["properties"]))
        return lst
    except Exception:
        return None


def get_hiili():
    try:
        t = date.today()
        month = t.month if t.month > 10 else ("0" + str(t.month))
        day = t.day if t.day > 10 else ("0" + str(t.day))
        base_url = "https://www.sodexo.fi/ruokalistat/output/daily_json/7498"
        r = requests.get(f"{base_url}/{t.year}-{month}-{day}")
        data = r.json()
        lst = []
        for _, number in data["courses"].items():
            lst.append("{} ({})".format(number["title_fi"], number["properties"]))
        return lst
    except Exception:
        return None


def crawl_factory():
    try:
        r = requests.get("https://ravintolafactory.com/lounasravintolat/ravintolat/helsinki-salmisaari/")

        soup = BeautifulSoup(r.text, "html.parser")

        today = DATE_MAP[date.weekday(date.today())].capitalize()
        h3 = soup.find("h3", string=re.compile(today))
        if not h3:
            return None

        next_p = h3.findNext("p")
        if next_p.find("img"):
            next_p = next_p.findNext("p")

        return [str(item).strip() for item in next_p.contents if str(item) != "<br/>"]
    except Exception:
        return None


def crawl_himasali():
    try:
        r = requests.get("https://www.himasali.com/lounaslista/")

        today = DATE_MAP[date.weekday(date.today())].capitalize()

        soup = BeautifulSoup(r.text, "html.parser")
        for i in range(0, 20):
            lst = soup.find_all("p")[i].text
            if str(today) in lst:
                return ("\n".join(lst.split("\n")[1:])).splitlines()
    except Exception:
        return None


def crawl_dylanmilk():
    try:
        r = requests.get("https://www.dylan.fi/milk")
        soup = BeautifulSoup(r.text, "html.parser")
        for i in range(0, 50):
            row = soup.find_all("p")[i].text
            today = DATE_MAP[date.weekday(date.today())].capitalize()

            if str(today) in str(row):
                i += 1
                break

        arr = []
        for i in range(i, 50):
            row = soup.find_all("p")[i].text
            if len(str(row)) < 10:
                break
            arr.append(row)

        return arr
    except Exception:
        return None


def crawl_garam_page(url):
    def select_text_content(text_contents):
        lookfor = ["maanantai", "tiistai", "keskiviikko", "torstai", "perjantai"]
        for div in text_contents:
            count = 0
            for word in lookfor:
                if word in div.text.lower():
                    count += 1
            if count >= 3:
                # If most of the weekday words appear in the div, it is
                # probably the lunch list. This lets them to typo couple of the
                # words, but they still need to get most of them right.
                return div
        return text_contents[3]
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        text_contents = soup.find_all(class_="text-content")
        wrapper = select_text_content(text_contents)
        if not wrapper or not wrapper.p:
            return None

        today = DATE_MAP[date.weekday(date.today())].upper()
        tomorrow = DATE_MAP[date.weekday(date.today() + timedelta(1))].upper()

        all_p = wrapper.find_all("p")
        today_index = next(iter([i for i, s in enumerate(all_p) if today in s.text]), None)
        tomorrow_index = next(iter([i for i, s in enumerate(all_p) if tomorrow in s.text]), None)

        if not tomorrow_index:
            tomorrow_index = next(iter([i for i, s in enumerate(all_p) if "Hinnat" in s.text]), None)

        if today_index and tomorrow_index:
            return [p.text for p in all_p[today_index + 1: tomorrow_index]]
    except Exception:
        return None

    return None


def crawl_oikeus():
    return crawl_garam_page("https://www.cafeteria.fi/ravintola-oikeus/")


def crawl_silta():
    return crawl_garam_page("https://www.cafeteria.fi/silta-itamerentalo/")


@app.route("/")
def index():
    data = OrderedDict(
        {
            "min": get_min(),
            "hiili": get_hiili(),
            "silta": crawl_silta(),
            "oikeus": crawl_oikeus(),
            "factory": crawl_factory(),
            "hima&Sali": crawl_himasali(),
            "Dylan Milk": crawl_dylanmilk(),
        }
    )
    return render_template("index.html", data=data)


if __name__ == '__main__':
    app.run()
