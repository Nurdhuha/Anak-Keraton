import streamlit as st
from pymongo import MongoClient
import certifi

# Konfigurasi halaman
st.set_page_config(page_title="Rekomendasi Pola Diet", page_icon="🍽️")

def get_database():
    try:
        connection_string = "mongodb+srv://nurdhuhaam:Nurdhuha123@cluster0.ec5z7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
        client.server_info()
        return client['Database_Dhuha']
    except Exception as e:
        st.error(f"Gagal membuat koneksi database: {str(e)}")
        return None

def get_user_data(name):
    try:
        db = get_database()
        if db is None:
            return None
        collection = db['data_pasien']
        user_data = collection.find_one({"nama": name})
        return user_data
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {str(e)}")
        return None

def calculate_bmr(weight, height, gender):
    if gender == "Laki-laki":
        return 30 * weight
    else:
        return 25 * weight

def calculate_energy(age, bmr, activity_level):
    activity_factor = {
        "Sangat Rendah": 0.1,
        "Rendah": 0.2,
        "Sedang": 0.3,
        "Tinggi": 0.4,
        "Sangat Tinggi": 0.5
    }.get(activity_level, 0)

    age_factor = 0
    if 40 <= age < 60:
        age_factor = 0.05
    elif 60 <= age < 70:
        age_factor = 0.1
    elif age >= 70:
        age_factor = 0.15

    return (bmr * (1 + activity_factor)) - (bmr * age_factor)

if "user_data" not in st.session_state:
    st.error("Silakan lakukan login terlebih dahulu!")
    st.switch_page("streamlit_app.py")
    st.stop()

nama_pasien = st.session_state["user_data"]["username"]
user_data = get_user_data(nama_pasien)

if user_data:
    st.title(f"Rekomendasi Pola Diet untuk {nama_pasien}")
    
    berat_badan = user_data["data_antropometri"]["berat_badan"]
    tinggi_badan = user_data["data_antropometri"]["tinggi_badan"]
    usia = user_data["demografi"]["usia"]
    jenis_kelamin = user_data["demografi"]["jenis_kelamin"]
    tingkat_aktivitas = user_data["data_aktivitas_kesehatan"]["tingkat_aktivitas"]

    imt = berat_badan / ((tinggi_badan / 100) ** 2)

    if imt < 18.5:
        berat_digunakan = berat_badan
    else:
        berat_digunakan = 0.9 * (tinggi_badan - 100)

    bmr = calculate_bmr(berat_digunakan, tinggi_badan, jenis_kelamin)
    kebutuhan_kalori = calculate_energy(usia, bmr, tingkat_aktivitas)

    st.markdown(f"### Kebutuhan Kalori Harian Anda: {kebutuhan_kalori:.2f} kkal")
else:
    st.error("Data pengguna tidak ditemukan.")
