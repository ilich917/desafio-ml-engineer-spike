import pandas as pd
from csv import writer
import joblib
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, mutual_info_regression
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score


def train():
    precio_leche_pp_pib = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/cleaned_data.csv"))

    X = precio_leche_pp_pib.drop(['Precio_leche'], axis = 1)
    y = precio_leche_pp_pib['Precio_leche']

    np.random.seed(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipe = Pipeline([('scale', StandardScaler()),
                    ('selector', SelectKBest(mutual_info_regression)),
                    ('poly', PolynomialFeatures()),
                    ('model', Ridge())])
    k=[3, 4, 5, 6, 7, 10]
    alpha=[1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
    poly = [1, 2, 3, 5, 7]
    grid = GridSearchCV(estimator = pipe,
                        param_grid = dict(selector__k=k,
                                        poly__degree=poly,
                                        model__alpha=alpha),
                        cv = 3,
                    scoring = 'r2')
    grid.fit(X_train.values, y_train)
    y_predicted = grid.predict(X_test)

    # evaluar modelo
    rmse = mean_squared_error(y_test, y_predicted)
    r2 = r2_score(y_test, y_predicted)

    # printing values
    #print('RMSE: ', rmse)
    #

    with open(os.path.join(os.path.dirname(__file__), "../monitoring/metrics.csv"), 'a') as f:
        writer_object = writer(f)
        periodo = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/periods.csv")).tail(1)
        periodo = list(periodo['Periodo'])
        metricas = [str(periodo[0]), rmse, r2]
        writer_object.writerow(metricas)
        f.close()

    joblib.dump(grid, os.path.join(os.path.dirname(__file__), '../models/latest/model.pkl'))
    with open( os.path.join(os.path.dirname(__file__), '../models/latest/param.json'), 'w') as f:
            json.dump(grid.best_params_, f)
            f.close()