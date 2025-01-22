import streamlit as st
import pandas as pd
import json
from sklearn.naive_bayes import GaussianNB
from pymongo import MongoClient
import certifi

# Load CSV data
def load_csv_data(file_path):
    return pd.read_csv(file_path, skiprows=1)

# Load JSON data
def load_json_data(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)

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
def train_naive_bayes(data, food_preferences, pantangan_makanan, preferensi_diet, kondisi_kesehatan):
    # Tambahkan fitur baru ke dalam data pelatihan
    X = data[['berat', 'kalori', 'protein', 'karbohidrat', 'pantangan_makanan', 'preferensi_diet', 'kondisi_kesehatan']].values
    y = data['kategori'].values
    model = GaussianNB()
    model.fit(X, y)
    
    # Integrate food preferences
    if food_preferences:
        for preference in food_preferences:
            preference_data = [
                preference['berat'],
                preference['kalori'],
                preference['protein'],
                preference['karbohidrat'],
                pantangan_makanan,
                preferensi_diet,
                kondisi_kesehatan
            ]
            model.partial_fit([preference_data], [preference['kategori']])
    
    return model

# Display diet recommendations
def display_diet_recommendations(diet_group, porsi_diet, pantangan_makanan, preferensi_diet, kondisi_kesehatan):
    rekomendasi_menu = load_rekomendasi_menu()
    st.subheader("Rekomendasi Menu")
    
    # Filter menu berdasarkan pantangan makanan, preferensi diet, dan kondisi kesehatan
    filtered_menu = [item for item in rekomendasi_menu if item['Golongan'] == diet_group and 
                     item['menu'] not in pantangan_makanan and 
                     ('diet' not in item or item['diet'] in preferensi_diet) and 
                     ('kondisi_kesehatan' not in item or item['kondisi_kesehatan'] in kondisi_kesehatan)]
    
    if filtered_menu:
        df_rekomendasi = pd.DataFrame(filtered_menu)
        df_rekomendasi = df_rekomendasi[['waktu_makan', 'menu', 'total_kalori_kkal']]
        total_kalori = df_rekomendasi['total_kalori_kkal'].sum()
        df_rekomendasi.loc['Total'] = ['-', '-', total_kalori]
        st.dataframe(df_rekomendasi)
    else:
        st.error("Tidak ada rekomendasi menu yang sesuai dengan kriteria Anda.")

    st.subheader("Panduan Porsi Diet")
    df_porsi = pd.DataFrame([item for item in porsi_diet if item['Golongan'] == diet_group])
    if not df_porsi.empty:
        df_porsi = df_porsi.drop(columns=['Golongan'])
        st.dataframe(df_porsi)
    else:
        st.error("Kolom 'golongan' tidak ditemukan di data panduan porsi diet.")

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

        porsi_diet = load_porsi_diet()
        display_diet_recommendations(diet_group, porsi_diet, pantangan_makanan, preferensi_diet, kondisi_kesehatan)
    else:
        st.error("Data pengguna tidak ditemukan.")

if __name__ == "__main__":
    main()
