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
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = []
    for line in lines:
        # Assuming log lines are in format: "timestamp log_type component_name message"
        parts = line.strip().split(' ')
        a=parts[0]+" "+parts[1]
        b=parts[2]
        c=parts[3]
        d=" ".join(parts[4:])
        if 1<2:
            timestamp=a
            log_type=b 
            component_name=c
            message = d
            data.append([timestamp, log_type, component_name, message])

    df = pd.DataFrame(data, columns=["Timestamp", "Log Type", "Component Name", "Message"])
    csv_path = os.path.join(OUTPUT_FOLDER, os.path.basename(file_path) + '.csv')
    df.to_csv(csv_path, index=False)
    
    return csv_path

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

# @app.route('/search', methods=['POST'])
# def search_logs():
#     data = request.get_json()
#     csv_file_path = os.path.join(OUTPUT_FOLDER, data['filename'])
#     keyword = data.get('keyword', '')

#     start_time = data.get('startTime', '00:00:00 01/01/00')
#     end_time = data.get('endTime', '23:59:59 31/12/99')

#     if not os.path.exists(csv_file_path):
#         return jsonify({"error": "File not found"}), 404

#     df = pd.read_csv(csv_file_path)
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'], format="%H:%M:%S %d/%m/%y")

#     filtered_df = df[
#        ( (df['Message'].str.contains(keyword, case=False, na=False)) 
#         | 
#         (df['Log Type'].str.contains(keyword, case=False, na=False)        )
#         |
#         (df['Component Name'].str.contains(keyword, case=False, na=False)        ))
#         &
#         (df['Timestamp'] >= pd.to_datetime(start_time, format="%H:%M:%S %d/%m/%y")) &
#         (df['Timestamp'] <= pd.to_datetime(end_time, format="%H:%M:%S %d/%m/%y"))
#     ]
#     # filtered_df=filtered_df+df[
#     #     # (df['Message'].str.contains(keyword, case=False, na=False)) 
#     #     # # or 
#     #     (df['Component Name'].str.contains(keyword, case=False, na=False)        )
#     #     # &
#     #     # (df['Timestamp'] >= pd.to_datetime(start_time, format="%H:%M:%S %d/%m/%y")) &
#     #     # (df['Timestamp'] <= pd.to_datetime(end_time, format="%H:%M:%S %d/%m/%y"))
#     # ]
    
#     result = filtered_df.to_dict(orient='records')
#     return jsonify(result)

@app.route('/search', methods=['POST'])
def search_logs():
    data = request.get_json()
    csv_file_path = os.path.join(OUTPUT_FOLDER, data['filename'])
    keyword = data.get('keyword', '')
    searchKeywordComponent=data.get('searchKeywordComponent', '')
    start_time = data.get('startTime', '00:00:00 01/01/00')
    end_time = data.get('endTime', '23:59:59 31/12/99')

    if not os.path.exists(csv_file_path):
        return jsonify({"error": "File not found"}), 404

    df = pd.read_csv(csv_file_path)
    
    try:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format="%H:%M:%S %d/%m/%y")
        start_time = pd.to_datetime(start_time, format="%H:%M:%S %d/%m/%y")
        end_time = pd.to_datetime(end_time, format="%H:%M:%S %d/%m/%y")
        print(start_time, "<---->" ,end_time)
    except ValueError as e:
        return jsonify({"error": f"Date parsing error: {str(e)}"}), 400

    filtered_df = df[
        ((df['Message'].str.contains(keyword, case=False, na=False)) | 
        (df['Log Type'].str.contains(keyword, case=False, na=False)        )
        )& ((df['Component Name'].str.contains(searchKeywordComponent, case=False, na=False)        ) |(searchKeywordComponent=="all"))
        &
        (df['Timestamp'] >= start_time) 
        &
        (df['Timestamp'] <= end_time)
    ]

    result = filtered_df.to_dict(orient='records')
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
