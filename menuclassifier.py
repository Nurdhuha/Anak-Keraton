import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import json
from pymongo import MongoClient
import certifi
import streamlit as st
from kelompokdiet import get_diet_group, calculate_bmr, calculate_energy

def get_database():
    try:
        connection_string = "mongodb+srv://nurdhuhaam:Nurdhuha123@cluster0.ec5z7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
        return client['Database_Dhuha']
    except Exception as e:
        st.error(f"Gagal membuat koneksi database: {str(e)}")
        return None

def load_menu_data():
    with open('data/rekomendasi_menu.json') as f:
        return json.load(f)

def create_menu_features(menu_data):
    features = []
    labels = []
    
    # Definisi kategori pantangan
    pantangan_categories = {
        'seafood': ['ikan', 'udang', 'cumi', 'kepiting'],
        'daging_merah': ['daging sapi', 'baso'],
        'kacang': ['tahu', 'tempe', 'kacang merah', 'kacang panjang'],
        'dairy': ['susu', 'keju', 'yogurt']
    }
    
    for menu in menu_data:
        # Get nutritional values with default 0 for None/null values
        feature = {
            'kalori': float(menu.get('total_kalori_kkal', 0) or 0),
            'karbohidrat': float(menu.get('total_karbohidrat_g', 0) or 0),
            'protein': float(menu.get('total_protein_g', 0) or 0),
            'lemak': float(menu.get('total_lemak_g', 0) or 0),
            'seafood': 0,
            'daging_merah': 0,
            'kacang': 0,
            'dairy': 0
        }
        
        # Check ingredients in komponen
        for komponen in menu.get('komponen', []):
            bahan = komponen['bahan'].lower()
            for category, ingredients in pantangan_categories.items():
                if any(ing in bahan for ing in ingredients):
                    feature[category] = 1
        
        features.append(list(feature.values()))
        labels.append(menu['golongan'])
    
    return np.array(features), np.array(labels)

def train_menu_classifier():
    menu_data = load_menu_data()
    X, y = create_menu_features(menu_data)
    
    # Handle missing values
    imputer = SimpleImputer(strategy='constant', fill_value=0)
    X_imputed = imputer.fit_transform(X)
    
    classifier = GaussianNB()
    classifier.fit(X_imputed, y)
    return classifier, imputer

def get_alternative_menu(original_menu, pantangan, all_menus):
    """
    Find alternative menu with similar nutritional value but without restricted ingredients
    """
    # Get nutritional values with default 0 for None values
    target_calories = float(original_menu.get('total_kalori_kkal') or 0)
    target_carbs = float(original_menu.get('total_karbohidrat_g') or 0)
    target_protein = float(original_menu.get('total_protein_g') or 0)
    
    suitable_menus = []
    
    for menu in all_menus:
        # Skip if menu contains restricted ingredients
        if has_restricted_ingredients(menu, pantangan):
            continue
            
        # Calculate nutritional similarity with safe conversion
        cal_diff = abs(float(menu.get('total_kalori_kkal') or 0) - target_calories)
        carb_diff = abs(float(menu.get('total_karbohidrat_g') or 0) - target_carbs)
        protein_diff = abs(float(menu.get('total_protein_g') or 0) - target_protein)
        
        # Add to suitable menus if within acceptable range (e.g., ±20%)
        # Avoid division by zero
        if target_calories > 0:
            cal_threshold = target_calories * 0.2
        else:
            cal_threshold = 50  # default threshold

        if target_carbs > 0:
            carb_threshold = target_carbs * 0.2
        else:
            carb_threshold = 10  # default threshold

        if (cal_diff <= cal_threshold and
            carb_diff <= carb_threshold):
            suitable_menus.append((menu, cal_diff + carb_diff + protein_diff))
    
    # Sort by similarity and return the most similar menu
    if suitable_menus:
        return min(suitable_menus, key=lambda x: x[1])[0]
    return None

