import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
from datetime import datetime, timedelta
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from datetime import date, timedelta
from Config import *


##### DATA #####

def daterange(start_date, end_date):
    """daterange: devuelve un generador para iterar sobre un intervalo de dias
        INPUTS:
          * start_data: dia inicial
          * end_date:  dia final 
        OUTPUT:
          un coso para iterar"""
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def save_raw_csv(dirName, fecha, cluster_data_1, cluster_data_2, cluster_data_3):

    c_1 = [t + ('1',) for t in cluster_data_1]
    c_2 = [t + ('2',) for t in cluster_data_2]
    c_3 = [t + ('3',) for t in cluster_data_3]

    all_data = c_3 + c_2 + c_1

    df = pd.DataFrame(all_data, columns=[
                      'symbol', 'cmk_rank', 'price', 'market_cap', 'id', 'cluster'])

    subdir_name = 'raw_data'
    if not os.path.exists(dirName+'/'+subdir_name):
        os.mkdir(dirName+'/'+subdir_name)

    df.to_csv(f"{dirName}/{subdir_name}/{fecha}.csv")


def Get_Data(url, parameters, headers):

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data_ = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return data_


def Get_Data_for_Token(date_, token_list):
    """Get_Data: realiza llamadas historicas a la API
        INPUTS:
          * date: dia
        OUTPUT:
          json con la informacion descargada"""

    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/historical'

    parameters = {
        'time_start': (date_ - timedelta(1)).isoformat(),
        'time_end': (date_ + timedelta(1)).isoformat(),
        'symbol': token_list,
        'interval': 'daily'
    }

    data_ = Get_Data(url, parameters, headers)

    return data_


def Get_ROI_BTC(start_date, end_date):

    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/historical'

    parameters = {
        'time_start': start_date,
        'time_end': end_date,
        'symbol': 'BTC',
        'interval': 'daily'
    }

    data_ = Get_Data(url, parameters, headers)

    return data_


def process_json(data_, id_list_):

    cluster1_data = []
    cluster2_data = []
    cluster3_data = []

    #id_list_ = {}
    name_dict = {}
    tokens_guardados = 0

    for i in range(len(data_['data'])):

        tag = data_['data'][i]['tags']

        if 'stablecoin' in tag:
            continue
        elif data_['data'][i]['symbol'] in ['BCHA', 'RAI', 'ROWAN', 'HT', 'vBUSD', 'vUSDT', 'vUSDC'] or "USD" in data_['data'][i]['symbol']:
            continue
        elif tokens_guardados == 500:
            break

        id_ = data_['data'][i]['id']
        name = data_['data'][i]['name'].lower()
        symbol = data_['data'][i]['symbol']
        price = data_['data'][i]['quote']['USD']['price']
        market_cap = data_['data'][i]['quote']['USD']['market_cap']

        cmk_rank = str(tokens_guardados+1)

        id_list_.update({symbol: id_})

        # Separo en Clusters
        if tokens_guardados < 10:

            cluster1_data.append((symbol, cmk_rank, price, market_cap, id_))

        elif tokens_guardados < 50:

            cluster2_data.append((symbol, cmk_rank, price, market_cap, id_))

        else:

            cluster3_data.append((symbol, cmk_rank, price, market_cap, id_))

        tokens_guardados += 1

    return cluster1_data, cluster2_data, cluster3_data

##### TOKENS/ CLUSTERS #####


def calculo_mkt_total(mkc_cap_data):

    mkc_total = 0
    for mkc in mkc_cap_data:
        mkc_total += mkc[3]
    return mkc_total


def update_token_amount(tokens_amount, cluster1_data, cluster2_data, cluster3_data, fecha):

    current_tokens = []
    tokens_to_sell = []
    data_ = cluster1_data + cluster2_data + cluster3_data

    for i in range(len(data_)):
        token_name = data_[i][4]
        current_tokens.append(token_name)

    tokens_to_sell = list(
        set([k for k, v in tokens_amount.items() if v != 0])-set(current_tokens))

    tokens_to_buy = list(set(current_tokens) - set(tokens_amount.keys()))

    ceros = [0] * len(tokens_to_buy)
    helper_dict = {}
    for k, v in zip(tokens_to_buy, ceros):
        helper_dict[k] = v

    return helper_dict, tokens_to_sell


