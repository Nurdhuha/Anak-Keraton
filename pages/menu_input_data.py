import streamlit as st 
import pandas as pd
from datetime import datetime
from pathlib import Path

# Konfigurasi halaman
st.set_page_config(page_title="Input Data Pasien - Rekomendasi Diet Diabetes", page_icon="📋")

# Path ke file CSV
csv_path = Path("data/datapasien.csv")

# Fungsi untuk memuat data pengguna dari sesi
if "user_data" not in st.session_state:
    st.error("Silakan lakukan login terlebih dahulu!")
    st.switch_page("streamlit_app.py")
    st.stop()

# Fungsi untuk menyimpan data ke CSV
def save_to_csv(data_pasien):
    try:
        # Flattenkan data untuk format CSV
        flat_data = {
            'nama': data_pasien['nama'],
            'tanggal_input': data_pasien['tanggal_input'],
            'usia': data_pasien['demografi']['usia'],
            'jenis_kelamin': data_pasien['demografi']['jenis_kelamin'],
            'alamat': data_pasien['demografi']['alamat'],
            'no_telepon': data_pasien['demografi']['no_telepon'],
            'berat_badan': data_pasien['data_klinis']['berat_badan'],
            'tinggi_badan': data_pasien['data_klinis']['tinggi_badan'],
            'tingkat_aktivitas': data_pasien['data_klinis']['tingkat_aktivitas'],
            'kondisi_kesehatan': ';'.join(data_pasien['data_klinis']['kondisi_kesehatan']),
            'pantangan_makanan': ';'.join(data_pasien['preferensi_makanan']['pantangan']),
            'preferensi_diet': ';'.join(data_pasien['preferensi_makanan']['preferensi_diet']),
            'catatan_tambahan': data_pasien['preferensi_makanan']['catatan_tambahan']
        }
        
        # Buat DataFrame baru
        new_df = pd.DataFrame([flat_data])
        
        # Jika file sudah ada, append data
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = new_df
            
        # Pastikan direktori ada
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Simpan ke CSV
        df.to_csv(csv_path, index=False)
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
with st.form("form_input_data", clear_on_submit=False):
    # Data Demografi
    st.markdown("### Data Demografi")
    col1, col2 = st.columns(2)

    with col1:
        usia = st.number_input("Usia (tahun)", min_value=0, max_value=120)
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])

    with col2:
        alamat = st.text_area("Alamat")
        no_telepon = st.text_input("Nomor Telepon")

    # Data Antropometri
    st.markdown("### Data Antropometri")
    col3, col4 = st.columns(2)

    with col3:
        berat_badan = st.number_input("Berat Badan (kg)", min_value=0.0)
        tinggi_badan = st.number_input("Tinggi Badan (cm)", min_value=0.0)

    with col4:
        tingkat_aktivitas = st.select_slider(
            "Tingkat Aktivitas",
            options=["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
        )

    kondisi_kesehatan = st.multiselect(
        "Kondisi Kesehatan Lain",
        ["Hipertensi", "Kolesterol Tinggi", "Penyakit Jantung", "Gangguan Ginjal", "Tidak Ada"]
    )

    # Preferensi Makanan
    st.markdown("### Preferensi Makanan")
    col5, col6 = st.columns(2)

    with col5:
        pantangan_makanan = st.multiselect(
            "Pantangan Makanan",
            ["Seafood", "Daging Merah", "Kacang-kacangan", "Dairy", "Tidak Ada"]
        )

    with col6:
        preferensi_diet = st.multiselect(
            "Preferensi Diet",
            ["Vegetarian", "Vegan", "Bebas Gluten", "Rendah Karbohidrat", "Normal"]
        )

    catatan_tambahan = st.text_area("Catatan Tambahan")

    # Tombol Submit
    submitted = st.form_submit_button("Simpan Data")

    if submitted:
        # Validasi data minimal
        if not usia or not jenis_kelamin or not berat_badan or not tinggi_badan:
            st.error("Mohon lengkapi data usia, jenis kelamin, berat badan, dan tinggi badan!")
        else:
            # Buat dictionary data pasien
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

            # Simpan data
            if save_to_csv(data_pasien):
                st.success("Data berhasil disimpan!")
                st.session_state.data_saved = True

                # Tampilkan IMT
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

# Tampilkan tombol rekomendasi jika data telah disimpan
if st.session_state.data_saved:
    if st.button("Lihat Rekomendasi Pola Diet", type="primary"):
        st.info("Fitur rekomendasi pola diet sedang dalam pengembangan. Silakan tunggu update selanjutnya.")

# Tombol logout
if st.sidebar.button("Logout"):
    del st.session_state["user_data"]
    st.switch_page("streamlit_app.py")
