import requests
import pandas as pd

URL = "https://opendata.bekasikota.go.id/api/bigdata/dinas_komunikasi_informatika_statistik_dan_persandian/titik_wifi_bekasikotapatriot_wifi_id_kota_bekasi_1?per_page=3878"

response = requests.get(URL)
json_data = response.json()


wifi_list = json_data["data"]

print("Jumlah data:", len(wifi_list))

df = pd.DataFrame(wifi_list)

df.to_csv("wifi_bekasi.csv", index=False, encoding="utf-8")

print("CSV berhasil dibuat")