def vender_sobrantes(date_, tokens_to_sell, tokens_amount_, id_list_):

    token_symbol = []

    for id_ in tokens_to_sell:

        try:
            token_symbol.append(list(id_list_.keys())[
                                list(id_list_.values()).index(int(id_))])
        except:
            continue

    new_fondos_bal = 0

    to_sell_dict = {key: [] for key in ['symbol', 'price', 'amount']}

    for symbol in token_symbol:

        symbol_token_to_sell = symbol

        data_to_sell = Get_Data_for_Token(date_, symbol)
        if 'data' not in data_to_sell.keys():

            precio_token_to_sell = 0
        else:

            key = list(data_to_sell['data'].keys())[0]
            precio_token_to_sell = data_to_sell['data'][key][0]['quotes'][0]['quote']['USD']['price']

        amount_token_to_sell = tokens_amount_[id_list_[symbol]]

        new_fondos_bal += 0.99 * (precio_token_to_sell * amount_token_to_sell)

        to_sell_dict['symbol'].append(symbol_token_to_sell)
        to_sell_dict['price'].append(precio_token_to_sell)
        to_sell_dict['amount'].append(amount_token_to_sell)

    time.sleep(len(token_symbol)/2)

    return new_fondos_bal, to_sell_dict


def process_fondos_init(fondo, porcentajes_a_repartir):
    """ Fondos inciales: inversion inicial, fondos para balancear"""

    fondos_cluster, fondos_bal = fondo * \
        (1-percent_fondos_bal), fondo * percent_fondos_bal

    cluster1_inv = fondos_cluster * porcentajes_a_repartir[0]

    cluster2_inv = fondos_cluster * porcentajes_a_repartir[1]

    cluster3_inv = fondos_cluster * porcentajes_a_repartir[2]

    return cluster1_inv, cluster2_inv, cluster3_inv, fondos_bal


def market_value_cluster(cluster1_data, cluster2_data, cluster3_data, tokens_amount):

    market_value_1 = 0
    for t in cluster1_data:
        market_value_1 += t[2] * tokens_amount[t[4]]

    market_value_2 = 0
    for t in cluster2_data:
        market_value_2 += t[2] * tokens_amount[t[4]]

    market_value_3 = 0
    for t in cluster3_data:
        market_value_3 += t[2] * tokens_amount[t[4]]

    return market_value_1, market_value_2, market_value_3


def balanceo(fondos_bal, market_value_1, market_value_2, market_value_3, min_exp, max_exp):

    market_value_total = market_value_1 + market_value_2 + market_value_3

    c1_percent = market_value_1 / market_value_total
    c2_percent = market_value_2 / market_value_total
    c3_percent = market_value_3 / market_value_total

    balance = fondos_bal / market_value_total

    if balance < min_exp:
        total = fondos_bal + market_value_total
        market_value_total = total / (1 + min_exp)
        fondos_bal = market_value_total * min_exp

        market_value_1 = market_value_total * c1_percent
        market_value_2 = market_value_total * c2_percent
        market_value_3 = market_value_total * c3_percent

    if balance > max_exp:
        total = fondos_bal + market_value_total
        market_value_total = total / (1 + max_exp)
        fondos_bal = market_value_total * max_exp

        market_value_1 = market_value_total * c1_percent
        market_value_2 = market_value_total * c2_percent
        market_value_3 = market_value_total * c3_percent

    return market_value_1, market_value_2, market_value_3, fondos_bal

##### METRICS, FILES #####


