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

    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="RaceTable01")

    if not table:
        return {"error": "出馬表テーブルが見つかりません", "race_id": race_id}

    horses = []
    rows = table.find_all("tr", class_="HorseList")

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 8:
            continue

        horses.append({
            "number": tds[0].text.strip(),              # 馬番
            "waku": tds[1].text.strip(),                # 枠番
            "name": tds[3].text.strip(),                # 馬名
            "sex_age": tds[4].text.strip(),             # 性齢（例：牡5）
            "weight": tds[5].text.strip(),              # 斤量
            "jockey": tds[6].text.strip(),              # 騎手名
            "trainer": tds[7].text.strip()              # 調教師名
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
