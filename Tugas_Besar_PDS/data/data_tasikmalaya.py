import requests
import pandas as pd

URL = "https://opendata.tasikmalayakota.go.id/api/bigdata/dinas_komunikasi_dan_informatika/jmlh_ttk_ntrntwf_brdsrkn_lks_d_kt_tskmly?"

response = requests.get(URL)
json_data = response.json()


wifi_list = json_data["data"]

print("Jumlah data:", len(wifi_list))

df = pd.DataFrame(wifi_list)

df.to_csv("wifi_tasik.csv", index=False, encoding="utf-8")

print("CSV berhasil dibuat")
