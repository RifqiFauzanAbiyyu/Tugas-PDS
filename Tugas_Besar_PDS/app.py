import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, FeatureGroupSubGroup
from streamlit_folium import st_folium
import plotly.express as px
import os
# =========================
# 1. CONFIG & SETTING
# =========================
st.set_page_config(
    page_title="Analisis WiFi Jawa Barat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Sidebar Hijau (#86de6f) dengan Teks Putih
# Hapus huruf 'f' di depan kutip tiga untuk menghindari SyntaxError
st.markdown("""
    <style>
    /* Background Sidebar Hijau */
    [data-testid="stSidebar"] {
        background-color: #6dbc59;
    }

    /* Hilangkan padding atas agar benar-benar mepet */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 1rem;
    }

    /* Container Header Sidebar (FLEXBOX agar sejajar) */
    .sidebar-header {
        display: flex;
        align-items: center; /* Sejajar secara vertikal */
        gap: 15px; /* Jarak antara icon dan teks */
        margin-top: -20px;
        padding: 10px;
        color: white !important;
        font-weight: bold;
        font-size: 1.3rem;
    }

    /* Styling Icon WiFi Putih */
    .wifi-icon {
        font-size: 2.8rem;
        filter: brightness(0) invert(1); /* Trik memaksa icon jadi putih */
    }

    /* Styling Teks Judul Putih */
    .sidebar-title {
        color: white !important;
        font-size: 1.2rem;
        line-height: 1.2;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }

    /* Menu Navigasi (Radio) Teks Putih */
    [data-testid="stSidebar"] .stRadio label p {
        color: #ffffff !important;
        font-weight: 500;
        font-size: 16px;
    }
    
    /* Garis pembatas tipis putih */
    hr {
        border: 0.5px solid rgba(255,255,255,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# 2. DATA LOADING & CLEANING
# =========================
@st.cache_data
def load_data():
    if not (os.path.exists('data/wifi_jabar_final.csv') and os.path.exists('data/penduduk_clean.csv')):
        return None, None
    
    wifi = pd.read_csv("data/wifi_jabar_final.csv", sep=";")
    penduduk = pd.read_csv("data/penduduk_clean.csv", sep=";")
    penduduk.columns = penduduk.columns.str.strip()
    
    def clean_pop_numeric(val):
        try:
            s = str(val).split('.')[0]
            return int(s) * 1000
        except: return 0
    penduduk["jumlah_penduduk_numeric"] = penduduk["jumlah_penduduk"].apply(clean_pop_numeric)
    
    def fix_coord(val, is_lat=True):
        if pd.isna(val): return 0.0
        s = str(val).replace('.', '').replace('-', '').replace(',', '')
        if not s: return 0.0
        div = 10**(len(s)-1) if is_lat else 10**(len(s)-3)
        res = float(s) / div
        return -res if is_lat else res

    wifi['lat_kec_clean'] = wifi['lat_kec'].apply(lambda x: fix_coord(x, True))
    wifi['lon_kec_clean'] = wifi['lon_kec'].apply(lambda x: fix_coord(x, False))
    wifi['lat_kot_clean'] = wifi['lat_kot'].apply(lambda x: fix_coord(x, True))
    wifi['lon_kot_clean'] = wifi['lon_kot'].apply(lambda x: fix_coord(x, False))
    return wifi, penduduk

wifi_df, penduduk_df = load_data()

# =========================
# 3. SIDEBAR (LOGO & NAMA SEJAJAR)
# =========================
st.sidebar.markdown("""
    <div class="sidebar-header">
        <span style="font-size: 2.5rem;">🌐</span>
        <div>Analisis WiFi<br>Jawa Barat</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "📌 Pilih Menu",
    [
        "🏠 Beranda",
        "📶 Data Titik WiFi",
        "👥 Data Penduduk",
        "📊 Visualisasi & Grafik",
        "📈 Analisis Rasio",
        "🗺️ Peta Persebaran WiFi",
        "💡 Saran Pengembangan"
    ]
)

# =========================================================
# MENU 0 — DASHBOARD
# =========================================================
if menu == "🏠 Beranda":
    st.title("📊 Sistem Informasi Geografis WiFi Publik Jabar")
    
    # Sub-judul yang lebih santai
    st.subheader("Meninjau Ketersediaan Internet Gratis untuk Masyarakat")
    
    # HITUNG DATA SECARA OTOMATIS
    total_wifi = len(wifi_df)
    total_kota = wifi_df['kota_kabupaten'].nunique()
    total_kecamatan = wifi_df['kecamatan'].nunique()

    # TAMPILKAN METRIK
    col1, col2, col3= st.columns(3)
    col1.metric("Total Titik WiFi", f"{total_wifi} Titik")
    col2.metric("Total Kota/Kab", f"{total_kota}")
    col3.metric("Total Kecamatan", f"{total_kecamatan}")

    st.divider()

    # Penjelasan Fitur (Semua Menu)
    st.markdown("### 🔍 Apa yang dapat Anda temukan di sini?")
    
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown("""
        **1. Informasi Lokasi Spesifik**
        * Cek alamat lengkap dan nama tempat titik WiFi di menu **Data Titik WiFi**.
        * Lihat titik koordinat fisik secara langsung di **Peta Persebaran WiFi**.
        
        **2. Data Kependudukan**
        * Lihat jumlah populasi penduduk di tiap wilayah melalui menu **Data Penduduk**.
        """)

    with right_col:
        st.markdown("""
        **3. Analisis & Grafik**
        * Pantau perbandingan antar wilayah secara visual di **Visualisasi & Grafik**.
        * Cek pemerataan akses internet di menu **Analisis Rasio**.
        
        **4. Rekomendasi Pintar**
        * Dapatkan saran wilayah prioritas pembangunan di menu **Saran Pengembangan**.
        """)

    st.divider()
    st.info("💡 **Tips:** Gunakan menu di samping kiri untuk menjelajahi data lebih dalam.")
    with st.expander("📝 Catatan Penting Mengenai Data"):
        st.warning("""
    **Catatan Data:** Analisis dalam dashboard ini disusun berdasarkan data publik yang tersedia. 
    Meskipun cakupan wilayah saat ini masih terbatas pada data yang berhasil dihimpun, 
    informasi ini tetap dapat memberikan gambaran mengenai pola sebaran WiFi publik di Jawa Barat.
    """)
# =========================================================
# MENU 1 — JUMLAH WIFI PER KOTA
# =========================================================
elif menu == "📶 Data Titik WiFi":
    st.title("📋 Data Titik WiFi Publik")
    st.markdown("Halaman ini menampilkan sebaran titik akses internet berdasarkan data yang tersedia.")

    # Bagian Filter
    list_kota = ["Semua"] + sorted(wifi_df['kota_kabupaten'].unique().tolist())
    selected_kota = st.selectbox("📍 Pilih Wilayah yang ingin ditampilkan:", list_kota)
    
    # Proses filtering data
    filtered_wifi = wifi_df if selected_kota == "Semua" else wifi_df[wifi_df['kota_kabupaten'] == selected_kota]

    # Menggunakan TAB
    tab_ringkasan, tab_detail = st.tabs(["📊 Ringkasan Data", "📋 Detail Lokasi"])

    with tab_ringkasan:
        st.subheader("Ringkasan Jumlah per Kota")
        # Hitung agregat
        wifi_summary = filtered_wifi.groupby("kota_kabupaten").size().reset_index(name="Jumlah Titik WiFi")
        wifi_summary = wifi_summary.sort_values("Jumlah Titik WiFi", ascending=False)
        
        st.dataframe(wifi_summary, use_container_width=True, hide_index=True)

    with tab_detail:
        st.subheader(f"Detail Lokasi: {selected_kota}")
        
        # Filter kolom
        cols_to_show = [
            c for c in filtered_wifi.columns 
            if not any(x in c.lower() for x in ['lat', 'lon', 'key_kec', 'clean'])
        ]
        
        st.dataframe(filtered_wifi[cols_to_show], use_container_width=True, hide_index=True)

    csv = filtered_wifi[cols_to_show].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Sebagai CSV",
        data=csv,
        file_name=f'data_wifi_{selected_kota.lower().replace(" ", "_")}.csv',
        mime='text/csv',
    )
