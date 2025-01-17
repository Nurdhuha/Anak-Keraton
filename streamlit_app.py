import json
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Sign Up - Rekomendasi Diet Diabetes", page_icon=":lock:")
# Path to the JSON file for storing user data
DATA_FILE = Path("./data/datapasien.json")

# Function to load user data
def load_user_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save user data
def save_user_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to handle user actions
def handle_user_action():
    st.subheader("Masukkan Informasi Akun Anda")
    username = st.text_input("Masukkan username")
    password = st.text_input("Masukkan password", type="password")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Sign Up"):
            if username and password:
                user_data = load_user_data()
                if username in user_data:
                    st.error("Username telah digunakan, gunakan username lain.")
                else:
                    user_data[username] = password
                    save_user_data(user_data)
                    st.success("Sign Up sukses.")
            else:
                st.error("Silakan masukkan username dan password.")

    with col2:
        if st.button("Login"):
            if username and password:
                user_data = load_user_data()
                if username not in user_data:
                    st.error("Username tidak ditemukan. Silakan Sign Up terlebih dahulu.")
                elif user_data[username] != password:
                    st.error("Password salah. Silakan coba lagi.")
                else:
                    st.success("Login berhasil!")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.switch_page("menu_input_data")
            else:
                st.error("Silakan masukkan username dan password.")

# Main function to display the menu
def main_menu():
    st.title("Diet Recommendation Website")
    handle_user_action()

if __name__ == "__main__":
    main_menu()
