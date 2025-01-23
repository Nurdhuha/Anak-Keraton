import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import json
from pymongo import MongoClient
import certifi
import streamlit as st

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
    target_calories = original_menu.get('total_kalori_kkal', 0)
    target_carbs = original_menu.get('total_karbohidrat_g', 0)
    target_protein = original_menu.get('total_protein_g', 0)
    
    suitable_menus = []
    
    for menu in all_menus:
        # Skip if menu contains restricted ingredients
        if has_restricted_ingredients(menu, pantangan):
            continue
            
        # Calculate nutritional similarity
        cal_diff = abs(menu.get('total_kalori_kkal', 0) - target_calories)
        carb_diff = abs(menu.get('total_karbohidrat_g', 0) - target_carbs)
        protein_diff = abs(menu.get('total_protein_g', 0) - target_protein)
        
        # Add to suitable menus if within acceptable range (e.g., ±20%)
        if (cal_diff <= target_calories * 0.2 and
            carb_diff <= target_carbs * 0.2 and
            protein_diff <= target_protein * 0.2):
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

def generate_menu_recommendations(user_data):
    menu_data = load_menu_data()
    classifier, imputer = train_menu_classifier()
    
    pantangan = user_data["preferensi_makanan"]["pantangan"]
    preferensi_diet = user_data["preferensi_makanan"]["preferensi_diet"]
    
    recommended_menus = []
    
    # Group menus by waktu_makan
    menus_by_time = {}
    for menu in menu_data:
        waktu = menu['waktu_makan']
        if waktu not in menus_by_time:
            menus_by_time[waktu] = []
        menus_by_time[waktu].append(menu)
    
    # Generate recommendations for each meal time
    for waktu, menus in menus_by_time.items():
        suitable_menus = [
            menu for menu in menus 
            if not has_restricted_ingredients(menu, pantangan) and 
            filter_menu_by_diet_preference(menu, preferensi_diet)
        ]
        
        if suitable_menus:
            # Use classifier to predict the best menu
            features = np.array([create_menu_features([menu])[0][0] for menu in suitable_menus])
            features_imputed = imputer.transform(features)  # Apply same imputation
            predictions = classifier.predict_proba(features_imputed)
            
            # Get the menu with highest probability for user's diet group
            best_menu = suitable_menus[np.argmax(predictions)]
            recommended_menus.append(best_menu)
        else:
            # Find alternative menu
            alternative_menus = [
                menu for menu in menu_data 
                if not has_restricted_ingredients(menu, pantangan) and 
                filter_menu_by_diet_preference(menu, preferensi_diet)
            ]
            
            if alternative_menus:
                original_menu = next((menu for menu in menus), None)
                if original_menu:
                    alt_menu = get_alternative_menu(original_menu, pantangan, alternative_menus)
                    if alt_menu:
                        recommended_menus.append(alt_menu)
    
    return recommended_menus

def display_recommendations(recommendations):
    if not recommendations:
        st.warning("Tidak ada rekomendasi menu yang sesuai")
        return
        
    st.subheader("Rekomendasi Menu Berdasarkan Preferensi")
    
    df_rekomendasi = pd.DataFrame([{
        'Waktu Makan': menu['waktu_makan'],
        'Menu': menu['menu'],
        'Kalori (kkal)': menu.get('total_kalori_kkal', 0),
        'Karbohidrat (g)': menu.get('total_karbohidrat_g', 0),
        'Protein (g)': menu.get('total_protein_g', 0),
        'Lemak (g)': menu.get('total_lemak_g', 0)
    } for menu in recommendations])
    
    st.dataframe(df_rekomendasi.set_index('Waktu Makan'))
    
    # Display total nutritional value
    total_calories = sum(menu.get('total_kalori_kkal', 0) for menu in recommendations)
    total_carbs = sum(menu.get('total_karbohidrat_g', 0) for menu in recommendations)
    total_protein = sum(menu.get('total_protein_g', 0) for menu in recommendations)
    total_fat = sum(menu.get('total_lemak_g', 0) for menu in recommendations)
    
    st.write("Total Nilai Gizi:")
    st.write(f"Total Kalori: {total_calories:.1f} kkal")
    st.write(f"Total Karbohidrat: {total_carbs:.1f} g")
    st.write(f"Total Protein: {total_protein:.1f} g")
    st.write(f"Total Lemak: {total_fat:.1f} g")