# =========================================================
# MENU 2 — DATA PENDUDUK PER KOTA
# =========================================================
elif menu == "👥 Data Penduduk":
    st.title("👥 Data Demografi Penduduk")
    
    # --- PROSES MEMBERSIHKAN DATA (HAPUS .00 & FORMAT TITIK) ---
    # 1. Buang bagian desimal .00 agar angka jadi bulat
    penduduk_df['jumlah_penduduk'] = (
        penduduk_df['jumlah_penduduk']
        .astype(str)
        .str.split('.').str[0] 
        .str.replace(r'[^\d]', '', regex=True)
    )
    
    # 2. Ubah ke angka bulat (int) agar bisa muncul pemisah titik di tabel
    penduduk_df['jumlah_penduduk'] = pd.to_numeric(penduduk_df['jumlah_penduduk'], errors='coerce').fillna(0).astype(int)
    # ---------------------------------------------------------

    # Filter Wilayah
    list_kota_pop = ["Semua"] + sorted(penduduk_df['kota_kabupaten'].unique().tolist())
    selected_kota_pop = st.selectbox("📍 Pilih Kota/Kabupaten:", list_kota_pop)
    
    filtered_pop = penduduk_df if selected_kota_pop == "Semua" else penduduk_df[penduduk_df['kota_kabupaten'] == selected_kota_pop]

    # TAMPILAN TABEL (Langsung tabel tanpa metrik di atasnya)
    st.subheader(f"Tabel Populasi: {selected_kota_pop}")
    
    # Pilih kolom yang mau ditampilkan sesuai CSV kamu
    display_pop = filtered_pop[["kota_kabupaten", "jumlah_penduduk", "satuan", "tahun"]].copy()

    st.dataframe(
        display_pop.sort_values("jumlah_penduduk", ascending=False), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "jumlah_penduduk": st.column_config.NumberColumn(
                "Jumlah Penduduk",
                format="%d", # Otomatis kasih titik sebagai pemisah ribuan
            ),
            "satuan": "Satuan",
            "kota_kabupaten": "Kota/Kabupaten",
            "tahun": "Tahun"
        }
    )
    
    # Tombol Download
    csv_pop = display_pop.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Penduduk (CSV)", 
        data=csv_pop, 
        file_name=f'data_penduduk_{selected_kota_pop.lower().replace(" ", "_")}.csv'
    )

