from flask import Flask, render_template, request
import PyPDF2
import os
import main

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def process_pdf_files(pdf_files):
    processed_data = {}
    for pdf_file in pdf_files:
        with open(pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            data = main.extract_data_from_pdf(pdf_reader)
            processed_data[pdf_file] = data
    return processed_data

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        checked_keys = request.form.getlist('checked_keys')
        print(checked_keys)
        pdf_files = []
        for uploaded_file in request.files.getlist('pdf_files'):
            if uploaded_file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(file_path)
                pdf_files.append(file_path)
        processed_data = process_pdf_files(pdf_files)
        processed_data = {k: {k1: v1 for k1, v1 in v.items() if k1 in checked_keys} for k, v in processed_data.items()}
        print(processed_data)
        return render_template('result.html', processed_data=processed_data)
    l = ['Pot life', 'Mixed density', 'Tensile strength', 'Color', 'Adhesion bonding', 'Water vapour', 'Water absorption', 'Adhesion to concrete', 'Toxicity', 'Crack Bridging', 'Flexibility', 'Elongation at break', 'Hardness', 'Packaging']
    return render_template('upload.html', data=l)

if __name__ == '__main__':
    app.run(debug=True)
