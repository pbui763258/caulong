import requests
from bs4 import BeautifulSoup

def crawl_news(store):
    url = "https://www.python.org/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    latest = soup.find("div", class_="medium-widget blog-widget")
    for li in latest.find_all("li")[:5]:
        a = li.find("a")
        store.create({"MA_VOT": a["href"], "TEN_VOT": a.get_text(strip=True), "GIA_BAN": 0})

