import streamlit as st
import pandas as pd
import folium
import random
import plotly.express as px
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard WiFi Jawa Barat", layout="wide")

# --- 2. FUNGSI CLEANING ---
def clean_lat_long(val):
    try:
        s = str(val).replace('.', '').replace(',', '')
        if not s: return 0.0
        if s.startswith('-'):
            return float(s[0:2] + '.' + s[2:])
        else:
            return float(s[0:3] + '.' + s[3:])
    except: return 0.0

# --- 3. LOAD DATA ---
@st.cache_data
def load_data():
    df_w = pd.read_csv('wifi_jabar_final_geo.csv', sep=';')
    df_p = pd.read_csv('penduduk_clean.csv')
    df_w['lat_kec_clean'] = df_w['lat_kec'].apply(clean_lat_long)
    df_w['lon_kec_clean'] = df_w['lon_kec'].apply(clean_lat_long)
    return df_w, df_p

df_wifi, df_penduduk = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌐 Menu Navigasi")
    menu = st.radio(
        "Pilih Halaman:",
        ["🏠 Ringkasan Informasi", "📊 Detail Data & Filter", "🗺️ Peta Sebaran", "📈 Grafik Analisis", "🎯 Rekomendasi Pembangunan"]
    )

# ---------------------------------------------------------
# MENU 1: RINGKASAN
# ---------------------------------------------------------
if menu == "🏠 Ringkasan Informasi":
    st.title("🚀 Dashboard WiFi Jawa Barat")
    st.markdown("---")
    total_wifi = len(df_wifi)
    total_kota = df_wifi['kota_kabupaten'].nunique()
    total_pop = df_penduduk[df_penduduk['tahun'] == 2025]['jumlah_penduduk'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("📶 Total Titik WiFi", f"{total_wifi:,}")
    c2.metric("🏙️ Cakupan Wilayah", total_kota)
    c3.metric("👥 Penduduk (2025)", f"{total_pop:,.0f} Ribu")

# ---------------------------------------------------------
# MENU 2: DETAIL DATA
# ---------------------------------------------------------
elif menu == "📊 Detail Data & Filter":
    st.header("🔍 Eksplorasi Data")
    list_kota = sorted(df_wifi['kota_kabupaten'].unique())
    pilih_kota = st.selectbox("Pilih Wilayah:", ["Semua Kota"] + list_kota)
    df_w_v = df_wifi if pilih_kota == "Semua Kota" else df_wifi[df_wifi['kota_kabupaten'] == pilih_kota]
    st.dataframe(df_w_v, use_container_width=True)

# ---------------------------------------------------------
# MENU 3: PETA (TIDAK BERUBAH)
# ---------------------------------------------------------
elif menu == "🗺️ Peta Sebaran":
    st.header("🗺️ Peta Interaktif")
    m = folium.Map(location=[-6.9175, 107.6191], zoom_start=8)
    icon_create_function = """
    function(cluster) {
        return L.divIcon({
            html: '<div style="position:relative;"><i class="fa fa-map-marker fa-3x" style="color: #d9534f; text-shadow: 2px 2px 2px #000;"></i></div>',
            className: 'marker-cluster-custom',
            iconSize: L.point(30, 30),
            iconAnchor: L.point(15, 30)
        });
    }
    """
    mc_utama = MarkerCluster(icon_create_function=icon_create_function, disableClusteringAtZoom=12).add_to(m)
    for kota, group_kota in df_wifi.groupby('kota_kabupaten'):
        avg_lat, avg_lon = group_kota['lat_kec_clean'].mean(), group_kota['lon_kec_clean'].mean()
        jml_kec = group_kota['kecamatan'].nunique()
        info_p = df_penduduk[(df_penduduk['kota_kabupaten'] == kota) & (df_penduduk['tahun'] == 2025)]
        populasi = info_p['jumlah_penduduk'].sum() if not info_p.empty else 0
        folium.Marker(location=[avg_lat, avg_lon], tooltip=f"🏙️ <b>{kota}</b><br>📍 {jml_kec} Kec<br>👥 {populasi:,.0f} Ribu", icon=folium.Icon(color='red', icon='city', prefix='fa')).add_to(mc_utama)
        for kec, group_kec in group_kota.groupby('kecamatan'):
            lat_kc, lon_kc = group_kec['lat_kec_clean'].iloc[0], group_kec['lon_kec_clean'].iloc[0]
            jml_wifi_kec = len(group_kec)
            folium.Marker(location=[lat_kc, lon_kc], tooltip=f"<b>Kecamatan: {kec}</b><br>📶 {jml_wifi_kec} WiFi", icon=folium.Icon(color='blue', icon='info-sign')).add_to(mc_utama)
            for _, row in group_kec.iterrows():
                j_lat, j_lon = lat_kc + random.uniform(-0.003, 0.003), lon_kc + random.uniform(-0.003, 0.003)
                folium.CircleMarker(location=[j_lat, j_lon], radius=5, color='green', fill=True, popup=f"WiFi: {row['nama_lokasi']}").add_to(mc_utama)
    folium_static(m, width=1100, height=600)

# ---------------------------------------------------------
# MENU 4: GRAFIK ANALISIS
# ---------------------------------------------------------
elif menu == "📈 Grafik Analisis":
    st.title("📈 Visualisasi Data Perbandingan")
    
    # Hitung data WiFi per Kota
    df_cnt = df_wifi['kota_kabupaten'].value_counts().reset_index()
    df_cnt.columns = ['kota_kabupaten', 'jumlah_wifi']
    
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(df_cnt, x='jumlah_wifi', y='kota_kabupaten', orientation='h', title="Jumlah WiFi per Kota", color='jumlah_wifi')
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.pie(df_cnt.head(10), values='jumlah_wifi', names='kota_kabupaten', title="Top 10 Persentase WiFi", hole=0.3)
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# MENU 5: HASIL REKOMENDASI (SISTEM CERDAS)
# ---------------------------------------------------------
elif menu == "🎯 Rekomendasi Pembangunan":
    st.title("🎯 Hasil Rekomendasi Wilayah")
    st.write("Wilayah yang muncul di urutan teratas adalah yang memiliki rasio WiFi terkecil dibandingkan jumlah penduduknya.")

    # Gabung Data & Hitung Rasio
    df_wifi_cnt = df_wifi['kota_kabupaten'].value_counts().reset_index()
    df_wifi_cnt.columns = ['kota_kabupaten', 'jumlah_wifi']
    df_pop = df_penduduk[df_penduduk['tahun'] == 2025][['kota_kabupaten', 'jumlah_penduduk']]
    
    df_res = pd.merge(df_wifi_cnt, df_pop, on='kota_kabupaten')
    df_res['skor_rasio'] = (df_res['jumlah_wifi'] / df_res['jumlah_penduduk']) * 1000
    df_res = df_res.sort_values('skor_rasio', ascending=True)

    # Grafik Rasio
    fig_res = px.bar(df_res, x='skor_rasio', y='kota_kabupaten', orientation='h', 
                     title="Prioritas Pembangunan (Rasio Terendah = Prioritas Utama)",
                     color='skor_rasio', color_continuous_scale='Reds_r')
    st.plotly_chart(fig_res, use_container_width=True)

    # Box Rekomendasi
    st.markdown("---")
    kota_prio = df_res.iloc[0]['kota_kabupaten']
    st.error(f"### 📢 Rekomendasi Utama: {kota_prio}")
    st.write(f"Berdasarkan analisis data, **{kota_prio}** sangat direkomendasikan untuk pembangunan titik WiFi baru karena memiliki rasio ketersediaan paling rendah terhadap jumlah penduduk.")