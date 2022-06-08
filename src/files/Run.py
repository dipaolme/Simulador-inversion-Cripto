# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
from tqdm.notebook import tqdm
from Classes import Cluster, Token
from Utils import *
from datetime import date, timedelta
from Config import *


def main(fecha_inicio, fecha_final, fondos, estrategia, tolerancia_balanceo, exposicion, porcentajes_a_repartir):

    start_date = date(fecha_inicio[0], fecha_inicio[1], fecha_inicio[2])
    end_date = date(fecha_final[0], fecha_final[1], fecha_final[2])
    delta = end_date - start_date

    # archivo contenedor

    dirName = start_date.strftime("%Y-%m-%d")
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    dirName_2 = f'{dirName}/{estrategia}'
    if not os.path.exists(dirName_2):
        os.mkdir(dirName_2)

    # Estructura de datos

    # dict para guardar datos de cada cluster
    clusters = {'1': {}, '2': {}, '3': {}}

    historical_clusters = {}
    historical_tokens = {}
    tokens_amount = {}
    last_Date_roi_acc = {}
    historical_fondos_balanceo = {}
    id_list = {}

    historical_tokens_venta = {}
    historical_fondos_venta = {}

    # {fecha:token} dict con la fecha que fue incorporado el token al top 500
    new_token = {}

    # fechas que no encontro datos
    fechas = []

    cant_tokens = '550'

    estrategia = estrategia

    tolerancia_balanceo = tolerancia_balanceo

    exposicion = exposicion

    min_exp = exposicion[0]
    max_exp = exposicion[1]

    clusters['1']['tolerancia_balanceo'] = tolerancia_balanceo[0]
    clusters['2']['tolerancia_balanceo'] = tolerancia_balanceo[1]
    clusters['3']['tolerancia_balanceo'] = tolerancia_balanceo[2]

    clusters['1']['fondos_inv'] = {}
    clusters['2']['fondos_inv'] = {}
    clusters['3']['fondos_inv'] = {}

    fondos = fondos

    # contador
    n_iter = 0

    for single_date in tqdm(daterange(start_date, end_date), total=delta.days):

        if single_date == start_date:
            print('Start Date: ', single_date.strftime("%Y-%m-%d"))
            fecha = single_date.isoformat()

            historical_clusters[fecha] = {}
            historical_tokens[fecha] = {}
            historical_fondos_balanceo[fecha] = {}

            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/historical'
            parameters = {'date': fecha,
                          'convert': 'USD', 'limit': cant_tokens}

            data = Get_Data(url, parameters, headers)

            try:
                len(data['data']) == int(cant_tokens)
            except:
                print(f'Fecha {fecha}: DATOS FALTANTES')
                fechas.append(fecha)
                continue

            # obtengo data del json de c/ cluster
            cluster1_data, cluster2_data, cluster3_data = process_json(
                data, id_list)

            clusters['1']['data'] = cluster1_data
            clusters['2']['data'] = cluster2_data
            clusters['3']['data'] = cluster3_data

            save_raw_csv(dirName, fecha, cluster1_data,
                         cluster2_data, cluster3_data)

            # distribucion de fondos
            cluster1_fondos, cluster2_fondos, cluster3_fondos, fondos_bal = process_fondos_init(
                fondos, porcentajes_a_repartir)

            clusters['1']['fondos_init'] = cluster1_fondos
            clusters['2']['fondos_init'] = cluster2_fondos
            clusters['3']['fondos_init'] = cluster3_fondos

            historical_fondos_balanceo[fecha] = fondos_bal

            for c in clusters.keys():

                if c == '1':
                    ultima_fecha_cluster1 = fecha

                # instancio los tokens
                tokens = [Token(t[0], t[1], t[2], t[3], t[4], c)
                          for t in clusters[c]['data']]

                #suma_porcentaje_market_cap = 0

                for t in tokens:

                    # hago la compra incial
                    t.token_amount(clusters[c]['fondos_init'])
                    # calculo market_value (precio x amount)
                    t.mkt_value()

                    # guardo los cambios en historical_tokens
                    historical_tokens[fecha][t.name] = {}
                    historical_tokens[fecha][t.name]['name'] = t.nombre
                    historical_tokens[fecha][t.name]['rank'] = t.cmk_rank
                    historical_tokens[fecha][t.name]['price'] = t.price
                    historical_tokens[fecha][t.name]['market_cap'] = t.market_cap
                    historical_tokens[fecha][t.name]['amount'] = t.amount
                    historical_tokens[fecha][t.name]['operacion'] = t.operacion
                    historical_tokens[fecha][t.name]['variacion'] = t.variacion
                    historical_tokens[fecha][t.name]['market_value'] = t.price * t.amount
                    historical_tokens[fecha][t.name]['cluster'] = t.cluster
                    historical_tokens[fecha][t.name]['roi'] = 0
                    historical_tokens[fecha][t.name]['roi_acumulado'] = 0

                    # ultima fecha que se calculo el roi acumulado para cada token
                    last_Date_roi_acc[t.name] = fecha

                    # actualizo el amount de cada token
                    tokens_amount[t.name] = t.amount

                    # como es la primera fecha todos los tokens son nuevos
                    new_token[t.name] = fecha

                cluster = Cluster(c, clusters[c]['fondos_init'], historical_fondos_balanceo[fecha],
                                  clusters[c]['tolerancia_balanceo'], tokens, first_day=True)

                # guardo los cambios en historical_cluster
                historical_clusters[fecha][c] = {}
                historical_clusters[fecha][c]['market_value'] = cluster.mkt_value(
                )
                historical_clusters[fecha][c]['costo_operacion'] = cluster.mkt_value(
                ) * 0.001
                historical_clusters[fecha][c]['transacciones'] = cluster.transacciones
                historical_clusters[fecha][c]['roi'] = round(
                    cluster.mkt_value() / clusters[c]['fondos_init'] - 1, 2)
                historical_clusters[fecha][c]['ganancia'] = 0

                historical_fondos_balanceo[fecha] = cluster.fondos_bal - \
                    historical_clusters[fecha][c]['costo_operacion']

            historical_fondos_venta[fecha] = 0

        else:

            # Update solo funciona dias 5
            if single_date.day != dia_inversion:
                continue

            dia_anterior = fecha
            fecha = single_date.isoformat()
            print('\r', end=f'Fecha: {fecha}')

            historical_clusters[fecha] = {}
            historical_tokens[fecha] = {}
            historical_fondos_balanceo[fecha] = {}
            historical_tokens_venta[fecha] = {}
            historical_fondos_venta[fecha] = {}
            #betf[fecha] = {}

            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/historical'
            parameters = {'date': fecha,
                          'convert': 'USD', 'limit': cant_tokens}

            data = Get_Data(url, parameters, headers)

            try:
                len(data['data']) == int(cant_tokens)
            except:
                print(f'Fecha {fecha}: DATOS FALTANTES\n', data)
                fechas.append(fecha)
                fecha = dia_anterior
                continue

            cluster1_data, cluster2_data, cluster3_data = process_json(
                data, id_list)

            # Completo los clusters con la data
            clusters['1']['data'] = cluster1_data
            clusters['2']['data'] = cluster2_data
            clusters['3']['data'] = cluster3_data

            save_raw_csv(dirName, fecha, cluster1_data,
                         cluster2_data, cluster3_data)

            # actualiza la lista con los nuevos tokens/lista de tokens que se deben vender
            tokens2update, tokens_to_sell = update_token_amount(
                tokens_amount, cluster1_data, cluster2_data, cluster3_data, fecha)

            # fecha de compra de los nuevos tokens
            new_token.update({k: fecha for k in tokens2update.keys()})

            # Actualizo el token amount con los tokens nuevos en 0
            tokens_amount.update(tokens2update)

            ####### market value actual #######

            mktv_c1, mktv_c2, mktv_c3 = market_value_cluster(
                cluster1_data, cluster2_data, cluster3_data, tokens_amount)

            ####### balanceo / fondos/ tokens lott #######
            fondos_1, fondos_2, fondos_3, f_bal = balanceo(
                historical_fondos_balanceo[dia_anterior], mktv_c1, mktv_c2, mktv_c3, min_exp, max_exp)

            clusters['1']['fondos_inv'][fecha] = fondos_1
            clusters['2']['fondos_inv'][fecha] = fondos_2
            clusters['3']['fondos_inv'][fecha] = fondos_3

            historical_fondos_balanceo[fecha] = f_bal

            for c in clusters.keys():

                # instancio los tokens
                tokens = [Token(t[0], t[1], t[2], t[3], t[4], c,
                                amount=tokens_amount[t[4]]) for t in clusters[c]['data']]

                cluster = Cluster(c, clusters[c]['fondos_inv'][fecha], historical_fondos_balanceo[fecha],
                                  clusters[c]['tolerancia_balanceo'], tokens, first_day=False)

                # calcula los nuevos amount luego del rebalanceo
                cluster.new_token_amount()

                # guardo los cambios en historical_cluster
                historical_clusters[fecha][c] = {}

                historical_clusters[fecha][c]['market_value'] = cluster.mkt_value(
                )
                historical_clusters[fecha][c]['transacciones'] = cluster.transacciones
                historical_clusters[fecha][c]['roi'] = cluster.mkt_value(
                ) / historical_clusters[start_date.isoformat()][c]['market_value'] - 1
                historical_clusters[fecha][c]['ganancia'] = cluster.mkt_value(
                ) - clusters[c]['fondos_init']
                historical_clusters[fecha][c]['costo_operacion'] = cluster.costo_operacion

                historical_fondos_balanceo[fecha] = cluster.fondos_bal

                # vendo los tokens que ya no se encuentran en el top 500, sumo la plata obtenida a los fondos de balanceo para el proximo ciclo
                if (len(tokens_to_sell) != 0 and c == '3'):
                    fondo_bal_Extra, to_sell_dict = vender_sobrantes(
                        single_date, tokens_to_sell, tokens_amount, id_list)

                    # tokens a vender
                    historical_tokens_venta[fecha] = to_sell_dict

                    historical_clusters[fecha][c]['transacciones'] += len(
                        tokens_to_sell)

                    for token in tokens_to_sell:
                        # pongo en 0 los tokens vendidos
                        tokens_amount[token] = 0

                    # sumo las ventas al fondo de balanceo
                    historical_fondos_balanceo[fecha] += fondo_bal_Extra

                    # ingresos generados por las ventas
                    historical_fondos_venta[fecha] = fondo_bal_Extra


                for t in tokens:

                    historical_tokens[fecha][t.name] = {}
                    historical_tokens[fecha][t.name]['name'] = t.nombre
                    historical_tokens[fecha][t.name]['rank'] = t.cmk_rank
                    historical_tokens[fecha][t.name]['price'] = t.price
                    historical_tokens[fecha][t.name]['market_cap'] = t.market_cap
                    historical_tokens[fecha][t.name]['amount'] = t.amount
                    historical_tokens[fecha][t.name]['operacion'] = t.operacion
                    historical_tokens[fecha][t.name]['variacion'] = t.variacion
                    historical_tokens[fecha][t.name]['market_value'] = t.price * t.amount
                    historical_tokens[fecha][t.name]['cluster'] = t.cluster

                    if new_token[t.name] == fecha:
                        historical_tokens[fecha][t.name]['roi'] = 0
                        historical_tokens[fecha][t.name]['roi_acumulado'] = 0
                    else:
                        historical_tokens[fecha][t.name]['roi'] = t.mkt_value(
                        ) / historical_tokens[new_token[t.name]][t.name]['market_value'] - 1
                        if t.name in last_Date_roi_acc.keys():
                            historical_tokens[fecha][t.name]['roi_acumulado'] = historical_tokens[fecha][t.name]['roi'] + \
                                historical_tokens[last_Date_roi_acc[t.name]
                                                  ][t.name]['roi_acumulado']
                        else:
                            historical_tokens[fecha][t.name]['roi_acumulado'] = 0
                        last_Date_roi_acc[t.name] = fecha

                    # Update tokens_amount
                    tokens_amount[t.name] = t.amount

            time.sleep(1)

        n_iter += 1
        if n_iter % 90 == 0:
            print("STOP! Time for a nap...")
            time.sleep(20)
            print("OK... READY LETS GO!")

    data_fecha_cluster = save_Tokens(historical_tokens)

    data_token_top, data_token_low, roi_accumulado_top_low = top_low_roi(
        historical_tokens, last_Date_roi_acc)

    Global_metrics, cluster_metrics = save_Metrics(
        start_date, historical_clusters, historical_fondos_balanceo, historical_fondos_venta)

    data_ROI_BTC = Get_ROI_BTC(start_date, end_date)

    df_roi_btc = roi_btc(data_ROI_BTC)

    create_files(dirName, estrategia, Global_metrics, cluster_metrics, data_fecha_cluster, data_token_top,
                 data_token_low, historical_tokens_venta, df_roi_btc, roi_accumulado_top_low)

    with open(f'{dirName}/{estrategia}/log_{estrategia}.txt', 'w') as f:
        f.write('Tipo: mensual' + "\n" +
                'Estrategia: ' + estrategia + "\n" +
                'Fondos: ' + str(fondos) + "\n" +
                'tolerancia_balanceo Cluster 1: ' + str(tolerancia_balanceo[0]) + "\n" +
                'tolerancia_balanceo Cluster 2: ' + str(tolerancia_balanceo[1]) + "\n" +
                'tolerancia_balanceo Cluster 3: ' + str(tolerancia_balanceo[2]) + "\n" +
                'Exposicion minima: ' + str(exposicion[0]) + "\n" +
                'Exposicion maxima: ' + str(exposicion[1]) + "\n" +
                'Porcentaje del fondo invertido Cluster 1:' + str(porcentajes_a_repartir[0]) + "\n" +
                'Porcentaje del fondo invertido Cluster 2:' + str(porcentajes_a_repartir[1]) + "\n" +
                'Porcentaje del fondo invertido Cluster 3:' +
                str(porcentajes_a_repartir[2]) + "\n"
                )


if __name__ == '__main__':

    fecha_inicio = (2021, 7, 5)
    fecha_final = (2022, 6, 6)
    fondos = 100000
    porcentajes_a_repartir = [0.2, 0.2, 0.6]
    tolerancia_balanceo = [0.05, 0.1, 0.2]
    exposicion = [0.1, 0.2]
    estrategia = "estrategia_2"

    main(fecha_inicio, fecha_final, fondos, estrategia,
         tolerancia_balanceo, exposicion, porcentajes_a_repartir)
