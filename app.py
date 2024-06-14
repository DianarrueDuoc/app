import fitz  # PyMuPDF
import openai
import requests
import time
import re
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
from io import BytesIO
import os
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# Configura tu clave de API de OpenAI de forma segura
openai.api_key = 'sk-proj-dXZhJNiQdoDvYMNhmJKjT3BlbkFJfn3bnF5Wlx0gyZ1yhJy7'

# Configura tu clave de API de Leonardo
leonardo_api_key = 'e9790eaa-1bfd-41bc-8947-6154bf8d9687'

# Configura Firebase Admin SDK
cred = credentials.Certificate("ruta/a/tu/archivo/de/credenciales.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Palabras conflictivas que podrían causar problemas
conflictive_words = ['child', 'kill', 'death', 'blood', 'murder']

# Función para eliminar palabras conflictivas
def remove_conflictive_words(text, words):
    pattern = re.compile('|'.join(re.escape(word) for word in words), re.IGNORECASE)
    return pattern.sub('[removed]', text)

# Función para extraer texto del PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Función para generar un resumen en inglés utilizando la API de OpenAI
def summarize_text_with_openai(text, max_chars=1000):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following text in English in a detailed and vivid manner, including key characters, locations, and events. Ensure the summary does not exceed {max_chars} characters:\n\n{text}"}
        ]
    )
    summary = response['choices'][0]['message']['content'].strip()
    return summary

# Función para dividir el resumen en 5 partes
def split_summary(summary, num_parts=5):
    sentences = summary.split('. ')
    parts = [''] * num_parts
    for i, sentence in enumerate(sentences):
        parts[i % num_parts] += sentence + '. '
    return parts

# Función para asegurar que el prompt no exceda los 1000 caracteres
def trim_prompt(prompt, max_chars=1000):
    if len(prompt) > max_chars:
        return prompt[:max_chars].rsplit(' ', 1)[0] + '...'
    return prompt

# Función para generar una imagen utilizando la API de Leonardo
def generate_image_with_leonardo(prompt, output_path):
    leonardo_url = 'https://cloud.leonardo.ai/api/rest/v1/generations'
    
    payload = {
        "height": 512,
        "width": 512,
        "modelId": "2067ae52-33fd-4a82-bb92-c2c55e7d2786",
        "prompt": prompt,
        "num_images": 1
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {leonardo_api_key}"
    }
    
    response = requests.post(leonardo_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        if 'sdGenerationJob' in response_data and 'generationId' in response_data['sdGenerationJob']:
            generation_id = response_data['sdGenerationJob']['generationId']
            time.sleep(20)
            
            image_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
            while True:
                image_response = requests.get(image_url, headers=headers)
                if image_response.status_code == 200:
                    image_data = image_response.json()
                    if 'generations_by_pk' in image_data and 'generated_images' in image_data['generations_by_pk']:
                        generated_images = image_data['generations_by_pk']['generated_images']
                        if len(generated_images) > 0:
                            image_url = generated_images[0]['url']
                            image_response = requests.get(image_url)
                            if image_response.status_code == 200:
                                image = Image.open(BytesIO(image_response.content))
                                image.save(output_path)
                                return output_path
                            else:
                                print(f"Error al descargar la imagen: {image_response.status_code}")
                                break
                        else:
                            print("No se encontraron datos de imagen en la respuesta.")
                    else:
                        print("No se encontraron datos de imagen en la respuesta.")
                else:
                    print(f"Error al obtener la imagen generada: {image_response.status_code}")
                time.sleep(5)
    else:
        print(f"Error al generar la imagen: {response.text}")

app = Flask(__name__)
CORS(app)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo PDF."})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo PDF."})

    upload_folder = 'C:/Users/diana/my-app/backend/uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    pdf_path = os.path.join(upload_folder, file.filename)
    file.save(pdf_path)
    
    text = extract_text_from_pdf(pdf_path)
    
    if text:
        summary = summarize_text_with_openai(text, max_chars=1000)
        summary_parts = split_summary(summary, 5)  # Dividir el resumen en 5 partes
        image_paths = []

        for i, part in enumerate(summary_parts):
            cleaned_part = remove_conflictive_words(part.strip(), conflictive_words)
            prompt = f"Create a storybook illustration with soft, pastel colors for kids, based on the following summary part: {cleaned_part}"
            prompt = trim_prompt(prompt, max_chars=1000)
            image_output_path = f"C:/Users/diana/my-app/backend/generated_images/storybook_illustration_part_{i+1}.jpg"
            
            image_path = generate_image_with_leonardo(prompt, image_output_path)
            if image_path:
                image_paths.append(image_path)
                print(f"Imagen generada y guardada en: {image_path}")

        # Guardar los datos en Firestore
        doc_ref = db.collection('uploads').add({
            'summary': summary,
            'image_paths': image_paths,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

        response = {
            "summary": summary,
            "image_paths": image_paths
        }
        print(response)
        return jsonify(response)
    else:
        return jsonify({"error": "No se encontró texto en el PDF."})

@app.route('/generated_images/<filename>')
def get_image(filename):
    return send_from_directory('C:/Users/diana/my-app/backend/generated_images', filename)

if __name__ == '__main__':
    app.run(debug=True)
