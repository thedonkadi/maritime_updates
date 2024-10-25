from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)
data_file_path = 'data.json'
upload_folder = 'uploads'

# Ensure the upload folder exists
os.makedirs(upload_folder, exist_ok=True)
from datetime import datetime

def update_json_with_new_data(ship_id, lat, lon, emergency, additional_data):
    new_data = {
        'lat': lat,
        'lon': lon,
        'emergency': emergency,
        'timestamp': datetime.utcnow().isoformat(),  # Save current timestamp in ISO format
        'flag': 1,  # New data flag, can be removed if not using
    }

    # Add any additional data fields
    new_data.update(additional_data)

    # Load existing data
    with open(data_file_path, 'r+') as f:
        data = json.load(f)

        # Update existing ship data or append new data
        if ship_id in data:
            # Append new data to existing ship
            data[ship_id].append(new_data)
        else:
            # Create new entry for the ship
            data[ship_id] = [new_data]

        # Write updated data back to JSON file
        f.seek(0)
        json.dump(data, f, indent=4)  # Write with pretty print
        f.truncate()

def process_file(file):
    # Use the uploaded file's filename as the ship ID
    ship_id = os.path.splitext(file.filename)[0]  # Use filename (without extension) as ship ID
    
    # Dummy values for lat, lon, and emergency (replace with actual extraction logic)
    lat = 20.5  # Replace with extracted latitude
    lon = 78.5  # Replace with extracted longitude
    emergency = False  # Replace with actual emergency status if available

    # Prepare additional data from the file (as a dictionary)
    additional_data = {}  # Any additional data you want to include can be extracted here

    # Update JSON with the new data
    update_json_with_new_data(ship_id, lat, lon, emergency, additional_data)

    # Fetch and return updated data
    updated_data = get_updated_data()
    return updated_data

def get_updated_data():
    with open(data_file_path) as f:
        data = json.load(f)
    return data

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Define the common name for the uploaded file
    common_file_name = 'latest_image.jpg'
    common_file_path = os.path.join(upload_folder, common_file_name)

    # Remove any existing file with the common name
    if os.path.isfile(common_file_path):
        os.remove(common_file_path)

    # Save the new file with the common name
    file.save(common_file_path)

    # Process the uploaded file (custom logic for your case)
    updated_data = process_file(file)
    
    return jsonify({'message': 'File uploaded and processed successfully', 'data': updated_data})

@app.route('/api/data')
def api_data():
    data = get_updated_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
