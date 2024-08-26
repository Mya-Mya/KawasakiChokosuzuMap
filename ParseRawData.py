from urllib.request import urlretrieve
from urllib.parse import quote
import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Literal, List
import requests

def retrieve_raw_data():
    """
    次のページに掲示してある2つのExcelファイルをダウンロードする。
    [川崎市HP, 2024, "「かわさきちょこ涼（ちょこすず）」はじめました"](https://www.city.kawasaki.jp/300/page/0000167100.html)
    """
    # 公共施設
    urlretrieve(
        "https://www.city.kawasaki.jp/300/cmsfiles/contents/0000167/167100/choko_list0712.xlsx",
        "Data/PublicRaw.xlsx",
    )
    # 民間施設
    urlretrieve(
        "https://www.city.kawasaki.jp/300/cmsfiles/contents/0000167/167100/M0731.xlsx",
        "Data/PrivateRaw.xlsx",
    )

@dataclass
class Raw:
    type:Literal["Public", "Private"]
    number:int
    name:str
    address:str
    time:str
    close:str
    target:str
    fee:str
    water:str
    memo:str
    hp:str
    contact:str
    id:str = ""
    def __post_init__(self):
        self.id = f"{self.type}{self.number:03d}"

def extract_raw_data():
    """
    `retrieve_raw_data`にてダウンロードした2ファイルを統合し、`Raw.json`を作成する。
    """

    raw_list:List[dict] = []

    df = pd.read_excel(f"Data/PublicRaw.xlsx", header=7)
    for _, r in df.iterrows():
        place = Raw(
            type="Public",
            number=int(r["番号"]),
            name=r["施設名"],
            address=r["所在地"],
            time=r["開放時間"],
            close=r["休館日"],
            target=r["対象年齢"],
            fee=r["費用"],
            water=r["自販機または\n給水施設の有無"],
            memo=r["利用にあたってのお知らせ"],
            hp=r["施設のホームページ"],
            contact=r["施設の連絡先"]
        )
        raw_list.append(place)

    df = pd.read_excel(f"Data/PrivateRaw.xlsx", header=7)
    for _, r in df.iterrows():
        place = Raw(
            type="Private",
            number=int(r["番号"]),
            name=r["施設名"],
            address=r["所在地"],
            time=r["開放時間"],
            close=r["休館日"],
            target=None,
            fee=None,
            water=r["自販機または\n給水施設の有無"],
            memo=r["利用にあたっての施設からのお知らせ"],
            hp=r["施設のホームページ"],
            contact=r["施設の連絡先"]
        )
        raw_list.append(place)
    
    raw_df = pd.DataFrame(raw_list)
    raw_df.set_index("id", inplace=True)
    raw_df.to_json("Data/Raw.json", orient="index", force_ascii=False, indent=1)

def prepare_coord_data():
    """
    `Raw.json`に記載されている住所(`address`)から座標を求める。
    """
    coord_data = []
    raw_df = pd.read_json("Data/Raw.json", orient="index")
    for id, address in raw_df["address"].items():
        print(id, address, end=" ")
        url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={quote(address)}"
        response = requests.get(url)
        lat, lon = response.json()[0]["geometry"]["coordinates"]
        print(lat, lon)
        coord_data.append({
            "id":id,
            "lat":lat,
            "lon":lon
        })
    coord_df = pd.DataFrame(coord_data)
    coord_df.set_index("id", inplace=True)
    coord_df.to_json("Data/Coord.json", orient="index", force_ascii=False, indent=1)

prepare_coord_data()