# =========================================================
# MENU 3 — VISUALISASI & GRAFIK
# =========================================================
elif menu == "📊 Visualisasi & Grafik":
    st.header("📈 Visualisasi Perbandingan WiFi Jawa Barat")
    
    # Menyiapkan data untuk grafik
    wifi_counts = wifi_df.groupby("kota_kabupaten").size().reset_index(name="jumlah_wifi")
    merged_viz = pd.merge(wifi_counts, penduduk_df, on="kota_kabupaten")
    
    tab1, tab2 = st.tabs(["📊 Peringkat WiFi per Kota", "📍 WiFi vs Jumlah Penduduk"])
    
    with tab1:
        fig1 = px.bar(merged_viz.sort_values("jumlah_wifi"), 
                     x="jumlah_wifi", 
                     y="kota_kabupaten", 
                     orientation='h', 
                     title="Peringkat Jumlah WiFi per Kabupaten/Kota",
                     color="jumlah_wifi", 
                     color_continuous_scale="Viridis",
                     labels={"jumlah_wifi": "Total Titik WiFi", "kota_kabupaten": "Wilayah"})
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Penjelasan untuk orang awam
        st.info("""
        **🔍 Cara Membaca Grafik Peringkat:**
        * Grafik ini menunjukkan **siapa yang punya 'stok' WiFi paling banyak**. 
        * Semakin panjang batang ke arah kanan, berarti Pemerintah Daerah tersebut sudah memasang lebih banyak titik WiFi gratis untuk warga.
        * **Warna Kuning/Terang:** Wilayah dengan fasilitas WiFi paling melimpah.
        * **Warna Ungu/Gelap:** Wilayah yang jumlah titik WiFi-nya masih sedikit.
        """)

    with tab2:
        fig2 = px.scatter(merged_viz, 
                         x="jumlah_penduduk_numeric", 
                         y="jumlah_wifi", 
                         text="kota_kabupaten", 
                         size="jumlah_wifi",
                         title="Korelasi Jumlah Penduduk vs Jumlah WiFi",
                         labels={"jumlah_penduduk_numeric": "Total Penduduk", "jumlah_wifi": "Jumlah Titik WiFi"})
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Penjelasan untuk orang awam
        st.warning("""
        **🔍 Cara Membaca Grafik Korelasi:**
        Grafik ini memberi tahu kita: **"Apakah jumlah WiFi sudah adil jika dibanding jumlah orangnya?"**
        
        * **Semakin ke Kanan:** Jumlah penduduknya semakin padat.
        * **Semakin ke Atas:** Jumlah titik WiFi-nya semakin banyak.
        
        **Tanda Bahaya (🚨):** Jika ada nama kota yang posisinya **sangat ke kanan tapi rendah (di bawah)**, artinya kota tersebut sedang "Krisis Digital". Penduduknya jutaan, tapi titik WiFi-nya sangat sedikit. Idealnya, kota-kota harus berada di garis diagonal (semakin banyak penduduk, semakin banyak WiFi).
        """)

