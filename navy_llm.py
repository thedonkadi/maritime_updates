import json
from PIL import Image
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
import pytesseract
groq_api_key= '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'

def extract_text_from_image(image_path):
    try:
        # Set path to tessdata if needed
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # Open the image using PIL
        image = Image.open(image_path)
        
        # Perform OCR using Tesseract
        extracted_text = pytesseract.image_to_string(image)
        
        print("OCR text:", extracted_text)
        
        return extracted_text
    except Exception as e:
        print(f"Error in extracting text from image: {e}")
        return None

# Function to analyze extracted text and return JSON features
def analyze_text_with_model(extracted_text, model):
    system_prompt = """
    You are a maritime intelligence system. Your job is to analyze and extract specific features from maritime reports.
    Each report includes information about objects such as ships, submarines, or aircraft.

    Features to extract:
    1. Geographical information (latitude, longitude, heading, speed)
    2. Temporal data (time of sighting, date)
    3. Vessel attributes (name , type, size, nationality, MLA)
    4. Behavioral features (movement, threat level, proximity)
    5. Additional attributes (weather conditions, communications log)

    If a feature is unavailable, return null for that field. Your output should be a JSON object containing these features.
    just give the json file the format should be like this:
    {
        "latitude": null,
        "longitude": null,
        "name" : null,
        "heading": null,
        "speed": null,
        "time_of_sighting": null,
        "date": null,
        "vessel_type": null,
        "size": null,
        "nationality": null,
        "MLA": null,
        "movement": null,
        "threat_level": null,
        "proximity": null,
        "weather_conditions": null,
        "communications_log": null
    }
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=extracted_text)
    ]
    
    try:
        result = model.invoke(messages)
        return result
    except Exception as e:
        print(f"Error in analyzing text with model: {e}")
        return None

# Function to parse result into JSON format
def parse_to_json(result):
    from langchain_core.output_parsers import StrOutputParser
    
    parser = StrOutputParser()
    json_string = parser.invoke(result)

    # Find the first occurrences of '{' and '}'
    start_index = json_string.find('{')
    end_index = json_string.rfind('}') + 1

    # Extract the substring that contains the JSON
    json_substring = json_string[start_index:end_index]
    print("json text" ,json_substring )
    return json_substring

# Function to save extracted features to a JSON file
def save_to_json_file(data, filename):
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON data has been extracted and written to {filename}")
    except Exception as e:
        print(f"Error in saving JSON file: {e}")

# Function to update the database with new extracted features
def update_database(new_data, db_path):
    try:
        # Load existing data if file exists, otherwise create empty list
        try:
            with open(db_path, "r") as db_file:
                db_data = json.load(db_file)
        except FileNotFoundError:
            db_data = []
        
        # Append the new data
        db_data.append(new_data)

        # Write updated data back to file
        with open(db_path, "w") as db_file:
            json.dump(db_data, db_file, indent=4)

        print(f"Database has been updated with new data.")
    except Exception as e:
        print(f"Error in updating database: {e}")

def process_image(image_path ):
    # Extract text from image
    extracted_text = extract_text_from_image(image_path)

    if extracted_text:
        # Initialize LangChain model
        model = ChatGroq(model="Gemma2-9b-It", groq_api_key = groq_api_key)

        # Analyze text
        analysis_result = analyze_text_with_model(extracted_text, model)

        if analysis_result:
            json_string = parse_to_json(analysis_result)

            # Convert the JSON substring to a Python dictionary
            extracted_features = json.loads(json_string)

            # Specify the filename
            filename = 'extracted_vessel_data.json'
            save_to_json_file(extracted_features, filename)

            # Update database
            db_path = "database.json"
            # update_database(extracted_features, db_path)

if __name__ == "__main__":
    process_image()