def has_restricted_ingredients(menu, pantangan):
    if 'Tidak Ada' in pantangan:
        return False
        
    restricted_ingredients = {
        'Seafood': ['ikan', 'udang', 'cumi', 'kepiting'],
        'Daging Merah': ['daging sapi', 'baso'],
        'Kacang-kacangan': ['tahu', 'tempe', 'kacang merah', 'kacang panjang'],
        'Dairy': ['susu', 'keju', 'yogurt']
    }
    
    for restriction in pantangan:
        if restriction in restricted_ingredients:
            for ingredient in restricted_ingredients[restriction]:
                for komponen in menu.get('komponen', []):
                    if ingredient in komponen['bahan'].lower():
                        return True
    return False

def get_diet_preferences_menus():
    """
    Return dictionary of diet preferences and their allowed menus
    """
    return {
        'Vegetarian': [
            'pepaya',
            'nagasari ubi ungu isi pisang',
            'buah melon',
            'puding melon',
            'singkong goreng isi unti',
            'jus semangka',
            'kue lapis ubi kuning',
            'buah pisang',
            'milkshake semangka',
            'bolu kukus lapis talas'
        ],
        'Vegan': [
            'pepaya',
            'nagasari ubi ungu isi pisang',
            'buah melon',
            'puding melon',
            'singkong goreng isi unti',
            'jus semangka',
            'kue lapis ubi kuning',
            'buah pisang'
        ],
        'Bebas Gluten': [
            'pepaya',
            'buah melon',
            'puding melon',
            'singkong goreng isi unti',
            'jus semangka',
            'buah pisang'
        ],
        'Rendah Karbohidrat': [
            'pepaya',
            'buah melon',
            'puding melon',
            'jus semangka',
            'buah pisang'
        ],
        'Normal': []  # Empty list means all menus are allowed
    }

def filter_menu_by_diet_preference(menu, preferensi_diet):
    """
    Check if menu is allowed for given diet preference
    """
    if 'Normal' in preferensi_diet:
        return True
        
    diet_menus = get_diet_preferences_menus()
    menu_name = menu['menu'].lower()
    
    for preference in preferensi_diet:
        if preference == 'Normal':
            return True
        allowed_menus = [m.lower() for m in diet_menus.get(preference, [])]
        if menu_name in allowed_menus:
            return True
    return False

def calculate_daily_calories_range(diet_group):
    """Calculate calorie range for diet group"""
    ranges = {
        "I": (0, 1200),  # Modified to match kelompokdiet.py ranges
        "II": (1200, 1400),
        "III": (1401, 1600),
        "IV": (1601, 1800), 
        "V": (1801, 2000),
        "VI": (2001, 2200),
        "VII": (2201, 2400),
        "VIII": (2401, 9999)  # Upper bound for highest group
    }
    return ranges.get(diet_group, (0, 1200))  # Default to group I range

def get_menu_suggestions(menu, pantangan, preferensi_diet):
    """Generate suggestions for restricted ingredients"""
    suggestions = []
    
    # Check pantangan
    for komponen in menu.get('komponen', []):
        bahan = komponen['bahan'].lower()
        for restriction, ingredients in {
            'Seafood': ['ikan', 'udang', 'cumi', 'kepiting'],
            'Daging Merah': ['daging sapi', 'baso'],
            'Kacang-kacangan': ['tahu', 'tempe', 'kacang merah', 'kacang panjang'],
            'Dairy': ['susu', 'keju', 'yogurt']
        }.items():
            if any(ing in bahan for ing in ingredients) and restriction in pantangan:
                alternatives = {
                    'Seafood': 'ayam atau tahu',
                    'Daging Merah': 'ayam atau ikan',
                    'Kacang-kacangan': 'jamur atau sayuran',
                    'Dairy': 'santan atau susu kedelai'
                }
                suggestions.append(f"Ganti {bahan} dengan {alternatives[restriction]}")
    
    return suggestions

