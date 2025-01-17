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

# Function to handle user sign up
def sign_up():
    st.subheader("Sign Up")
    username = st.text_input("Masukkan username")
    password = st.text_input("Masukkan password", type="password")
    
    if st.button("Sign Up"):
        if username and password:
            user_data = load_user_data()
            if username in user_data:
                st.error("Username telah digunakan, gunakan username lain.")
            else:
                user_data[username] = password
                save_user_data(user_data)
                st.success("Sign Up sukses.")
                st.switch_page("pages/menu_input_data.py")
        else:
            st.error("Please provide both username and password.")

# Main function to display the sign-up menu
def main_menu():
    st.title("Diet Recommendation Website")
    sign_up()

if __name__ == "__main__":
    main_menu()
