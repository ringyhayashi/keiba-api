from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()


def _parse_body_weight(text: str):
    """
    '478(+2)' → (478, +2)
    '---'      → (None, None)
    """
    m = re.match(r"(\d+)\(([-+0-9]+)\)", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


@app.get("/race_card/{race_id}")
def get_race_card(race_id: str):
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        return {"error": "ページ取得失敗", "status_code": res.status_code}

    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    # 出馬表テーブル
    table = soup.find("table", class_="RaceTable01")
    if not table:
        return {"error": "出馬表テーブルが見つかりません", "race_id": race_id}

    rows = table.find_all("tr", class_="HorseList")
    horses = []

    for row in rows:
        tds = row.find_all("td")

        # 11 列以上ない＝情報不足（想定外の HTML）なのでスキップ
        if len(tds) < 11:
            continue

        # 列の並び（2025/06 時点）
        # 0: 枠  1: 馬番  2: 印  3: 馬名  4: 性齢  5: 斤量
        # 6: 騎手  7: 厩舎  8: 馬体重(増減)  9: オッズ  10: 人気
        # ※2: 印 は存在するが使用しない

        body_weight, body_diff = _parse_body_weight(tds[8].text.strip())

        horses.append({
            "waku": tds[0].text.strip(),             # 枠番
            "number": tds[1].text.strip(),           # 馬番
            # "mark": tds[2].text.strip(),           # ← 使用しないのでコメントアウト
            "name": tds[3].text.strip(),             # 馬名
            "sex_age": tds[4].text.strip(),          # 性齢
            "carried_weight": tds[5].text.strip(),   # 斤量
            "jockey": tds[6].text.strip(),           # 騎手
            "trainer": tds[7].text.strip(),          # 調教師
            "body_weight": body_weight,              # 馬体重
            "body_weight_diff": body_diff,           # 増減
            "odds": tds[9].text.strip(),             # 単勝オッズ
            "popularity": tds[10].text.strip()       # 人気順位
        })

    if not horses:
        return {
            "error": "出馬表が取得できません",
            "hint": "HTML構造が変わった or 出馬表が未掲載の可能性",
            "race_id": race_id
        }

    return {"race_id": race_id, "horses": horses}
