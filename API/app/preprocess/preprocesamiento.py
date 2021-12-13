import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import numpy as np
import locale
import dateparser
import joblib
import os

import pandas as pd
import os
import json


def to_100(x): #mirando datos del bc, pib existe entre ~85-120 - igual esto es cm (?)
    x = x.split('.')
    if x[0].startswith('1'): #es 100+
        if len(x[0]) >2:
            return float(x[0] + '.' + x[1])
        else:
            x = x[0]+x[1]
            return float(x[0:3] + '.' + x[3:])
    else:
        if len(x[0])>2:
            return float(x[0][0:2] + '.' + x[0][-1])
        else:
            x = x[0] + x[1]
            return float(x[0:2] + '.' + x[2:])
        
def convert_int(x):
    return int(x.replace('.', ''))

def preprocess_query(file):
    precipitaciones_query = file['precipitaciones']
    precipitaciones_q_df = pd.DataFrame.from_dict([precipitaciones_query])
    
    
    precio_leche_query = file['precio_leche']
    precio_leche_q_df = pd.DataFrame.from_dict([precio_leche_query])
    
    banco_central_query = file['banco_central']
    banco_central_q_df = pd.DataFrame.from_dict([banco_central_query])  
    
    precipitaciones = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/precipitaciones.csv"))#[mm]
    precipitaciones = precipitaciones.append(precipitaciones_q_df)

    precipitaciones['date'] = pd.to_datetime(precipitaciones['date'], format = '%Y-%m-%d')
    precipitaciones['Periodo'] = precipitaciones['date']

    banco_central = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/banco_central.csv"))
    banco_central = banco_central.append(banco_central_q_df)

    banco_central['Periodo'] = banco_central['Periodo'].apply(lambda x: x[0:10])
    banco_central['Periodo'] = banco_central['Periodo'].apply(lambda x: dateparser.parse(x,date_formats=['%Y-%m-%d'], languages=['es']))
    banco_central['Periodo'] = pd.to_datetime(banco_central['Periodo'], format = '%Y-%m-%d', errors = 'coerce')

    cols_pib = [x for x in list(banco_central.columns) if 'PIB' in x]
    cols_pib.extend(['Periodo'])
    cols_imacec = [x for x in list(banco_central.columns) if 'Imacec' in x]

    banco_central_pib = banco_central[[*cols_pib]]
    banco_central_pib = banco_central_pib.dropna(how = 'any', axis = 0)

    for col in cols_pib:
        if col == 'Periodo':
            continue
        else:
            banco_central_pib[col] = banco_central_pib[col].apply(lambda x: convert_int(x))

    banco_central_pib.sort_values(by = 'Periodo', ascending = True)

    banco_central_imacec = banco_central[[*cols_imacec, 'Periodo']]
    banco_central_imacec = banco_central_imacec.dropna(how = 'any', axis = 0)
    for col in cols_imacec:
        if col == 'Periodo':
            continue
        else:
            banco_central_imacec[col] = banco_central_imacec[col].apply(lambda x: to_100(x))
            assert(banco_central_imacec[col].max()>100)
            assert(banco_central_imacec[col].min()>30)

    banco_central_imacec.sort_values(by = 'Periodo', ascending = True)

    banco_central_iv = banco_central[['Indice_de_ventas_comercio_real_no_durables_IVCM', 'Periodo']]
    banco_central_iv = banco_central_iv.dropna() # -unidades? #parte 
    banco_central_iv = banco_central_iv.sort_values(by = 'Periodo', ascending = True)

    banco_central_iv['num'] = banco_central_iv.Indice_de_ventas_comercio_real_no_durables_IVCM.apply(lambda x: to_100(x))
    banco_central_num = pd.merge(banco_central_pib, banco_central_imacec, on = 'Periodo', how = 'inner')
    banco_central_num = pd.merge(banco_central_num, banco_central_iv, on = 'Periodo', how = 'inner')

    precio_leche = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/precio_leche.csv"))
    precio_leche = precio_leche.append(precio_leche_q_df)

    precio_leche["Periodo"] = precio_leche["Anio"].astype(str) +'-'+ precio_leche["Mes"].astype(str) + "-01" 
    precio_leche['Periodo'] = precio_leche['Periodo'].apply(lambda x: dateparser.parse(x,date_formats=['%Y-%m-%d'], languages=['es']))
    precio_leche['Periodo'] = pd.to_datetime(precio_leche['Periodo'], format = '%Y-%m-%d', errors = 'coerce')

    target = precio_leche.sort_values(by='Periodo')
    target.drop(['Anio', 'Mes'], axis=1, inplace=True)
    precio_leche_pp = pd.merge(target, precipitaciones, on = 'Periodo', how = 'inner')

    precio_leche_pp_pib = pd.merge(precio_leche_pp, banco_central_num, on = ['Periodo'], how = 'inner')

    precio_leche_pp_pib.drop(['date','Indice_de_ventas_comercio_real_no_durables_IVCM'], axis =1, inplace = True)

    cc_cols = [x for x in precio_leche_pp_pib.columns if x not in ['Periodo']]

    precio_leche_pp_pib_shift3_mean = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).mean().shift(1)

    precio_leche_pp_pib_shift3_mean.columns = [x+'_shift3_mean' for x in precio_leche_pp_pib_shift3_mean.columns]
                                                    
    precio_leche_pp_pib_shift3_std = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).std().shift(1)

    precio_leche_pp_pib_shift3_std.columns = [x+'_shift3_std' for x in precio_leche_pp_pib_shift3_std.columns] 

    precio_leche_pp_pib_shift1 = precio_leche_pp_pib[cc_cols].shift(1)

    precio_leche_pp_pib_shift1.columns = [x+'_mes_anterior' for x in precio_leche_pp_pib_shift1.columns]

    precio_leche_pp_pib['Periodo'].to_csv(os.path.join(os.path.dirname(__file__), "../data/periods.csv"))

    precio_leche_pp_pib = pd.concat([precio_leche_pp_pib['Precio_leche'], precio_leche_pp_pib_shift3_mean, precio_leche_pp_pib_shift3_std, precio_leche_pp_pib_shift1], axis = 1) 
    precio_leche_pp_pib = precio_leche_pp_pib.dropna(how = 'any', axis = 0)

    #Save Data after preprocessing

    precio_leche_pp_pib.to_csv(os.path.join(os.path.dirname(__file__), "../data/cleaned_data.csv"))

    query_ = precio_leche_pp_pib.tail(1)

    return(np.array(query_))