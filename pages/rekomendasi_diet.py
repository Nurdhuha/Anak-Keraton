# Import additional libraries needed for interactive tables
import streamlit as st
import pandas as pd
import json
from sklearn.naive_bayes import GaussianNB

# Load CSV data
def load_csv_data():
    bahan_pangan = pd.read_csv('data/BAHAN PANGAN.csv', skiprows=1)
    porsi_diet = pd.read_csv('data/PEDOMAN PORSI DIET.csv', skiprows=1)
    rekomendasi_menu = pd.read_csv('data/REKOMENDASI MENU.csv', skiprows=1)
    return bahan_pangan, porsi_diet, rekomendasi_menu

# Load JSON data for local foods
def load_json_data():
    with open('data/datapanganlokal.json') as json_file:
        pangan_lokal = json.load(json_file)
    return pangan_lokal
    
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
        
# Train Naive Bayes model
def train_naive_bayes(data):
    X = data[['berat', 'kalori', 'protein', 'karbohidrat']].values
    y = data['kategori'].values
    model = GaussianNB()
    model.fit(X, y)
    return model

# Display diet recommendations
def display_diet_recommendations(diet_group, local_foods):
    _, porsi_diet, rekomendasi_menu = load_csv_data()
    
    st.subheader("Pedoman Porsi Diet")
    st.dataframe(porsi_diet[['GOLONGAN', diet_group]])

    st.subheader("Rekomendasi Menu")
    st.dataframe(rekomendasi_menu[rekomendasi_menu['GOLONGAN'] == diet_group])

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