def save_Metrics(start_date, historical_clusters_, historical_fondos_balanceo_, historical_fondos_venta_):
    """Esta funcion calcula las metricas globales por fecha y separa las metricas de cada cluster"""

    Metrics_df = pd.DataFrame.from_dict({(i, j): historical_clusters_[i][j]
                                         for i in historical_clusters_.keys()
                                         for j in historical_clusters_[i].keys()},
                                        orient='index')

    Metrics_df.index.set_names(['Fecha', 'Cluster'], inplace=True)

    # Metricas globales solo se calculan el dia 5 del mes
    Global_metrics = Metrics_df.groupby(level=[0]).sum()

    # Convierto las fechas en columnas
    Global_metrics = Global_metrics.reset_index()

    # Convierto las fechas de STR -> DATETIME
    Global_metrics['Fecha'] = pd.to_datetime(
        Global_metrics['Fecha'], format='%Y-%m-%d')

    # Selecciono los dias 5 del mes
    if start_date.day == 5:
        Global_metrics = Global_metrics.loc[(Global_metrics.Fecha.dt.day == 5)]
    else:
        line = pd.DataFrame(Global_metrics.iloc[0].to_dict(), index=[0])
        # concatenate two dataframe
        filtered_dates = Global_metrics.loc[(Global_metrics.Fecha.dt.day == 5)]
        Global_metrics = pd.concat(
            [line, filtered_dates]).reset_index(drop=True)

    metrics_cluster3 = Metrics_df[Metrics_df.index.get_level_values(
        'Cluster').isin(['3'])].copy()
    metrics_cluster2 = Metrics_df[Metrics_df.index.get_level_values(
        'Cluster').isin(['2'])].copy()
    metrics_cluster1 = Metrics_df[Metrics_df.index.get_level_values(
        'Cluster').isin(['1'])].copy()

    #Roi * 100
    metrics_cluster3['roi'] = 100 * metrics_cluster3['roi']
    metrics_cluster2['roi'] = 100 * metrics_cluster2['roi']
    metrics_cluster1['roi'] = 100 * metrics_cluster1['roi']

    # Transac acc
    metrics_cluster3['transacciones acumuladas'] = metrics_cluster3['transacciones'].cumsum()
    metrics_cluster2['transacciones acumuladas'] = metrics_cluster2['transacciones'].cumsum()
    metrics_cluster1['transacciones acumuladas'] = metrics_cluster1['transacciones'].cumsum()
    Global_metrics['transacciones acumuladas'] = Global_metrics['transacciones'].cumsum()

    # costo acc
    metrics_cluster3['costo acumulado'] = metrics_cluster3['costo_operacion'].cumsum()
    metrics_cluster2['costo acumulado'] = metrics_cluster2['costo_operacion'].cumsum()
    metrics_cluster1['costo acumulado'] = metrics_cluster1['costo_operacion'].cumsum()
    Global_metrics['costo acumulado'] = Global_metrics['costo_operacion'].cumsum()

    historical_fondos_balanceo_df = pd.DataFrame(
        historical_fondos_balanceo_.items(), columns=['Fecha', 'Fondos_balanceo'])
    historical_fondos_venta_df = pd.DataFrame(
        historical_fondos_venta_.items(), columns=['Fecha', 'Fondos_venta'])

    Global_metrics['fondos_bal'] = historical_fondos_balanceo_df['Fondos_balanceo'] - \
        historical_fondos_venta_df['Fondos_venta']
    Global_metrics['fondos_venta'] = historical_fondos_venta_df['Fondos_venta']

    Global_metrics['roi'] = 100 * (Global_metrics['market_value'] /
                                   Global_metrics.loc[Global_metrics['Fecha'] == start_date.isoformat(), 'market_value'].values - 1)

    return Global_metrics.round(2), [metrics_cluster1.round(2), metrics_cluster2.round(2), metrics_cluster3.round(2)]


def save_Tokens(historical_tokens):
    """Genera dataframe por fecha con las coins segun el cluster"""

    data_fecha_cluster = {}

    for fecha in historical_tokens.keys():

        data_fecha_cluster[fecha] = {'1': None, '2': None, '3': None}

        to_df1 = {key: [] for key in ['name', 'rank', 'price', 'market_cap', 'amount',
                                      'operacion', 'variacion', 'market_value', 'cluster', 'roi', 'roi_acumulado']}
        to_df2 = {key: [] for key in ['name', 'rank', 'price', 'market_cap', 'amount',
                                      'operacion', 'variacion', 'market_value', 'cluster', 'roi', 'roi_acumulado']}
        to_df3 = {key: [] for key in ['name', 'rank', 'price', 'market_cap', 'amount',
                                      'operacion', 'variacion', 'market_value', 'cluster', 'roi', 'roi_acumulado']}

        for token, token_dict in historical_tokens[fecha].items():

            if token_dict['cluster'] == '1':

                to_df1['name'].append(token_dict['name'])
                to_df1['rank'].append(token_dict['rank'])
                to_df1['price'].append(token_dict['price'])
                to_df1['market_cap'].append(token_dict['market_cap'])
                to_df1['amount'].append(token_dict['amount'])
                to_df1['operacion'].append(token_dict['operacion'])
                to_df1['variacion'].append(token_dict['variacion'])
                to_df1['market_value'].append(token_dict['market_value'])
                to_df1['cluster'].append(token_dict['cluster'])
                to_df1['roi'].append(token_dict['roi'])
                to_df1['roi_acumulado'].append(token_dict['roi_acumulado'])

            elif token_dict['cluster'] == '2':

                to_df2['name'].append(token_dict['name'])
                to_df2['rank'].append(token_dict['rank'])
                to_df2['price'].append(token_dict['price'])
                to_df2['market_cap'].append(token_dict['market_cap'])
                to_df2['amount'].append(token_dict['amount'])
                to_df2['operacion'].append(token_dict['operacion'])
                to_df2['variacion'].append(token_dict['variacion'])
                to_df2['market_value'].append(token_dict['market_value'])
                to_df2['cluster'].append(token_dict['cluster'])
                to_df2['roi'].append(token_dict['roi'])
                to_df2['roi_acumulado'].append(token_dict['roi_acumulado'])

            else:

                to_df3['name'].append(token_dict['name'])
                to_df3['rank'].append(token_dict['rank'])
                to_df3['price'].append(token_dict['price'])
                to_df3['market_cap'].append(token_dict['market_cap'])
                to_df3['amount'].append(token_dict['amount'])
                to_df3['operacion'].append(token_dict['operacion'])
                to_df3['variacion'].append(token_dict['variacion'])
                to_df3['market_value'].append(token_dict['market_value'])
                to_df3['cluster'].append(token_dict['cluster'])
                to_df3['roi'].append(token_dict['roi'])
                to_df3['roi_acumulado'].append(token_dict['roi_acumulado'])

            data_fecha_cluster[fecha]['1'] = to_df1
            data_fecha_cluster[fecha]['2'] = to_df2
            data_fecha_cluster[fecha]['3'] = to_df3

    return data_fecha_cluster


