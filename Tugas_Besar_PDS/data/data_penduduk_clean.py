import pandas as pd

# 1. AMBIL REFERENSI KOTA DARI DATA WIFI
# Menggunakan sep=";" sesuai format file wifi_jabar_final_geo kamu
df_wifi = pd.read_csv("wifi_jabar_final_geo.csv", sep=";")

# PERBAIKAN: Tambahkan .str sebelum .upper()
list_kota_referensi = df_wifi['kota_kabupaten'].astype(str).str.strip().str.upper().unique().tolist()
print(f"🔍 Referensi: Ada {len(list_kota_referensi)} kota unik di data WiFi.")

# 2. LOAD DATA PENDUDUK KOTOR
df_pdk = pd.read_csv("data_penduduk.csv", sep=";")

# 3. FILTER TAHUN 2025 SAJA
df_2025 = df_pdk[df_pdk['tahun'] == 2025].copy()

# 4. PENYESUAIAN NAMA KOLOM & FILTER KOTA
# Ganti nama agar sama dengan data WiFi
df_2025 = df_2025.rename(columns={'nama_kabupaten_kota': 'kota_kabupaten'})

# Bersihkan teks (Pakai .str.upper() agar tidak error lagi)
df_2025['kota_kabupaten'] = df_2025['kota_kabupaten'].astype(str).str.strip().str.upper()

# --- FILTER INTI: Hanya ambil yang ada di list_kota_referensi ---
df_final = df_2025[df_2025['kota_kabupaten'].isin(list_kota_referensi)].copy()

# 5. CLEANING ANGKA PENDUDUK (Format 2748.07.00)
def fix_populasi(val):
    if pd.isna(val): return 0
    s = str(val).strip()
    parts = s.split('.')
    if len(parts) > 2: # Contoh: 2748.07.00 -> 2748.07
        return float(f"{parts[0]}.{parts[1]}")
    try:
        return float(s)
    except:
        return 0

df_final['jumlah_penduduk'] = df_final['jumlah_penduduk'].apply(fix_populasi)

# 6. SIMPAN HASIL
# Kita simpan kolom yang penting saja
df_final = df_final[['kota_kabupaten', 'jumlah_penduduk', 'satuan', 'tahun']]
df_final.to_csv("penduduk_clean.csv", index=False)

print("\nPROSES BERHASIL!")
print(f"Berhasil mengambil {len(df_final)}")