# =========================================================
# MENU 4 — ANALISI RASIO
# =========================================================
elif menu == "📈 Analisis Rasio":
    st.title("📊 Analisis Pemerataan WiFi Publik")
    st.markdown("""
    Analisis ini mengukur perbandingan jumlah titik WiFi dengan populasi penduduk (per 100.000 jiwa).
    Pembagian warna membantu mengidentifikasi wilayah mana yang sudah cukup atau masih kurang.
    """)

    # --- 1. PROSES DATA ---
    wifi_counts = wifi_df.groupby("kota_kabupaten").size().reset_index(name="jumlah_wifi")
    
    penduduk_clean = penduduk_df.copy()
    penduduk_clean['jumlah_penduduk'] = (
        penduduk_clean['jumlah_penduduk']
        .astype(str)
        .str.split('.').str[0]
        .str.replace(r'[^\d]', '', regex=True)
    )
    penduduk_clean['jumlah_penduduk'] = pd.to_numeric(penduduk_clean['jumlah_penduduk'], errors='coerce').fillna(0).astype(int)

    analisis_df = pd.merge(penduduk_clean, wifi_counts, on="kota_kabupaten", how="left")
    analisis_df["jumlah_wifi"] = analisis_df["jumlah_wifi"].fillna(0).astype(int)
    
    # Rasio per 100.000 Penduduk
    analisis_df["rasio"] = (analisis_df["jumlah_wifi"] / analisis_df["jumlah_penduduk"].replace(0, 1)) * 100000
    
    # --- 2. KATEGORI WARNA (Lebih Banyak Tingkatan) ---
    def kategori_warna_profesional(r):
        if r == 0:
            return "🔴 Sangat Rendah"
        elif r < 2:
            return "🟠 Rendah"
        elif r < 7:
            return "🟡 Sedang"
        elif r < 15:
            return "🔵 Cukup Baik"
        else:
            return "🟢 Sangat Baik"

    analisis_df["status"] = analisis_df["rasio"].apply(kategori_warna_profesional)

    # --- 3. TAMPILAN TABEL ---
    st.subheader("Hasil Analisis Wilayah")
    
    st.dataframe(
        analisis_df[["kota_kabupaten", "jumlah_wifi", "jumlah_penduduk", "rasio", "status"]]
        .sort_values("rasio", ascending=False), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "kota_kabupaten": "Kota/Kabupaten",
            "jumlah_wifi": "Total WiFi",
            "jumlah_penduduk": st.column_config.NumberColumn("Total Penduduk", format="%d"),
            "rasio": st.column_config.NumberColumn("Rasio", format="%.2f"),
            "status": "Status Ketersediaan"
        }
    )

    st.divider()

    # --- 4. LEGENDA WARNA ---
    st.markdown("""
    **Keterangan Warna:**
    * 🟢 **Sangat Baik**: Ketersediaan WiFi sangat melimpah dibanding jumlah warga.
    * 🔵 **Cukup Baik**: Wilayah dengan akses WiFi yang sudah memadai.
    * 🟡 **Sedang**: Wilayah dengan akses WiFi rata-rata.
    * 🟠 **Rendah**: Wilayah yang butuh penambahan titik WiFi.
    * 🔴 **Sangat Rendah**: Wilayah prioritas utama (belum ada data WiFi).
    """)