def top_low_roi(historical_tokens, last_Date_roi_acc):

    # convierto a df
    to_df0 = {key: [] for key in ['id', 'roi_acumulado']}

    for id_, fecha in last_Date_roi_acc.items():

        to_df0['id'].append(id_)
        to_df0['roi_acumulado'].append(
            historical_tokens[fecha][id_]['roi_acumulado'])

    df = pd.DataFrame.from_dict(to_df0)

    top_25 = df.nlargest(25, 'roi_acumulado')['id'].values
    low_25 = df.nsmallest(25, 'roi_acumulado')['id'].values

    rank_dict = {}
    rank_top_25 = df.nlargest(
        25, 'roi_acumulado').reset_index().index.values + 1
    rank_low_25 = df.nsmallest(
        25, 'roi_acumulado').reset_index().index.values + 26
    ids_top = list(top_25)
    ids_low = list(low_25)

    roi_accumulado = {}

    ranks_top = list(rank_top_25)
    ranks_low = list(rank_low_25)

    for id_, rnk in zip(ids_top, ranks_top):
        rank_dict[id_] = rnk

    for id_, rnk in zip(ids_low, ranks_low):
        rank_dict[id_] = rnk

    data_token = {}
    data_token['top_25'] = {key: {key: [] for key in ['name', 'rank', 'price', 'market_cap', 'amount', 'operacion',
                                                      'variacion', 'market_value', 'cluster', 'roi', 'roi_acumulado', 'fecha', 'rank_roi']} for key in top_25}
    data_token['low_25'] = {key: {key: [] for key in ['name', 'rank', 'price', 'market_cap', 'amount', 'operacion',
                                                      'variacion', 'market_value', 'cluster', 'roi', 'roi_acumulado', 'fecha', 'rank_roi']} for key in low_25}

    for fecha in historical_tokens.keys():

        for id_, token_dict in historical_tokens[fecha].items():

            if id_ in top_25:

                data_token['top_25'][id_]['fecha'].append(fecha)
                data_token['top_25'][id_]['rank'].append(token_dict['rank'])
                data_token['top_25'][id_]['price'].append(token_dict['price'])
                data_token['top_25'][id_]['market_cap'].append(
                    token_dict['market_cap'])
                data_token['top_25'][id_]['amount'].append(
                    token_dict['amount'])
                data_token['top_25'][id_]['operacion'].append(
                    token_dict['operacion'])
                data_token['top_25'][id_]['variacion'].append(
                    token_dict['variacion'])
                data_token['top_25'][id_]['market_value'].append(
                    token_dict['market_value'])
                data_token['top_25'][id_]['cluster'].append(
                    token_dict['cluster'])
                data_token['top_25'][id_]['roi'].append(token_dict['roi'])
                data_token['top_25'][id_]['roi_acumulado'].append(
                    token_dict['roi_acumulado'])
                data_token['top_25'][id_]['rank_roi'].append(rank_dict[id_])
                data_token['top_25'][id_]['name'].append(token_dict['name'])

                roi_accumulado[token_dict['name']] = {'rank': rank_dict[id_],
                                                      'roi': token_dict['roi_acumulado']}

            if id_ in low_25:

                data_token['low_25'][id_]['fecha'].append(fecha)
                data_token['low_25'][id_]['rank'].append(token_dict['rank'])
                data_token['low_25'][id_]['price'].append(token_dict['price'])
                data_token['low_25'][id_]['market_cap'].append(
                    token_dict['market_cap'])
                data_token['low_25'][id_]['amount'].append(
                    token_dict['amount'])
                data_token['low_25'][id_]['operacion'].append(
                    token_dict['operacion'])
                data_token['low_25'][id_]['variacion'].append(
                    token_dict['variacion'])
                data_token['low_25'][id_]['market_value'].append(
                    token_dict['market_value'])
                data_token['low_25'][id_]['cluster'].append(
                    token_dict['cluster'])
                data_token['low_25'][id_]['roi'].append(token_dict['roi'])
                data_token['low_25'][id_]['roi_acumulado'].append(
                    token_dict['roi_acumulado'])
                data_token['low_25'][id_]['rank_roi'].append(rank_dict[id_])
                data_token['low_25'][id_]['name'].append(token_dict['name'])

                roi_accumulado[token_dict['name']] = {'rank': rank_dict[id_],
                                                      # 'name': token_dict['name'],
                                                      'roi': token_dict['roi_acumulado']}

    return data_token['top_25'], data_token['low_25'], roi_accumulado


