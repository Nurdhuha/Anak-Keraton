import json
import streamlit as st
from pathlib import Path



st.set_page_config(
    page_title="Melimeal-Diet Recommendation Website", 
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = Path("data/datapasien.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# Function untuk memuat data pengguna
def load_user_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                st.error("File datapasien.json tidak valid. Periksa format file JSON.")
                return []
    return []

# Function untuk menyimpan data pengguna
def save_user_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function untuk mencari pengguna berdasarkan username
def find_user(username, user_data):
    for user in user_data:
        if user["username"] == username:
            return user
    return None

# Function untuk menangani aksi pengguna
def handle_user_action():
    st.subheader("Silahkan Verifikasi Akun Anda")
    username = st.text_input("Masukkan username")
    password = st.text_input("Masukkan password", type="password")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Sign Up"):
            if username and password:
                user_data = load_user_data()
                if find_user(username, user_data):
                    st.error("Username telah digunakan, gunakan username lain.")
                else:
                    user_data.append({"username": username, "password": password})
                    save_user_data(user_data)
                    st.success("Sign Up sukses. Silakan login.")
            else:
                st.error("Silakan masukkan username dan password.")
    
    with col2:
        if st.button("Login"):
            if username and password:
                user_data = load_user_data()
                user = find_user(username, user_data)
                if not user:
                    st.error("Username tidak ditemukan. Silakan Sign Up terlebih dahulu.")
                elif user["password"] != password:
                    st.error("Password salah. Silakan coba lagi.")
                else:
                    st.success("Login berhasil!")
                    # Simpan data user ke session state
                    st.session_state["user_data"] = {
                        "username": username,
                        "password": password
                    }
                    # Pindah ke halaman input data
                    st.switch_page("pages/menu_input_data.py")
            else:
                st.error("Silakan masukkan username dan password.")

# Main function
def main():
    st.title("Diet Recommendation Website")
    handle_user_action()

if __name__ == "__main__":
    main()
