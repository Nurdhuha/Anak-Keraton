def display_recommendations(recommendations, pantangan, preferensi_diet):
    # Add error handling for missing arguments
    if not pantangan or not preferensi_diet:
        st.error("Data pantangan atau preferensi diet tidak tersedia")
        return
        
    if not recommendations:
        st.warning("Tidak ada rekomendasi menu yang sesuai")
        return
        
    recommended_menus, menu_suggestions = recommendations[0], recommendations[1]
    
    st.subheader("Menu Tambahan Berdasarkan Pantangan dan Preferensi Diet")
    
    if recommended_menus:
        unique_menus = []
        seen_menus = set()
        for menu in recommended_menus:
            if menu['menu'] not in seen_menus:
                unique_menus.append(menu)
                seen_menus.add(menu['menu'])
        
        df_rekomendasi = pd.DataFrame([{
            'Waktu Makan': menu['waktu_makan'],
            'Menu': menu['menu'],
            'Kalori (kkal)': float(menu.get('total_kalori_kkal') or 0),
            'Karbohidrat (g)': float(menu.get('total_karbohidrat_g') or 0),
            'Protein (g)': float(menu.get('total_protein_g') or 0),
            'Lemak (g)': float(menu.get('total_lemak_g') or 0)
        } for menu in unique_menus])
        
        st.dataframe(df_rekomendasi.set_index('Waktu Makan'))
        
        # Display menu suggestions
        if menu_suggestions:
            st.subheader("Saran Modifikasi Menu")
            for suggestion in menu_suggestions:
                st.write(f"Menu: {suggestion['menu']}")
                for saran in suggestion['suggestions']:
                    st.write(f"- {saran}")
                    
    else:
        st.error("Tidak dapat menemukan menu yang sesuai dengan kriteria")
    
    # Display dietary restrictions and preferences
    st.write(f"Pantangan makananmu: {', '.join(pantangan)}")
    if 'Tidak Ada' not in pantangan:
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
