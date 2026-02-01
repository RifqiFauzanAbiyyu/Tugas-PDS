import pandas as pd
from geopy.geocoders import Nominatim
import time
import sys

# --- 1. LOAD DATA & INITIAL CLEANING ---
print("🚀 Memulai Proses... Harap tunggu.")
try:
    # Baca file asli dengan separator ;
    df = pd.read_csv("data/wifi_jabar.csv", sep=";")
    
    # Buang kolom sampah & baris yang tidak punya Kota/Kecamatan
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(subset=['kota_kabupaten', 'kecamatan'])
    
    # Hapus Duplikat (Abaikan ID) agar tidak kerja 2x untuk lokasi yang sama
    df = df.drop_duplicates(subset=['kota_kabupaten', 'kecamatan', 'nama_lokasi', 'alamat', 'tahun'])
    
    print(f"✅ Data dimuat. Ada {len(df)} baris unik yang akan diproses.")
except Exception as e:
    print(f"❌ Error Load File: {e}")
    sys.exit()

# --- 2. SETUP GEOPY ---
geolocator = Nominatim(user_agent="jabar_wifi_final_v3")

def get_geo_with_retry(query, attempt=3):
    for i in range(1, attempt + 1):
        try:
            location = geolocator.geocode(query, timeout=10)
            if location:
                return location.latitude, location.longitude
        except:
            time.sleep(2) # Jeda jika gagal koneksi
    return None, None

# --- 3. PROSES GEOCoding KECAMATAN (Unik) ---
kec_unik = df[['kota_kabupaten', 'kecamatan']].drop_duplicates().reset_index(drop=True)
map_lat_kec, map_lon_kec = {}, {}

for i, row in kec_unik.iterrows():
    q = f"{row['kecamatan']}, {row['kota_kabupaten']}, Jawa Barat, Indonesia"
    
    lat, lon = get_geo_with_retry(q)

    key = row['kota_kabupaten'] + "_" + row['kecamatan']
    map_lat_kec[key] = lat
    map_lon_kec[key] = lon

    time.sleep(2)


# --- 4. PROSES GEOCoding KOTA (Unik) ---
kota_unik = df[['kota_kabupaten']].drop_duplicates().reset_index(drop=True)
map_lat_kot, map_lon_kot = {}, {}

print(f"\n\n🏙️ [STEP 2/2] Mencari Koordinat {len(kota_unik)} Kota/Kabupaten...")
for i, row in kota_unik.iterrows():
    q = f"{row['kota_kabupaten']}, Jawa Barat, Indonesia"
    print(f"🔎 ({i+1}/{len(kota_unik)}) Mencari: {row['kota_kabupaten']}...", end="\r")
    
    lat, lon = get_geo_with_retry(q)
    map_lat_kot[row['kota_kabupaten']] = lat
    map_lon_kot[row['kota_kabupaten']] = lon
    time.sleep(1.1)

# --- 5. MAPPING, FILTERING, & RE-INDEX ---
print("\n\n🧹 Merapikan hasil akhir...")

df['key_kec'] = df['kota_kabupaten'] + "_" + df['kecamatan']
df['lat_kec'] = df['key_kec'].map(map_lat_kec)
df['lon_kec'] = df['key_kec'].map(map_lon_kec)
df['lat_kot'] = df['kota_kabupaten'].map(map_lat_kot)
df['lon_kot'] = df['kota_kabupaten'].map(map_lon_kot)

# Hapus yang tetap tidak ketemu setelah 3x coba
df = df.dropna(subset=['lat_kec', 'lon_kec', 'lat_kot', 'lon_kot'])

# Susun ulang ID agar urut 1, 2, 3...
df = df.reset_index(drop=True)
df['id_wifi'] = df.index + 1

# Bersihkan kolom Tahun (hilangkan .0)
df['tahun'] = pd.to_numeric(df['tahun'], errors='coerce').fillna(0).astype(int)

# --- 6. SIMPAN HASIL FINAL ---
df.to_csv("wifi_jabar_final.csv", index=False)

print("\n✨ SELESAI SEMPURNA! ✨")
print(f"📊 Total record bersih: {len(df)}")
print(f"📂 File disimpan: wifi_jabar_final.csv")