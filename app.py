from flask import Flask, request, send_file, render_template
import pandas as pd
import os
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Initialize the timezone finder and geolocator
tf = TimezoneFinder()
geolocator = Nominatim(user_agent="zip_to_timezone")

# Map of time zone names to their abbreviations
TIMEZONE_ABBREVIATIONS = {
    "America/Los_Angeles": "PST",
    "America/Phoenix": "MST",
    "America/Denver": "MST",
    "America/Chicago": "CST",
    "America/New_York": "EST",
    "America/Detroit": "EST",
    "America/Halifax": "AST",
    "America/St_Johns": "NST",
    "America/Edmonton": "MST",
    "America/Regina": "CST",
    "America/Toronto": "EST",
    "America/Vancouver": "PST",
    "Pacific/Honolulu": "HAST",  # Added Hawaii time zone
}

def get_timezone_from_zip(zip_code):
    try:
        country = 'CA' if zip_code[0].isalpha() else 'US'
        location = geolocator.geocode({'postalcode': zip_code, 'country': country})
        if location:
            timezone_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            return TIMEZONE_ABBREVIATIONS.get(timezone_name, "Timezone not found")
        else:
            return "Invalid ZIP/Postal Code"
    except Exception as e:
        return f"Error: {e}"

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    if 'Zip Code' not in df.columns:
        raise ValueError("The 'Zip Code' column is missing from the input file.")
    
    df['Timezone'] = df['Zip Code'].apply(lambda x: get_timezone_from_zip(str(x)))
    df.to_csv(output_file, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part")
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return "No selected file", 400
    
    print(f"File received: {file.filename}")  # Debugging log
    input_file_path = os.path.join('uploads', file.filename)
    output_file_path = os.path.join('outputs', 'OutputExample_Complete.csv')
    
    file.save(input_file_path)
    
    try:
        process_csv(input_file_path, output_file_path)
        return send_file(output_file_path, as_attachment=True)
    except Exception as e:
        print(f"Error processing file: {e}")  # Debugging log
        return f"Error processing file: {e}", 500

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    app.run(debug=True)
