import pandas as pd
import json
from pathlib import Path

geojson_data = {"type": "FeatureCollection"}
features = []
raw_df = pd.read_json("Data/Raw.json", orient="index")
coord_df = pd.read_json("Data/Coord.json")

for id, r in raw_df.iterrows():
    coord = coord_df[id]
    lat = coord["lat"]
    lon = coord["lon"]
    feature = {
        "type": "Feature",
        "properties": {
            "_markerType": "Icon",
            "_iconUrl": "https://maps.gsi.go.jp/portal/sys/v4/symbols/076.png",
            "_iconSize": [20, 20],
            "_iconAnchor": [10, 10],
            "施設名":r["name"],
            "開放時間":r["time"],
            "休館日":r["close"],
            "対象者":r["target"],
            "費用":r["fee"],
            "自販機/給水施設":r["water"],
            "メモ":r["memo"],
            "ホームページ":r["hp"],
            "連絡先":r["contact"],
            "タイプ":r["type"],
            "所在地":r["address"],
        },
        "geometry":{
            "type":"Point",
            "coordinates":[lat, lon],
        }
    }
    features.append(feature)

geojson_data["features"] = features
json.dump(geojson_data, Path("Map/かわさきちょこ涼.geojson").open("w"), ensure_ascii=False, indent=1)