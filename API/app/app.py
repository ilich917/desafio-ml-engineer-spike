from joblib import load
import pandas as pd
from flask import Flask, request
from preprocess.preprocesamiento import *
from predict.predict import predict_

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.json
        query_to_predict = preprocess_query(file)
        prediction = predict(query_to_predict)
        return json.dumps(prediction)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