def display_menu_by_diet_group(menu_data, diet_group):
    st.subheader(f"Rekomendasi Menu untuk Golongan Diet {diet_group}")
    df_menu = pd.DataFrame([{
        'Waktu Makan': menu['waktu_makan'],
        'Menu': menu['menu'],
        'Kalori (kkal)': float(menu.get('total_kalori_kkal') or 0),
        'Karbohidrat (g)': float(menu.get('total_karbohidrat_g') or 0),
        'Protein (g)': float(menu.get('total_protein_g') or 0),
        'Lemak (g)': float(menu.get('total_lemak_g') or 0)
    } for menu in menu_data if menu['golongan'] == diet_group])
    
    st.dataframe(df_menu.set_index('Waktu Makan'))
    
    # Display total nutritional values
    total_calories = df_menu['Kalori (kkal)'].sum()
    total_carbs = df_menu['Karbohidrat (g)'].sum()
    total_protein = df_menu['Protein (g)'].sum()
    total_fat = df_menu['Lemak (g)'].sum()
    
    st.write(f"Total Kalori: {total_calories:.1f} kkal")
    st.write(f"Total Karbohidrat: {total_carbs:.1f} g")
    st.write(f"Total Protein: {total_protein:.1f} g")
    st.write(f"Total Lemak: {total_fat:.1f} g")

def generate_menu_recommendations(user_data):
    menu_data = load_menu_data()
    classifier, imputer = train_menu_classifier()
    
    # Get diet group using imported functions
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
    weight_status = "Kurang" if imt < 18.5 else "Normal" if imt < 25 else "Berlebih" if imt < 30 else "Obesitas"
    kebutuhan_kalori = calculate_energy(usia, bmr, tingkat_aktivitas, weight_status)
    diet_group = get_diet_group(kebutuhan_kalori)
    
    pantangan = user_data["preferensi_makanan"]["pantangan"]
    preferensi_diet = user_data["preferensi_makanan"]["preferensi_diet"]
    
    recommended_menus = []
    menu_suggestions = []
    total_calories = 0
    
    # Display menu by diet group
    display_menu_by_diet_group(menu_data, diet_group)
    
    # Group menus by waktu_makan
    menus_by_time = {
        "pagi": [],
        "selingan I": [],
        "siang": [],
        "selingan II": [],
        "malam": []
    }
    
    for menu in menu_data:
        if menu['golongan'] == diet_group:
            waktu = menu['waktu_makan']
            if waktu in menus_by_time:
                menus_by_time[waktu].append(menu)

    # Generate recommendations ensuring total calories meet the requirement
    for waktu in menus_by_time.keys():
        try:
            available_menus = menus_by_time[waktu]
            suitable_menus = [
                menu for menu in available_menus 
                if not has_restricted_ingredients(menu, pantangan) and 
                filter_menu_by_diet_preference(menu, preferensi_diet)
            ]
            
            if not suitable_menus:  # If no suitable menu in current diet group
                # Look for alternatives in other diet groups
                other_menus = [
                    menu for menu in menu_data 
                    if menu['waktu_makan'] == waktu and
                    not has_restricted_ingredients(menu, pantangan) and 
                    filter_menu_by_diet_preference(menu, preferensi_diet)
                ]
                if other_menus:
                    suitable_menus = other_menus

            if suitable_menus:
                # Calculate remaining needed calories
                remaining_target = kebutuhan_kalori - total_calories
                
                # Sort menus by calorie content
                suitable_menus.sort(
                    key=lambda x: abs(float(x.get('total_kalori_kkal', 0) or 0) - (remaining_target / (5 - len(recommended_menus))))
                )
                
                best_menu = suitable_menus[0]
                menu_calories = float(best_menu.get('total_kalori_kkal', 0) or 0)
                
                if menu_calories > 0:  # Only add menu if it has calories
                    recommended_menus.append(best_menu)
                    total_calories += menu_calories
                    
                    suggestions = get_menu_suggestions(best_menu, pantangan, preferensi_diet)
                    if suggestions:
                        menu_suggestions.append({
                            'menu': best_menu['menu'],
                            'suggestions': suggestions
                        })
                        
        except Exception as e:
            st.error(f"Error generating recommendation for {waktu}: {str(e)}")
            continue
    
    # If total calories still don't meet requirement, add supplementary items
    while total_calories < kebutuhan_kalori:
        deficit = kebutuhan_kalori - total_calories
        supplementary_menus = [
            menu for menu in menu_data 
            if float(menu.get('total_kalori_kkal', 0) or 0) <= deficit and
            not has_restricted_ingredients(menu, pantangan) and 
            filter_menu_by_diet_preference(menu, preferensi_diet)
        ]
        
        if supplementary_menus:
            supplementary_menus.sort(key=lambda x: float(x.get('total_kalori_kkal', 0) or 0), reverse=True)
            for menu in supplementary_menus:
                if total_calories < kebutuhan_kalori:
                    recommended_menus.append(menu)
                    total_calories += float(menu.get('total_kalori_kkal', 0) or 0)
                else:
                    break
        else:
            break
    
    recommendations = (recommended_menus, menu_suggestions, total_calories, (kebutuhan_kalori * 0.9, kebutuhan_kalori * 1.1))
    
    # Pass pantangan and preferensi_diet to display_recommendations
    return recommendations

