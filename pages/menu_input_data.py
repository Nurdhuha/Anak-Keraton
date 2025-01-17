import streamlit as st
import json
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(page_title="Input Data Pasien - Rekomendasi Diet Diabetes", page_icon="📋")

# Cek status login dari parameter URL
params = st.experimental_get_query_params()
if 'login_success' not in params or 'nama' not in params:
    st.error("Silakan login terlebih dahulu!")
    st.stop()

# Tampilkan sambutan
nama_pasien = params['nama'][0]
st.title(f"Selamat Datang, {nama_pasien}!")
st.subheader("Form Input Data Pasien")

# Buat form untuk input data
with st.form("form_input_data"):
    # Data Demografi
    st.markdown("### Data Demografi")
    col1, col2 = st.columns(2)
    
    with col1:
        usia = st.number_input("Usia (tahun)", min_value=0, max_value=120)
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        
    with col2:
        alamat = st.text_area("Alamat")
        no_telepon = st.text_input("Nomor Telepon")

    # Data Klinis
    st.markdown("### Data Klinis")
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
                "berat_badan": berat_badan,
                "tinggi_badan": tinggi_badan,
                "tingkat_aktivitas": tingkat_aktivitas,
                "kondisi_kesehatan": kondisi_kesehatan
            },
            "preferensi_makanan": {
                "pantangan": pantangan_makanan,
                "preferensi_diet": preferensi_diet,
                "catatan_tambahan": catatan_tambahan
            }
        }

        # Simpan ke file JSON
        try:
            with open("Database/data_pasien_detail.json", "a") as f:
                json.dump(data_pasien, f)
                f.write('\n')  # Tambahkan newline untuk JSONL format
            st.success("Data berhasil disimpan!")
            
            # Tampilkan BMI
            bmi = berat_badan / ((tinggi_badan/100) ** 2)
            st.info(f"BMI Anda: {bmi:.1f}")
            
            # Kategorisasi BMI
            if bmi < 18.5:
                st.warning("Kategori: Berat Badan Kurang")
            elif 18.5 <= bmi < 25:
                st.success("Kategori: Berat Badan Normal")
            elif 25 <= bmi < 30:
                st.warning("Kategori: Berat Badan Berlebih")
            else:
                st.error("Kategori: Obesitas")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan saat menyimpan data: {e}")