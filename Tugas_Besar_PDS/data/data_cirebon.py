import requests
import pandas as pd

URL = "https://opendata.cirebonkota.go.id/api/bigdata/dinas_komunikasi_informatika_dan_statistik_kota_cirebon/jumlah_free_wi_fi_pada_area_publik_di_kota_cirebon_5?"

response = requests.get(URL)
json_data = response.json()


wifi_list = json_data["data"]

print("Jumlah data:", len(wifi_list))

df = pd.DataFrame(wifi_list)

df.to_csv("wifi_cirebon.csv", index=False, encoding="utf-8")

print("CSV berhasil dibuat")
