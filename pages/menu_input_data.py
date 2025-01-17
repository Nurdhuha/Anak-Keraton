import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import os

# Konfigurasi halaman
st.set_page_config(page_title="Input Data Pasien - Rekomendasi Diet Diabetes", page_icon="📋")

# Path ke file JSON untuk menyimpan data pasien
data_file_path = Path("data/data_detail_pasien.json")

# Fungsi untuk memuat data pengguna dari sesi
if "user_data" not in st.session_state:
    st.error("Silakan lakukan login terlebih dahulu!")
    st.switch_page("streamlit_app.py")
    st.stop()

# Fungsi untuk menyimpan data ke JSON
def save_to_json(data_pasien):
    try:
        # Pastikan direktori data ada
        os.makedirs(data_file_path.parent, exist_ok=True)
        
        # Baca data yang sudah ada atau inisialisasi list baru
        existing_data = []
        if data_file_path.exists():
            try:
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []
            except json.JSONDecodeError:
                existing_data = []
        
        # Tambahkan data baru
        existing_data.append(data_pasien)
        
        # Simpan semua data ke file dengan encoding UTF-8
        with open(data_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menyimpan data: {str(e)}")
        return False

# Inisialisasi state
if 'data_saved' not in st.session_state:
    st.session_state.data_saved = False

# Tampilkan sambutan
nama_pasien = st.session_state["user_data"]["username"]
st.title(f"Selamat Datang, {nama_pasien}!")
st.subheader("Form Input Data Pasien")

# Form untuk input data
form = st.form("form_input_data")

# Data Demografi
form.markdown("### Data Demografi")
col1, col2 = form.columns(2)

with col1:
    usia = form.number_input("Usia (tahun)", min_value=0, max_value=120)
    jenis_kelamin = form.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])

with col2:
    alamat = form.text_area("Alamat")
    no_telepon = form.text_input("Nomor Telepon")

# Data Antropometri
form.markdown("### Data Antropometri")
col3, col4 = form.columns(2)

with col3:
    berat_badan = form.number_input("Berat Badan (kg)", min_value=0.0)
    tinggi_badan = form.number_input("Tinggi Badan (cm)", min_value=0.0)

with col4:
    tingkat_aktivitas = form.select_slider(
        "Tingkat Aktivitas",
        options=["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
    )

kondisi_kesehatan = form.multiselect(
    "Kondisi Kesehatan Lain",
    ["Hipertensi", "Kolesterol Tinggi", "Penyakit Jantung", "Gangguan Ginjal", "Tidak Ada"]
)

# Preferensi Makanan
form.markdown("### Preferensi Makanan")
col5, col6 = form.columns(2)

with col5:
    pantangan_makanan = form.multiselect(
        "Pantangan Makanan",
        ["Seafood", "Daging Merah", "Kacang-kacangan", "Dairy", "Tidak Ada"]
    )

with col6:
    preferensi_diet = form.multiselect(
        "Preferensi Diet",
        ["Vegetarian", "Vegan", "Bebas Gluten", "Rendah Karbohidrat", "Normal"]
    )

catatan_tambahan = form.text_area("Catatan Tambahan")

# Tombol Submit
submitted = form.form_submit_button("Simpan Data")

# Hanya proses data jika tombol submit ditekan
if submitted:
    # Validasi data minimal
    if not usia or not jenis_kelamin or not berat_badan or not tinggi_badan:
        st.error("Mohon lengkapi data usia, jenis kelamin, berat badan, dan tinggi badan!")
    else:
        # Buat dictionary data pasien setelah validasi berhasil
        data_pasien = {
            "nama": nama_pasien,
            "tanggal_input": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "demografi": {
                "usia": usia,
                "jenis_kelamin": jenis_kelamin,
                "alamat": alamat,
                "no_telepon": no_telepon
            },
            "data_klinis": {
                "berat_badan": float(berat_badan),
                "tinggi_badan": float(tinggi_badan),
                "tingkat_aktivitas": tingkat_aktivitas,
                "kondisi_kesehatan": kondisi_kesehatan
            },
            "preferensi_makanan": {
                "pantangan": pantangan_makanan,
                "preferensi_diet": preferensi_diet,
                "catatan_tambahan": catatan_tambahan
            }
        }

        # Simpan data hanya jika tombol submit ditekan dan validasi berhasil
        if save_to_json(data_pasien):
            st.success("Data berhasil disimpan!")
            st.session_state.data_saved = True

            # Hitung dan tampilkan IMT setelah data berhasil disimpan
            if berat_badan > 0 and tinggi_badan > 0:
                imt = berat_badan / ((tinggi_badan/100) ** 2)
                st.info(f"IMT Anda: {imt:.1f}")

                # Kategorisasi IMT
                if imt < 18.5:
                    st.warning("Kategori: Berat Badan Kurang")
                elif 18.5 <= imt < 23:
                    st.success("Kategori: Berat Badan Normal")
                elif 23 <= imt < 25:
                    st.warning("Kategori: Berat Badan Berlebih, Beresiko Obesitas")
                elif 25 <= imt < 30:
                    st.warning("Kategori: Obesitas Tingkat 1")
                else:
                    st.error("Kategori: Obesitas Tingkat 2")

# Tampilkan tombol rekomendasi hanya jika data telah disimpan
if st.session_state.data_saved:
    if st.button("Lihat Rekomendasi Pola Diet", type="primary"):
        st.info("Fitur rekomendasi pola diet sedang dalam pengembangan. Silakan tunggu update selanjutnya.")

# Tombol logout
if st.sidebar.button("Logout"):
    del st.session_state["user_data"]
    st.switch_page("streamlit_app.py")
