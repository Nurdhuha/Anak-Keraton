 st.write(f"Pantangan makananmu: {', '.join(pantangan)}")
        for p in pantangan:
            if p == 'Kacang-kacangan':
                st.write("Saran: Hindari makanan yang mengandung kacang-kacangan seperti tahu, tempe, kacang merah, dan kacang panjang.")
            elif p == 'Seafood':
                st.write("Saran: Hindari makanan laut seperti ikan, udang, cumi, dan kepiting.")
            elif p == 'Daging Merah':
                st.write("Saran: Hindari daging merah seperti daging sapi dan baso.")
            elif p == 'Dairy':
                st.write("Saran: Hindari produk susu seperti susu, keju, dan yogurt.")
    else:
        st.write("Nikmati makanan kesukaanmu")
    
    if preferensi_diet:
        st.write(f"Preferensi dietmu: {', '.join(preferensi_diet)}")
        for diet in preferensi_diet:
            if diet == 'Rendah Karbohidrat':
                st.write("Saran: Pilih makanan rendah karbohidrat seperti buah melon, puding melon, jus semangka, dan buah pisang.")
            elif diet == 'Vegetarian':
                st.write("Saran: Pilih makanan vegetarian seperti pepaya, nagasari ubi ungu isi pisang, buah melon, dan singkong goreng isi unti.")
            elif diet == 'Vegan':
                st.write("Saran: Pilih makanan vegan seperti pepaya, nagasari ubi ungu isi pisang, buah melon, dan jus semangka.")
            elif diet == 'Bebas Gluten':
                st.write("Saran: Pilih makanan bebas gluten seperti pepaya, buah melon, puding melon, dan singkong goreng isi unti.")
            elif diet == 'Normal':
                st.write("Saran: Tidak ada batasan khusus, semua jenis makanan diperbolehkan.")
    else:
        st.write("Nikmati makanan kesukaanmu")