def roi_btc(data_):

    roi_btc = {}
    precio_btc = {}

    for i in range(len(data_['data']['BTC'][0]['quotes'])):
        fecha = data_['data']['BTC'][0]['quotes'][i]['quote']['USD']['timestamp'].split('T')[
            0]
        precio_actual = data_[
            'data']['BTC'][0]['quotes'][i]['quote']['USD']['price']

        if len(roi_btc) == 0:
            btc_amount = 100 / precio_actual
            # roi_btc[fecha] = 1
            #print(f'Buy {btc_amount} BTC with 1USD')
            # print(ROI)

        roi_btc[fecha] = (btc_amount * precio_actual / 100) - 1
        precio_btc[fecha] = precio_actual

    df_roi_btc = pd.DataFrame(roi_btc.items(), columns=['Fecha', 'ROI_BTC'])

    return df_roi_btc


def create_files(dirName, estrategia, Global_metrics, cluster_metrics, data_fecha_cluster, data_token_top, data_token_low, historical_fondos_balanceo, df_roi_btc, roi_accumulado_top_low_):

    df_roi_btc.to_csv(f'{dirName}/ROI_BTC.csv', index=False)

    # Carpeta CLUSTERS
    dirName = dirName + '/' + estrategia
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    Global_metrics.to_csv(f'{dirName}/Metricas_Globales.csv')
    roi_accumulado_top_low_ = pd.DataFrame.from_dict(
        roi_accumulado_top_low_, orient='index').sort_values(by='rank')
    roi_accumulado_top_low_.to_csv(f'{dirName}/roi.csv')

    subdir_name = 'top_25'
    if not os.path.exists(dirName+'/'+subdir_name):
        os.mkdir(dirName+'/'+subdir_name)

    subdir_name = 'low_25'
    if not os.path.exists(dirName+'/'+subdir_name):
        os.mkdir(dirName+'/'+subdir_name)

    for id_, values in data_token_top.items():
        rnk = values['rank_roi'][0]
        df = pd.DataFrame.from_dict(values)
        df.to_csv(f'{dirName}/top_25/{rnk}.csv')

    for id_, values in data_token_low.items():
        rnk = values['rank_roi'][0]
        df = pd.DataFrame.from_dict(values)
        df.to_csv(f'{dirName}/low_25/{rnk}.csv')

    # Carpeta de cada Cluster
    for i in range(1, 4):
        subdir_name = 'Cluster' + str(i)
        # print('\t/'+subdir_name)
        if not os.path.exists(dirName+'/'+subdir_name):
            os.mkdir(dirName+'/'+subdir_name)

        # Save de metricas por cluster
        cluster_metrics[i -
                        1].to_csv(f'{dirName}/{subdir_name}/Metricas_cluster{i}.csv')

        # print('\t\t/Fechas')
        if not os.path.exists(dirName+'/'+subdir_name+'/Fechas'):
            os.mkdir(dirName+'/'+subdir_name+'/Fechas')

        for fecha in data_fecha_cluster.keys():
            if (str(i) == '1' and fecha.split('-')[2] != '05'):
                continue
            df = pd.DataFrame.from_dict(data_fecha_cluster[fecha][str(i)])
            df.to_csv(f'{dirName}/{subdir_name}/Fechas/{fecha}.csv')

    if not os.path.exists(dirName+'/ventas'):
        os.mkdir(dirName+'/ventas')

    for fecha, values in historical_fondos_balanceo.items():
        df = pd.DataFrame.from_dict(values)
        df.to_csv(f'{dirName}/ventas/{fecha}.csv')
