import requests
import pandas as pd

URL = "https://opendata.cianjurkab.go.id/api/bigdata/dinas_komunikasi_informatika_dan_persandian/jmlh_ds_yng_mndptkn_plynn_wf_grts_brdsrkn_kcmtn_d_kbptn_cnjr?"

response = requests.get(URL)
json_data = response.json()

# INI INTINYA
wifi_list = json_data["data"]

print("Jumlah data:", len(wifi_list))

df = pd.DataFrame(wifi_list)

df.to_csv("wifi_cianjur.csv", index=False, encoding="utf-8")

print("CSV berhasil dibuat")
