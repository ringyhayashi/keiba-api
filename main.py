from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/race_card/{race_id}")
def get_race_card(race_id: str):
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {"error": "ページ取得失敗"}

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.select_one('table.RaceTable01')
    if not table:
        return {"error": "出馬表が見つかりません"}

    horses = []
    for row in table.select('tr')[1:]:
        cols = row.select('td')
        if len(cols) < 7:
            continue
        horses.append({
            "number": cols[0].text.strip(),
            "name": cols[3].text.strip(),
            "jockey": cols[6].text.strip()
        })

    return {"race_id": race_id, "horses": horses}
