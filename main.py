from flask import Flask, render_template, request
import requests
import pandas as pd
import pytesseract
import os
import cv2
import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
@app.route('/',methods=['GET'])
def Home():
    return render_template('index.html')
@app.route("/predict", methods=['POST'])
def extract():
    final_data = pd.read_csv('Final Database.csv')
    if request.method == 'POST':
        address = request.form['URL/Directory']
        ctr = 0
        for i in ['https://', 'http://', 'www.']:
            sub_str = i
            def check(address, sub_str):
                if (address.find(sub_str) == -1):
                    return 'NO'
                else:
                    return 'YES'
            yes_no = check(address, sub_str)
            if yes_no == 'YES':
                ctr = ctr + 1
            if ctr == 1:
                break
        image_name = []
        image_add = []
        image_text = []
        if yes_no == 'YES':
            url = address
            a = urlparse(url)
            response = requests.get(address)
            img = Image.open(BytesIO(response.content))
            text = pytesseract.image_to_string(img)
            image_name.append(os.path.basename(a.path))
            image_add.append(address)
            image_text.append(text)
        else:
            list_of_images = []
            for filename in os.listdir(address):
                if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".pdf") or filename.endswith(".tiff"):
                    list_of_images.append(os.path.join(address, filename))
            for i in list_of_images:
                url = i
                a = urlparse(url)
                img = cv2.imread(i)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                text = pytesseract.image_to_string(img)
                image_name.append(os.path.basename(a.path))
                image_add.append(i)
                image_text.append(text)
        for i in range(len(image_text)):
            new_str = ' '
            for j in range(len(image_text[i])):
                if image_text[i][j] != '\n':
                    new_str = new_str + image_text[i][j]
            image_text[i] = new_str
        data = {'Image' : image_name, 'URL/Path' : image_add, 'Text' : image_text}
        data = pd.DataFrame(data)
        final_data = pd.concat([final_data, data], axis = 0)
        final_data.to_csv('Final Database.csv', index = None)
        return render_template('index.html', prediction_text = "Final Database.csv saved in folder. Thank you!!!")
    else:
        return render_template('index.html')
if __name__=="__main__":
    app.run(debug=True)