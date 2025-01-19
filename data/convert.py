import pandas as pd
from pymongo import MongoClient
import certifi

# Load CSV data
def load_csv_data(file_path):
    data = pd.read_csv(file_path, skiprows=1)
    return data

# Convert CSV data to MongoDB format
def convert_to_mongodb_format(csv_data):
    menu_list = []
    current_menu = {}
    
    for _, row in csv_data.iterrows():
        if pd.notna(row['golongan']):
            if current_menu:
                menu_list.append(current_menu)
            current_menu = {
                "golongan": row['golongan'],
                "waktu_makan": row['waktu makan'],
                "menu": row['menu'],
                "komponen": [],
                "total_kalori (kkal)": row['total kalori (kkal)']
            }
        else:
            component = {
                "kategori": row['komponen'],
                "bahan": row['bahan'],
                "berat (g)": row['berat (g)'],
                "total_kalori (kkal)": row['total kalori (kkal)']
            }
            current_menu["komponen"].append(component)
    
    if current_menu:
        menu_list.append(current_menu)
    
    return menu_list

# Insert data into MongoDB
def insert_into_mongodb(data, collection_name):
    connection_string = "mongodb+srv://nurdhuhaam:Nurdhuha123@cluster0.ec5z7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = client['Database_Dhuha']
    collection = db[rekomendasi_menu]
    collection.insert_many(data)

# Main function to load, convert and insert data
def main():
    # Load CSV data
    csv_data = load_csv_data('data/REKOMENDASI MENU.csv')
    
    # Convert to MongoDB format
    mongodb_data = convert_to_mongodb_format(csv_data)
    
    # Insert into MongoDB
    insert_into_mongodb(mongodb_data, 'rekomendasi_menu')

if __name__ == "__main__":
    main()
