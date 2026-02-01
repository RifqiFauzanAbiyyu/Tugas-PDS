import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="WiFi Jabar Explorer", page_icon="📡", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("wifi_jabar_clean.csv")
    # Bersihkan nama kolom agar tidak ada spasi tersembunyi
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # --- SIDEBAR NAVIGASI ---
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/b2/Logo_Jawa_Barat.svg", width=80)
        st.title("Pusat Data WiFi")
        st.markdown("---")
        menu = st.radio(
            "SILAKAN PILIH HALAMAN:",
            options=[
                "🏠 Beranda Utama", 
                "📋 Tampilkan Semua Data",
                "💡 Hasil Analisis (Rekomendasi)", 
                "📊 Analisis Grafik (Soon)", 
                "🗺️ Visualisasi Peta (Soon)"
            ],
            index=2 
        )

    # --- MENU: HASIL ANALISIS (DRILL-DOWN LOGIC) ---
    if menu == "💡 Hasil Analisis (Rekomendasi)":
        st.title("💡 Rekomendasi Lokasi Pemasangan WiFi Baru")
        st.write("Klik pada nama kota di bawah untuk melihat detail kecamatan yang minim akses.")

        # 1. Hitung Statistik Per Kota
        # Mengelompokkan berdasarkan kota dan menghitung jumlah ID WiFi
        kota_stats = df.groupby('kota_kabupaten').size().reset_index(name='Total_WiFi')
        
        # 2. Ambil Top 10 Kota dengan WiFi PALING SEDIKIT
        top_10_minim = kota_stats.sort_values(by='Total_WiFi', ascending=True).head(10)
        list_kota = top_10_minim['kota_kabupaten'].tolist()

        # Gunakan Session State agar pilihan tidak hilang saat halaman refresh
        if 'selected_city' not in st.session_state:
            st.session_state.selected_city = list_kota[0]

        # 3. Tampilkan Tombol Top 10 Kota (Baris Berjejer)
        st.markdown("### 📍 Top 10 Wilayah Minim WiFi (Klik Nama Kota)")
        
        # Membuat grid 5 kolom (jadi ada 2 baris)
        cols = st.columns(5)
        for i, nama_kota in enumerate(list_kota):
            with cols[i % 5]:
                # Tombol akan berubah warna/style jika sedang dipilih
                if st.button(nama_kota, key=f"btn_{nama_kota}", use_container_width=True):
                    st.session_state.selected_city = nama_kota

        st.divider()

        # 4. DETAIL DRILL-DOWN (Setelah Kota Diklik)
        pilihan = st.session_state.selected_city
        st.subheader(f"🔍 Detail Analisis: {pilihan}")
        
        # Filter data hanya untuk kota yang dipilih
        df_target = df[df['kota_kabupaten'] == pilihan]
        
        # Hitung jumlah per kecamatan di dalam kota tersebut
        kec_stats = df_target.groupby('kecamatan').size().reset_index(name='Jumlah Titik')
        kec_stats = kec_stats.sort_values(by='Jumlah Titik', ascending=True)

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.write(f"Daftar Kecamatan di **{pilihan}** dari yang paling sedikit WiFi:")
            st.dataframe(kec_stats, use_container_width=True)

        with col_right:
            # Mengambil kecamatan teratas (paling minim)
            kec_rekomendasi = kec_stats.iloc[0]['kecamatan']
            st.success("### ✅ Rekomendasi Lokasi")
            st.write(f"Berdasarkan data, **Kecamatan {kec_rekomendasi}** adalah prioritas utama untuk pemasangan WiFi baru.")
            st.info(f"Wilayah ini hanya memiliki {kec_stats.iloc[0]['Jumlah Titik']} titik akses terdaftar.")

    # --- HALAMAN LAINNYA ---
    elif menu == "🏠 Beranda Utama":
        st.title("🏠 Beranda Utama")
        st.metric("Total Data WiFi Jabar", len(df))

    elif menu == "📋 Tampilkan Semua Data":
        st.title("📋 Database")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")