import streamlit as st

def calculate_bmr(weight, height, gender):
    if gender == "Laki-laki":
        return 30 * weight
    else:
        return 25 * weight

def calculate_energy(age, bmr, activity_level, weight_status):
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

    weight_factor = {
        "Kurang": 0.2,
        "Berlebih": -0.1,
        "Obesitas": -0.2,
        "Normal": 0
    }.get(weight_status, 0)

    stress_metabolic = 0.1

    return (bmr * (1 + activity_factor)) - (bmr * age_factor) + (bmr * weight_factor) + (bmr * stress_metabolic)

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

def calculate_bmi(berat_badan, tinggi_badan):
    if berat_badan > 0 and tinggi_badan > 0:
        imt = berat_badan / ((tinggi_badan / 100) ** 2)
        st.info(f"IMT Anda: {imt:.1f}")

        if imt < 18.5:
            st.warning("Kategori: Berat Badan Kurang")
            return "Kurang"
        elif 18.5 <= imt < 23:
            st.success("Kategori: Berat Badan Normal")
            return "Normal"
        elif 23 <= imt < 25:
            st.warning("Kategori: Berat Badan Berlebih, Beresiko Obesitas")
            return "Berlebih"
        elif 25 <= imt < 30:
            st.warning("Kategori: Obesitas Tingkat 1")
            return "Obesitas"
        else:
            st.error("Kategori: Obesitas Tingkat 2")
            return "Obesitas"
    else:
        st.error("Berat badan atau tinggi badan tidak valid")
        return None