# =========================================================
# MENU 5 — MAP (KODE ASLI KAMU - TIDAK DIUBAH)
# =========================================================
elif menu == "🗺️ Peta Persebaran WiFi":
    # --- FUNGSI PEMBANTU ---
    def format_id_pop(val):
        try:
            v = str(val).split('.')[0]
            v = int(''.join(filter(str.isdigit, v)))
            return "{:,}".format(v).replace(",", ".")
        except:
            return "0"

    # HTML Templates (Tetap sama seperti aslimu)
    def get_kota_popup_html(row):
        pop_formatted = format_id_pop(row['jumlah_penduduk'])
        return f"""
        <div style="width: 240px; font-family: sans-serif; border-radius: 8px; overflow: hidden; border: 1px solid #1a73e8;">
            <div style="background: #1a73e8; color: white; padding: 10px; font-weight: bold; text-align: center;">📍 {row['kota_kabupaten']}</div>
            <div style="padding: 10px; font-size: 12px; background: #fff;">
                <b>👨‍👩‍👧‍👦 Penduduk:</b> {pop_formatted} Jiwa<br>
                <b>🏙️ Kecamatan:</b> {row['kecamatan_count']}<br>
                <b>📶 Total WiFi:</b> {row['id_wifi_count']} Titik
            </div>
        </div>
        """

    def get_kec_popup_html(row):
        return f"""
        <div style="width: 200px; font-family: sans-serif; border-left: 5px solid #d32f2f; padding: 8px; background: white;">
            <b style="color: #d32f2f;">{row['kecamatan']}</b><br>
            <span style="font-size: 11px; color: #666;">{row['nama_lokasi']}</span>
            <hr style="margin: 5px 0;">
            <div style="font-size: 10px;"><b>Alamat:</b> {row['alamat']}</div>
        </div>
        """

    st.title("🌐 Peta Monitoring WiFi Jawa Barat")
    
    # --- OPTIMASI LOADING: Gunakan st.cache_data untuk Merge & Agg ---
    @st.cache_data
    def prepare_map_data(wifi_df, penduduk_df):
        # Merge hanya kolom yang diperlukan saja
        df_res = pd.merge(
            wifi_df, 
            penduduk_df[['kota_kabupaten', 'jumlah_penduduk']], 
            on='kota_kabupaten', 
            how='left'
        )
        # Agregasi Kota
        agg = df_res.groupby('kota_kabupaten').agg({
            'lat_kot_clean': 'first', 
            'lon_kot_clean': 'first',
            'kecamatan': 'nunique', 
            'id_wifi': 'count', 
            'jumlah_penduduk': 'first'
        }).rename(columns={'kecamatan': 'kecamatan_count', 'id_wifi': 'id_wifi_count'}).reset_index()
        return df_res, agg

    # Jalankan persiapan data (Hanya lari sekali, selanjutnya instan)
    df_map, kota_agg = prepare_map_data(wifi_df, penduduk_df)

    # Inisialisasi Peta
    m = folium.Map(location=[-6.9175, 107.6191], zoom_start=8, tiles='OpenStreetMap')
    main_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    # Looping Utama
    for _, row in kota_agg.iterrows():
        sub_group = FeatureGroupSubGroup(main_cluster, row['kota_kabupaten'])
        m.add_child(sub_group)
        
        # Marker Kota (Gunakan Marker biasa)
        folium.Marker(
            location=[row['lat_kot_clean'], row['lon_kot_clean']],
            popup=folium.Popup(get_kota_popup_html(row), max_width=300),
            tooltip=row['kota_kabupaten'],
            icon=folium.Icon(color='blue', icon='university', prefix='fa')
        ).add_to(m)

        # Marker Kecamatan
        df_kec = df_map[df_map['kota_kabupaten'] == row['kota_kabupaten']]
        for _, kec_row in df_kec.iterrows():
            # CircleMarker lebih ringan daripada Marker Icon untuk ribuan titik
            folium.CircleMarker(
                location=[kec_row['lat_kec_clean'], kec_row['lon_kec_clean']],
                radius=5, color='#d32f2f', fill=True, fill_color='#f44336', fill_opacity=0.7,
                popup=folium.Popup(get_kec_popup_html(kec_row), max_width=250)
            ).add_to(sub_group)

    folium.LayerControl().add_to(m)
    st_folium(m, width="100%", height=700, returned_objects=[])
# =========================================================
# MENU 6 — REKOMENDASI
# =========================================================
elif menu == "💡 Saran Pengembangan":
    st.header("💡 Rekomendasi Prioritas Pemerataan")
    wifi_counts = wifi_df.groupby("kota_kabupaten").size().reset_index(name="jumlah_wifi")
    rec_df = pd.merge(penduduk_df, wifi_counts, on="kota_kabupaten", how="left").fillna(0)
    rec_df["rasio"] = (rec_df["jumlah_wifi"] / rec_df["jumlah_penduduk_numeric"]) * 100000
    prioritas = rec_df.sort_values("rasio").head(5)
    
    st.warning("### ⚠️ Wilayah Prioritas Penambahan WiFi")
    for i, row in prioritas.iterrows():
        with st.expander(f"📍 {row['kota_kabupaten']}"):
            st.write(f"**Populasi:** {row['jumlah_penduduk_numeric']:,} Jiwa")
            st.write(f"**Rasio Saat Ini:** {row['rasio']:.2f} per 100rb Penduduk")
            st.info(f"Disarankan penambahan titik akses segera.")