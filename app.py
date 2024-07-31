from flask import Flask, request, jsonify
import os
import tempfile
import json
from llm import process_1003_pdf
from pymongo import MongoClient
import re
from bson import ObjectId
from flask_cors import CORS


def extract_json_data(input_str):
    # Define the regex pattern to capture any prefix and extract the data inside the outermost curly braces
    pattern = re.compile(r'^[^{]*({.*})', re.DOTALL)
    match = pattern.search(input_str)

    if match:
        # Extract and return the matched string
        return match.group(1)
    else:
        # If no match is found, return the original string
        return input_str


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

MONGO_CONNECTION_URI = f"mongodb+srv://pb642001:{os.environ.get('MONGO_PASSWORD')}@ocrdb.kbu0vkh.mongodb.net/?retryWrites=true&w=majority&appName=ocrdb"

# MongoDB configuration
mongo_client = MongoClient(MONGO_CONNECTION_URI)
db = mongo_client['ocrdb']
licenseCollection = db['license']
handWrittenFormsCollection = db['handwrittenForms']


app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({"error": "File is not a PDF"}), 400

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the file to the temporary directory
        file_path = os.path.join(temp_dir, pdf_file.filename)
        pdf_file.save(file_path)

       # Process the PDF file
        result_str = process_1003_pdf(file_path)
        print("response from LLM:", result_str)

        result_dict = json.loads(extract_json_data(result_str))

        print("result dict", result_dict)

        license = result_dict['license']
        licenseCollection.insert_one(license)

        del result_dict['license']

        result_dict["number"] = license["number"]
        result_dict["issue_date"] = license["issue_date"]
        result_dict["expiration_date"] = license["expiration_date"]
        result_dict["issue_state"] = license["issue_state"]
        result_dict["last_name"] = license["last_name"]
        result_dict["first_name"] = license["first_name"]
        result_dict["dob"] = license["dob"]

        handWrittenFormsCollection.insert_one(result_dict)
    return jsonify({'message':"success"})

@app.route("/applications")
def get_all_applications():
    result = []
    for form in handWrittenFormsCollection.find():
        result.append(form)
    return JSONEncoder().encode(result)

@app.route('/search', methods=['GET'])
def search_applications():
    query_keys = ["number", "issue_date", "expiration_date", "issue_state", "last_name", "first_name", "dob"]
    query = {}

    for key in query_keys:
        value = request.args.get(key)
        if value:
            # Use regex for partial matching for specific fields
            # if key in ["first_name", "last_name", "issue_state"]:
            query[key] = {"$regex": f"^{value}", "$options": "i"}  # Case-insensitive match
            # else:
                # query[key] = value

    result = []
    for form in handWrittenFormsCollection.find(query):
        result.append(form)

    return JSONEncoder().encode({
        'success': True,
        'data': result
    })


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'health_check': "all systems up and running 🔥"})


if __name__ == '__main__':
    app.run(debug=True)
