import requests
import pandas as pd

URL = "https://opendata.bandung.go.id/api/bigdata/dinas_komunikasi_dan_informatika_kota_bandung/jumlah_pengguna_wifi_bandung_juara_2?per_page=1140"

response = requests.get(URL)
json_data = response.json()


wifi_list = json_data["data"]

print("Jumlah data:", len(wifi_list))

df = pd.DataFrame(wifi_list)

df.to_csv("wifi_bandung.csv", index=False, encoding="utf-8")

print("CSV berhasil dibuat")
