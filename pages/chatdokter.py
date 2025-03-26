import streamlit as st
import time
import random
import re

st.set_page_config(
    page_title="Melimeal-Diet Recommendation Website", 
    page_icon="🍎",
    initial_sidebar_state="collapsed"
)

# Sidebar informatif
with st.sidebar:
    st.header("📌 Panduan Diabetes")
    st.markdown("""
    **Prinsip Diet Diabetes:**
    1. Kontrol asupan karbohidrat
    2. Tingkatkan serat makanan
    3. Hindari makanan mengandung gula tinggi
    4. Makan teratur 3x utama + 2x selingan
  
    
    **Contoh Pertanyaan:**
    - Dok, berapa porsi karbohidrat yang boleh saya makan?
    - Dok, apakah nasi merah baik untuk diabetes?
    - Bagaimana pola makan yang tepat untuk saya?
    - Apakah saya boleh makan buah durian?
    - Berapa kali saya harus makan dalam sehari?
    """)
    st.divider()
   
# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header aplikasi
st.title("🍽️ Konsultasi Diet Diabetes")
st.caption("dr. Kinanti Rizky Putri")

# Tampilkan riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(f"**Anda:** {message['content']}")
    else:
        st.chat_message("user").write(f"**dr. Kinan:** {message['content']}")


def get_doctor_response(user_input):
    user_input = user_input.lower()
    
    responses = {
        r'porsi|takaran': "Baik, untuk porsi karbohidrat yang aman, saya sarankan sekitar 45-60 gram per makan utama. Ini bisa berupa 100 gram nasi merah atau setara dengan satu ubi ukuran sedang.",
        r'nasi|karbo': "Saya menyarankan Anda untuk lebih memilih nasi merah dibandingkan nasi putih karena memiliki indeks glikemik yang lebih rendah.",
        r'buah|fruit': "Untuk buah, Anda bisa mengonsumsi apel, jeruk, pepaya, dan buah naga dalam porsi yang sesuai. Namun, sebaiknya hindari durian, mangga, rambutan, dan sawo karena kandungan gulanya tinggi.",
        r'makan malam|dinner': "Untuk makan malam, coba konsumsi nasi merah 100gr, ikan bakar, sayur rebus, dan sepotong pepaya. Ini seimbang dan tetap menjaga kadar gula darah Anda.",
        r'menu|contoh': "Contoh menu harian untuk Anda:\nSarapan: Oatmeal + telur rebus + brokoli\nSelingan: Yoghurt tanpa gula\nMakan Siang: Nasi merah + tempe bacem + tumis kangkung\nSelingan: 1 potong apel\nMakan Malam: Nasi merah + ikan bakar + sayur rebus",
        r'indeks glikemik': "Indeks Glikemik (GI) mengukur seberapa cepat makanan meningkatkan kadar gula darah. Pilih makanan dengan GI rendah (<55) untuk mengontrol diabetes lebih baik."
    }
    
    for pattern, response in responses.items():
        if re.search(pattern, user_input):
            return response
    
    return "Maaf, saya perlu lebih banyak informasi. Bisa Anda jelaskan lebih rinci mengenai pertanyaan Anda?"

# Input pengguna
if prompt := st.chat_input("Tulis pertanyaan Anda..."):
    # Tambahkan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Simulasi dokter berpikir
    with st.chat_message("user"):
        typing_message = st.empty()
        typing_message.write("dr. Kinan sedang mengetik...")
        time.sleep(1.5) 
        
        # Dapatkan respons dokter
        response = get_doctor_response(prompt)
        typing_message.write(f"**dr. Kinan:** {response}")
    
    # Simpan riwayat chat
    st.session_state.messages.append({"role": "assistant", "content": response})
