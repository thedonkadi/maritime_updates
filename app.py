from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)
data_file_path = 'data.json'
upload_folder = 'uploads'

# Ensure the upload folder exists
os.makedirs(upload_folder, exist_ok=True)

def update_json_with_new_data(ship_id, lat, lon, emergency, additional_data):
    new_data = {
        'lat': lat,
        'lon': lon,
        'emergency': emergency,
        'timestamp': datetime.utcnow().isoformat(),
    }

    new_data.update(additional_data)

    with open(data_file_path, 'r+') as f:
        data = json.load(f)

        if ship_id in data:
            data[ship_id].append(new_data)
        else:
            data[ship_id] = [new_data]

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def process_file(file):
    ship_id = os.path.splitext(file.filename)[0]
    
    # Dummy values for lat, lon, and emergency
    lat = 20.5  # Replace with actual extraction logic
    lon = 78.5  # Replace with actual extraction logic
    emergency = False  # Replace with actual emergency status

    additional_data = {}
    update_json_with_new_data(ship_id, lat, lon, emergency, additional_data)

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

    common_file_name = 'latest_image.jpg'
    common_file_path = os.path.join(upload_folder, common_file_name)

    if os.path.isfile(common_file_path):
        os.remove(common_file_path)

    file.save(common_file_path)

    updated_data = process_file(file)
    
    return jsonify({'message': 'File uploaded and processed successfully', 'data': updated_data})

@app.route('/previous_locations/<ship_id>')
def previous_locations(ship_id):
    with open(data_file_path) as f:
        data = json.load(f)

    if ship_id in data:
        return jsonify(data[ship_id])  # Return all entries for the ship
    else:
        return jsonify({'error': 'No previous data found.'}), 404

@app.route('/route.html')
def route_page():
    ship_id = request.args.get('ship_id')
    with open(data_file_path) as f:
        data = json.load(f)

    previous_entries = data.get(ship_id, [])
    return render_template('route.html', ship_id=ship_id, entries=previous_entries)

@app.route('/api/data')
def api_data():
    data = get_updated_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
