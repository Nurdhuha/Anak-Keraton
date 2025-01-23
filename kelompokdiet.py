def calculate_bmr(weight, height, gender):
    if gender == "Laki-laki":
        return 30 * weight
    else:
        return 25 * weight

def calculate_energy(age, bmr, activity_level):
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

    return (bmr * (1 + activity_factor)) - (bmr * age_factor)

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
