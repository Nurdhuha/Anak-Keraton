# Import additional libraries needed for interactive tables
import streamlit as st
import pandas as pd
import json
from sklearn.naive_bayes import GaussianNB
from pymongo import MongoClient
import certifi

# Load CSV data
def load_csv_data():
    bahan_pangan = pd.read_csv('data/BAHAN PANGAN.csv', skiprows=1)
    porsi_diet = pd.read_csv('data/PEDOMAN PORSI DIET.csv', skiprows=1)
    return bahan_pangan, porsi_diet

# Load JSON data for local foods
def load_json_data():
    with open('data/datapanganlokal.json') as json_file:
        pangan_lokal = json.load(json_file)
    return pangan_lokal

# Load JSON data for diet recommendations
def load_rekomendasi_menu():
    with open('data/rekomendasi_menu.json') as json_file:
        rekomendasi_menu = json.load(json_file)
    return rekomendasi_menu

# Get database connection
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

# Train Naive Bayes model
def train_naive_bayes(data):
    X = data[['berat', 'kalori', 'protein', 'karbohidrat']].values
    y = data['kategori'].values
    model = GaussianNB()
    model.fit(X, y)
    return model

# Display diet recommendations
def display_diet_recommendations(diet_group, local_foods):
    if diet_group == "I":
        rekomendasi_menu = load_rekomendasi_menu()
        st.subheader("Rekomendasi Menu")
        if any(item["golongan"] == diet_group for item in rekomendasi_menu):
            df_rekomendasi = pd.DataFrame([item for item in rekomendasi_menu if item['golongan'] == diet_group])
            st.dataframe(df_rekomendasi[['waktu_makan', 'menu', 'total_kalori_kkal']])
        else:
            st.error("Kolom 'golongan' tidak ditemukan di data rekomendasi menu.")
    else:
        st.error("Menu diet masih dikembangkan")

    st.subheader("Bahan Pangan Lokal")
    for province, foods in local_foods.items():
        st.markdown(f"### {province}")
        for category, items in foods.items():
            st.markdown(f"**{category}**")
            for item in items:
                st.write(item)

# Main function to run the app
def main():
    st.title("Rekomendasi Pola Diet")

    if "user_data" not in st.session_state:
        st.error("Silakan lakukan login terlebih dahulu!")
        st.switch_page("streamlit_app.py")
        st.stop()

    nama_pasien = st.session_state["user_data"]["username"]
    user_data = get_user_data(nama_pasien)

    if user_data:
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

        local_foods = load_json_data()
        display_diet_recommendations(diet_group, local_foods)
    else:
        st.error("Data pengguna tidak ditemukan.")

if __name__ == "__main__":
    main()
