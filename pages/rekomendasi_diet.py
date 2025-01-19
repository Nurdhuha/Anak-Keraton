import streamlit as st
from pymongo import MongoClient
import certifi
import pandas as pd

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

def get_diet_group(energy):
    if energy < 1200:
        return "I"
    elif 1200 <= energy <= 1400:
        return "II"
    elif 1401 <= energy <= 1600:
        return "III"
    elif 1601 <= energy <= 1800:
        return "IV"
    elif 1801 <= energy <= 2000:
        return "V"
    elif 2001 <= energy <= 2200:
        return "VI"
    elif 2201 <= energy <= 2400:
        return "VII"
    else:
        return "VIII"
        
def load_csv_data():
    bahan_pangan = pd.read_csv('data/BAHAN PANGAN.csv', skiprows=1)
    porsi_diet = pd.read_csv('data/PEDOMAN PORSI DIET.csv', skiprows=1)
    rekomendasi_menu = pd.read_csv('data/REKOMENDASI MENU.csv', skiprows=1)
    return bahan_pangan, porsi_diet, rekomendasi_menu

def display_diet_recommendations(diet_group):
    _, porsi_diet, rekomendasi_menu = load_csv_data()
    
    st.subheader("Pedoman Porsi Diet")
    st.dataframe(porsi_diet[['GOLONGAN', diet_group]])

    st.subheader("Rekomendasi Menu")
    st.dataframe(rekomendasi_menu[rekomendasi_menu['GOLONGAN'] == diet_group])

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
    diet_group = get_diet_group(kebutuhan_kalori)

    st.markdown(f"### Kebutuhan Kalori Harian Anda: {kebutuhan_kalori:.2f} kkal")
    st.markdown(f"### Kelompok Diet Anda: {diet_group}")

    display_diet_recommendations(diet_group)
else:
    st.error("Data pengguna tidak ditemukan.")
