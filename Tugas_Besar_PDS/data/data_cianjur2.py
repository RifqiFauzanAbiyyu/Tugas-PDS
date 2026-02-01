import requests
import pandas as pd

URL = "https://opendata.cianjurkab.go.id/api/bigdata/dinas_komunikasi_informatika_dan_persandian/daftar_wifi_publik_di_kabupaten_cianjur?per_page=199"

response = requests.get(URL)
json_data = response.json()

# INI INTINYA
wifi_list = json_data["data"]

print("Jumlah data:", len(wifi_list))

df = pd.DataFrame(wifi_list)

df.to_csv("wifi_cianjur2.csv", index=False, encoding="utf-8")

print("CSV berhasil dibuat")
