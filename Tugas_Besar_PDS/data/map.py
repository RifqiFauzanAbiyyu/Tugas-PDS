import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(layout="wide")
st.title("🗺️ GIS WiFi Publik Jawa Barat (Fixed Coordinates)")

@st.cache_data
def load_and_fix_data():
    # Baca file dengan separator ;
    df = pd.read_csv("wifi_jabar_final_geo.csv", sep=";", low_memory=False)
    
    def clean_jabar_coord(val, is_lat=True):
        if pd.isna(val): return None
        # Ambil cuma angka dan minus
        s = "".join(c for c in str(val) if c in "0123456789-")
        
        if not s: return None
        
        # Logika khusus untuk data kamu:
        # Latitude Jabar itu sekitar -6.xxxxxx
        # Longitude Jabar itu sekitar 107.xxxxxx
        
        if is_lat:
            # Pastikan ada minus di depan
            if not s.startswith("-"): s = "-" + s
            # Ambil karakter pertama (-6) lalu sisanya setelah titik
            # Contoh: -69082772 -> -6.9082772
            return float(s[0:2] + "." + s[2:])
        else:
            # Untuk Longitude: 1.075.741.277 -> Jadi 107.5741277
            # Buang angka '1' di paling depan jika panjangnya berlebih
            if s.startswith("10") and len(s) > 8:
                pass 
            elif s.startswith("1") and len(s) > 9:
                s = s[1:] # Buang angka 1 di depan
            
            return float(s[0:3] + "." + s[3:])

    # Proses pembersihan
    df['clean_lat'] = df['lat_kec'].apply(lambda x: clean_jabar_coord(x, is_lat=True))
    df['clean_lon'] = df['lon_kec'].apply(lambda x: clean_jabar_coord(x, is_lat=False))
    
    # Hapus yang gagal
    return df.dropna(subset=['clean_lat', 'clean_lon'])

try:
    df_fix = load_and_fix_data()
    
    st.success(f"✅ Berhasil memproses {len(df_fix)} titik WiFi dengan koordinat yang benar!")

    # Buat Peta
    m = folium.Map(location=[-6.9175, 107.6191], zoom_start=9)
    mc = MarkerCluster(name="WiFi Jabar").add_to(m)

    for _, row in df_fix.iterrows():
        # Info Popup
        label = f"<b>{row['nama_lokasi']}</b><br>{row['kecamatan']}<br>Tahun: {row['tahun']}"
        
        folium.Marker(
            location=[row['clean_lat'], row['clean_lon']],
            popup=folium.Popup(label, max_width=300),
            tooltip=str(row['nama_lokasi']),
            icon=folium.Icon(color='red', icon='wifi', prefix='fa')
        ).add_to(mc)

    st_folium(m, width=1350, height=750, returned_objects=[])

except Exception as e:
    st.error(f"Error: {e}")