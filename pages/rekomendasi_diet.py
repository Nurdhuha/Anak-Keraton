import streamlit as st
import pandas as pd
import json
from sklearn.naive_bayes import GaussianNB
from pymongo import MongoClient
import certifi
from menuclassifier import generate_menu_recommendations, display_recommendations
from kelompokdiet import get_diet_group, calculate_bmr, calculate_energy, calculate_bmi

st.set_page_config(page_title="Rekomendasi- Rekomendasi Diet Diabetes", page_icon="📋")

# Load JSON data for diet recommendations
def load_rekomendasi_menu():
    with open('data/rekomendasi_menu.json') as json_file:
        rekomendasi_menu = json.load(json_file)
    return rekomendasi_menu

# Load JSON data for diet portions
def load_porsi_diet():
    with open('data/pedoman_porsi_diet.json') as json_file:
        porsi_diet = json.load(json_file)
    return porsi_diet

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

def display_diet_recommendations(diet_group, porsi_diet, pantangan_makanan, preferensi_diet, kondisi_kesehatan, user_data):
    
    # Tampilkan rekomendasi menu menggunakan Naive Bayes
    recommendations = generate_menu_recommendations(user_data)
    display_recommendations(recommendations, pantangan_makanan, preferensi_diet)
    
    st.subheader("Panduan Porsi Diet")
    df_porsi = pd.DataFrame([item for item in porsi_diet if item['Golongan'] == diet_group])
    if not df_porsi.empty:
        columns_order = ['Waktu Makan', 'Karbohidrat', 'Protein Hewani', 'Protein Nabati', 'Sayuran A', 'Sayuran B', 'Buah', 'Susu', 'Minyak']
        df_porsi = df_porsi[columns_order]
        
        # Fill NA/null values with "-"
        df_porsi = df_porsi.fillna("-")
        
        # Convert numeric columns to string and replace empty strings with "-"
        for col in df_porsi.columns:
            if col != 'Waktu Makan':
                df_porsi[col] = df_porsi[col].astype(str).replace({"nan": "-", "": "-"})
        
        if 'Golongan' in df_porsi.columns:
            df_porsi = df_porsi.drop(columns=["Golongan"])
        st.dataframe(df_porsi)
    else:
        st.error("Kolom 'Golongan' tidak ditemukan di data panduan porsi diet.")

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
        food_preferences = user_data.get("preferensi_makanan", {})
        pantangan_makanan = user_data["preferensi_makanan"]["pantangan"]
        preferensi_diet = user_data["preferensi_makanan"]["preferensi_diet"]
        kondisi_kesehatan = user_data["data_aktivitas_kesehatan"]["kondisi_kesehatan"]

        weight_status = calculate_bmi(berat_badan, tinggi_badan)
        if weight_status is None:
            st.error("Berat badan atau tinggi badan tidak valid")
            return

        if weight_status == "Kurang":
            berat_digunakan = berat_badan
        else:
            berat_digunakan = 0.9 * (tinggi_badan - 100)

        bmr = calculate_bmr(berat_digunakan, tinggi_badan, jenis_kelamin)
        kebutuhan_kalori = calculate_energy(usia, bmr, tingkat_aktivitas, weight_status)
        diet_group = get_diet_group(kebutuhan_kalori)

        st.markdown(f"### Kebutuhan Kalori Harian Anda: {kebutuhan_kalori:.2f} kkal")
        st.markdown(f"### Kelompok Diet Anda: {diet_group}")

        porsi_diet = load_porsi_diet()
        display_diet_recommendations(diet_group, porsi_diet, pantangan_makanan, preferensi_diet, kondisi_kesehatan, user_data)
    else:
        st.error("Data pengguna tidak ditemukan.")

if __name__ == "__main__":
    main()
