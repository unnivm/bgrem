from flask import Flask, render_template, request, send_file, jsonify
import os
from rembg import remove
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(input_path)

            with open(input_path, 'rb') as i:
                input_data = i.read()
                output_data = remove(input_data)

            output_filename = 'processed_' + file.filename
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

            with open(output_path, 'wb') as o:
                o.write(output_data)

            # ✅ Return URL for processed image
            return jsonify({
                'image_url': f'/processed/{output_filename}'
            })

    return render_template('index.html')

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_file(os.path.join(app.config['PROCESSED_FOLDER'], filename), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
