import streamlit as st
import time
import random

# Konfigurasi halaman
st.set_page_config(page_title="Diabetes Nutrition Chat", page_icon="🩸")

# CSS kustom
st.markdown("""
<style>
    .chat-container {
        max-width: 800px;
        margin: auto;
        padding: 20px;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .doctor-message {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar informatif
with st.sidebar:
    st.header("📌 Panduan Diabetes")
    st.markdown("""
    **Prinsip Diet Diabetes:**
    1. Kontrol asupan karbohidrat
    2. Tingkatkan serat makanan
    3. Hindari makanan bergula tinggi
    4. Makan teratur 3x utama + 2x selingan
    5. Monitor indeks glikemik makanan
    
    **Contoh Pertanyaan:**
    - Berapa porsi karbohidrat yang boleh saya makan?
    - Apakah nasi merah baik untuk diabetes?
    - Bagaimana pola makan yang tepat untuk diabetes?
    - Bolehkah makan buah durian?
    - Berapa kali saya harus makan dalam sehari?
    """)
    st.divider()
    st.markdown("**Disclaimer:**\n*Konsultasikan dengan dokter/nutrisionis untuk rencana makan personal*")

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header aplikasi
st.title("🍽️ Konsultasi Diet Diabetes")
st.caption("Chatbot Edukasi Pola Makan untuk Penderita Diabetes Melitus")

# Tampilkan riwayat chat
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='user-message'>👤 **Anda:** {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='doctor-message'>🩺 **Nutrisionis:** {message['content']}</div>", unsafe_allow_html=True)

# Fungsi respons spesialis diabetes
def get_diabetes_response(user_input):
    user_input = user_input.lower()
    
    # Database pengetahuan
    food_db = {
        'nasi': {
            'response': "Pilih nasi merah (GI 50) daripada nasi putih (GI 73). Porsi maksimal 100gr (1 centong)",
            'gi': {'putih': 73, 'merah': 50}
        },
        'buah': {
            'safe': ["apel", "jeruk", "pepaya", "buah naga"],
            'avoid': ["durian", "mangga", "rambutan", "sawo"],
            'portion': "1 porsi = 1 potong sedang (150gr)"
        },
        'karbohidrat': {
            'daily': "45-60gr per makan utama",
            'sources': ["beras merah", "quinoa", "ubi", "oatmeal"]
        },
        'protein': {
            'recommendation': "Pilih protein rendah lemak: ikan, tahu, tempe, dada ayam"
        }
    }

    # Pola respons
    patterns = {
    r'porsi|takaran': f"Porsi karbohidrat harian: {food_db['karbohidrat']['daily']}. Contoh sumber: {', '.join(food_db['karbohidrat']['sources'])}",
    r'nasi|karbo': food_db['nasi']['response'],
    r'buah|fruit': f"Buah aman: {', '.join(food_db['buah']['safe'])}. Hindari: {', '.join(food_db['buah']['avoid'])}. {food_db['buah']['portion']}",
    r'makan malam|dinner': "Contoh makan malam: 100gr nasi merah + 100gr ikan bakar + 1 mangkok sayur rebus + 1 potong pepaya",
    r'menu|contoh': "Contoh menu harian:\nSarapan: Oatmeal + telur rebus + brokoli\nSelingan: Yoghurt tanpa gula\nMakan Siang: Nasi merah + tempe bacem + tumis kangkung\nSelingan: 1 potong apel\nMakan Malam: Nasi merah + ikan bakar + sayur rebus",
    r'indeks glikemik': "Indeks Glikemik (GI) mengukur kecepatan makanan meningkatkan gula darah. Pilih makanan GI rendah (<55)"
}

    # Cocokkan pertanyaan
    for pattern, response in patterns.items():
        if re.search(pattern, user_input):
            return response
    
    # Jika tidak cocok
    return "Untuk pertanyaan tentang pola makan diabetes:\n1. Sebutkan makanan yang ingin Anda tanyakan\n2. Tanyakan tentang porsi\n3. Tanyakan menu contoh\n4. Tanyakan tentang indeks glikemik"

# Input pengguna
if prompt := st.chat_input("Tulis pertanyaan tentang diabetes dan pola makan..."):
    # Tambahkan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Tampilkan indikator mengetik
    with st.empty() as typing_container:
        typing_container.markdown("<div class='typing-indicator'>🩺 Nutrisionis sedang mengetik...</div>", unsafe_allow_html=True)
        time.sleep(1)  # Simulasi waktu respons
        
    # Dapatkan dan tampilkan respons
    response = get_diabetes_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun untuk update chat
    st.rerun()
