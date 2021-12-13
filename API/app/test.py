from joblib import load
import pandas as pd
from preprocess.preprocesamiento import *
from predict.predict import predict_

path_to_json_query = os.path.join(os.path.dirname(__file__), "data/latest_month_copy.json")
#precipitaciones = request.json['precipitaciones']

with open(path_to_json_query, encoding='utf-8', errors='ignore',mode='r') as f:
    file = json.load(f)
    f.close()

query_to_predict = preprocess_query(file)
prediction = predict_(query_to_predict)
print("prediction ", prediction)
