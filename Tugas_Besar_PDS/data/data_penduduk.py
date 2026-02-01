import requests
import pandas as pd
import time

urls = [
    "https://data.jabarprov.go.id/api-backend//bigdata/bps/od_20495_jumlah_penduduk_berdasarkan_kabupatenkota_v2?limit=25&skip=0&where=%7B%22tahun%22%3A%5B%222025%22%5D%7D",
    "https://data.jabarprov.go.id/api-backend//bigdata/bps/od_20495_jumlah_penduduk_berdasarkan_kabupatenkota_v2?limit=25&skip=25&where=%7B%22tahun%22%3A%5B%222025%22%5D%7D"
]

# Headers super lengkap untuk menembus 403 Forbidden
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://opendata.jabarprov.go.id",
    "Referer": "https://opendata.jabarprov.go.id/",
    "Connection": "keep-alive"
}

all_data = []

print("🚀 Mencoba menembus proteksi 403... Harap bersabar.")

# Gunakan session agar koneksi lebih stabil
session = requests.Session()

for i, url in enumerate(urls):
    try:
        response = session.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            json_data = response.json()
            # Kadang struktur API beda, kita cek key 'data'
            data_part = json_data.get("data", [])
            all_data.extend(data_part)
            print(f"✅ Halaman {i+1} SUKSES! Mengambil {len(data_part)} data.")
        else:
            print(f"⚠️ Halaman {i+1} Gagal. Status: {response.status_code}")
            # Jika masih 403, cetak sedikit responnya untuk analisa
            if response.status_code == 403:
                print("🚫 Masih diblokir. Server minta akses dari portal resmi.")
        
        time.sleep(3) # Jeda lebih lama agar tidak disangka serangan
        
    except Exception as e:
        print(f"❌ Error: {e}")

if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv("jumlah_penduduk_jabar_2025.csv", index=False)
    print(f"\n✨ BERHASIL! Total data: {len(df)}")
else:
    print("\n⚠️ Jika masih gagal, API ini mungkin butuh Token API atau Cookie aktif dari browser.")