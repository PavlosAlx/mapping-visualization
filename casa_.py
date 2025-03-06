import streamlit as st
import json
import os
import folium
from streamlit_folium import folium_static
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials


# # Load credentials from an environment variable for streamlit deployment
# creds_json = os.getenv("GOOGLE_SHEET_CREDS")
# if not creds_json:
#     raise ValueError("Environment variable 'GOOGLE_SHEET_CREDS' is not set.")
# creds_dict = json.loads(creds_json)
# creds = Credentials.from_service_account_info(creds_dict)
# if creds is None:
#     raise ValueError("Failed to create credentials.")
# client = gspread.authorize(creds)

# Load credentials from Streamlit secrets - Streamlit Cloud

try:
    creds_json = st.secrets["google_sheets"]["creds"]
    st.write("Raw Secrets:", creds_json)  # Display the raw content
    creds_dict = json.loads(creds_json)  # Try to parse the JSON
    st.write("Parsed Secrets:", creds_dict)  # Display parsed content
except Exception as e:
    st.error(f"Error loading credentials: {e}")


# # Google Sheets authentication setup from json locally
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name("sheets-access.json", scope)
# client = gspread.authorize(creds)

# Open the Google Sheet
try:
    spreadsheet = client.open("Casa - Ayudame dios")
    sheet = spreadsheet.worksheet('first_search')
except Exception as e:
    st.error(f"Error accessing the Google Sheet: {str(e)}")

# Load data
expected_headers = ["Περιοχή", "Τιμή", "Τετραγωνικά"]
try:
    data = sheet.get_all_records(expected_headers=expected_headers)
except Exception as e:
    print(f"Error fetching records from Google Sheets: {e}")
    data = []

data = data[:25]  # Limit to first 25 rows

barcelona_map = folium.Map(location=[41.3784, 2.1685], zoom_start=13)

neighborhoods = {
    # Central Barcelona
    "Raval": [41.3784, 2.1685],
    "Eixample": [41.3888, 2.1590],
    "Poble Sec": [41.3723, 2.1605],
    "Gràcia": [41.4024, 2.1564],
    "Barceloneta": [41.3795, 2.1920],
    "Sant Martí": [41.4096, 2.1995],
    "Sants": [41.3751, 2.1347],
    "Les Corts": [41.3844, 2.1322],
    "Sarrià-Sant Gervasi": [41.4013, 2.1340],
    "Horta-Guinardó": [41.4184, 2.1745],
    
    # Nearby Barcelona Districts
    "El Clot": [41.4114, 2.1868],
    "El Born": [41.3851, 2.1801],
    "Vallcarca": [41.4145, 2.1453],
    "Sant Andreu": [41.4353, 2.1910],
    "Nou Barris": [41.4416, 2.1776],
    "El Carmel": [41.4192, 2.1544],
    "La Sagrera": [41.4236, 2.1867],

    # # Greater Barcelona (10-20km from Raval)
    # "Badalona": [41.4469, 2.2450],
    # "Santa Coloma de Gramenet": [41.4446, 2.2057],
    # "Montcada i Reixac": [41.4835, 2.1884],
    # "Cerdanyola del Vallès": [41.4919, 2.1405],
    # "Sant Cugat del Vallès": [41.4720, 2.0842],
    # "Esplugues de Llobregat": [41.3769, 2.0882],
    # "Cornellà de Llobregat": [41.3582, 2.0701],
    # "L'Hospitalet de Llobregat": [41.3596, 2.1003],
    # "Sant Boi de Llobregat": [41.3436, 2.0361],
    # "El Prat de Llobregat": [41.3249, 2.0945],
    # "Castelldefels": [41.2770, 1.9812],
    # "Gavà": [41.3071, 1.9995],
    # "Viladecans": [41.3172, 2.0143],
    # "Tiana": [41.4821, 2.2679],
    # "Montgat": [41.4682, 2.2814],
}

# Add house markers
for name, coords in neighborhoods.items():
    folium.Marker(location=coords, popup=name, icon=folium.Icon(color="blue", icon="home")).add_to(barcelona_map)

for row in data:
    area = row["Περιοχή"]
    price = row["Τιμή"]
    size = row["Τετραγωνικά"]
    
    if area in neighborhoods:
        coords = neighborhoods[area]
        random_offset_lat = random.uniform(-0.005, 0.005)
        random_offset_lon = random.uniform(-0.005, 0.005)
        new_coords = [coords[0] + random_offset_lat, coords[1] + random_offset_lon]
        
        folium.Marker(
            location=new_coords,
            popup=f"{area}: €{price} ({size} m²)",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(barcelona_map)


# Save map as an interactive HTML file
# barcelona_map.save("barcelona_housing_map.html")

# Display the map in Streamlit - dynamic
st.title("Barcelona Housing Map")
folium_static(barcelona_map)
