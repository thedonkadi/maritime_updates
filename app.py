from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)
data_file_path = 'data.json'
upload_folder = 'uploads'

# Ensure the upload folder exists
os.makedirs(upload_folder, exist_ok=True)

def update_json_with_new_data(ship_id, lat, lon, ship_type, emergency):
    new_data = {
        'lat': lat,
        'lon': lon,
        'type': ship_type,
        'emergency': emergency,
        'flag': 1  # New data flag
    }

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
    # Dummy processing logic
    ship_id = os.path.splitext(file.filename)[0]  # Use filename (without extension) as ship ID
    lat = 20.5  # Replace with extracted latitude
    lon = 78.5  # Replace with extracted longitude
    ship_type = "Ship"  # Replace with actual type if available
    emergency = False  # Replace with actual emergency status if available

    # Update JSON with the new data
    update_json_with_new_data(ship_id, lat, lon, ship_type, emergency)

    # Fetch and return updated data
    return get_updated_data()

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
        return jsonify({'message': 'No file uploaded.'}), 400

    file = request.files['file']
    
    # Save the uploaded file
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    
    # Process the uploaded file and get updated data
    updated_data = process_file(file)

    return jsonify({'message': 'File uploaded and processed successfully.', 'data': updated_data}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    with open(data_file_path) as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