def display_recommendations(recommendations):
    if not recommendations:
        st.warning("Tidak ada rekomendasi menu yang sesuai")
        return
        
    recommended_menus, menu_suggestions, total_calories, (min_calories, max_calories) = recommendations
    
    st.subheader("Menu yang Direkomendasikan")
    if recommended_menus:
        # Remove duplicate menus while preserving order
        seen_menus = set()
        unique_menus = []
        for menu in recommended_menus:
            if menu['menu'] not in seen_menus:
                seen_menus.add(menu['menu'])
                unique_menus.append(menu)

        df_rekomendasi = pd.DataFrame([{
            'Waktu Makan': menu['waktu_makan'],
            'Menu': menu['menu'],
            'Kalori (kkal)': float(menu.get('total_kalori_kkal') or 0),
            'Karbohidrat (g)': float(menu.get('total_karbohidrat_g') or 0),
            'Protein (g)': float(menu.get('total_protein_g') or 0),
            'Lemak (g)': float(menu.get('total_lemak_g') or 0)
        } for menu in unique_menus])
        
        st.dataframe(df_rekomendasi.set_index('Waktu Makan'))
        
        st.write("### Status Kalori")
        st.write(f"Total Kalori Menu: {total_calories:.1f} kkal")
        
        percentage = (total_calories / max_calories) * 100
        
        if total_calories < min_calories:
            deficit = min_calories - total_calories
            st.warning(f"Total kalori masih kurang {deficit:.1f} kkal dari kebutuhan minimal")
        elif total_calories > max_calories:
            excess = total_calories - max_calories
            st.warning(f"Total kalori melebihi {excess:.1f} kkal dari batas maksimal")
        else:
            st.success(f"Total kalori sudah sesuai dengan kebutuhan ({percentage:.1f}% dari target)")
        
        if menu_suggestions:
            st.subheader("Saran Modifikasi Menu")
            for suggestion in menu_suggestions:
                st.write(f"Menu: {suggestion['menu']}")
                for saran in suggestion['suggestions']:
                    st.write(f"- {saran}")
                    
        st.subheader("Total Nilai Gizi:")
        total_carbs = sum(float(menu.get('total_karbohidrat_g') or 0) for menu in recommended_menus)
        total_protein = sum(float(menu.get('total_protein_g') or 0) for menu in recommended_menus)
        total_fat = sum(float(menu.get('total_lemak_g') or 0) for menu in recommended_menus)
        
        st.write(f"Total Karbohidrat: {total_carbs:.1f} g")
        st.write(f"Total Protein: {total_protein:.1f} g")
        st.write(f"Total Lemak: {total_fat:.1f} g")
    else:
        st.error("Tidak dapat menemukan menu yang sesuai dengan kriteria")

def main():
    db = get_database()
    if db:
        user_collection = db['users']
        user_data = user_collection.find_one()
        
        if user_data:
            recommendations = generate_menu_recommendations(user_data)
            if recommendations:
                display_recommendations(recommendations)  # Changed this line
        else:
            st.error("Data pengguna tidak ditemukan")
