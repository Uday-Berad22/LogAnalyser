from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Process the file and generate CSV
    csv_path = process_log_file(file_path)

    return jsonify({"csvFileUrl": f'http://localhost:5000/download/{os.path.basename(csv_path)}'})

def process_log_file(file_path):
    # Implement your log processing logic here
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = []
    for line in lines:
        # Example: split line by whitespace
        data.append(line.strip().split())

    df = pd.DataFrame(data)
    csv_path = os.path.join(OUTPUT_FOLDER, os.path.basename(file_path) + '.csv')
    df.to_csv(csv_path, index=False)
    
    return csv_path

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
