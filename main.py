from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/race_card/{race_id}")
def get_race_card(race_id: str):
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {"error": "ページ取得失敗", "status_code": res.status_code}

    # 文字化け対策：推定エンコーディングを適用
    res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="RaceTable01")

    if not table:
        return {"error": "出馬表テーブルが見つかりません", "race_id": race_id}

    horses = []
    rows = table.find_all("tr", class_="HorseList")

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 7:
            continue
        horses.append({
            "number": tds[0].text.strip(),
            "name": tds[3].text.strip(),
            "jockey": tds[6].text.strip()
        })

    if not horses:
        return {
            "error": "出馬表が取得できません",
            "hint": "HTML構造が変わった or 出馬表が未掲載の可能性",
            "race_id": race_id
        }

    return {
        "race_id": race_id,
        "horses": horses
    }
