import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter 
import matplotlib.dates as mdates
import os


class Grafica:

  def __init__(self,path, primera_fecha, estrategia):

    self.path = path + '/' + primera_fecha + '/' + estrategia
    self.path_dir = path + '/' + primera_fecha
    self.estrategia = estrategia

    self.cluster1()
    self.cluster2()
    self.cluster3()
    
    self.total()

    self.btc()
    
    self.lott()

  def __plott__(self, tipo):

    fig, ax = plt.subplots(figsize=(25,10))

    
    if (tipo =='top_10' or tipo =='low_10'):

      colors = ['red', 'blue', 'green', 'pink', 'orange', 'black', 'purple', 'brown', 'cyan', 'olive']
      
      for df, rank in zip(self.df_list, self.rank_list):
        
        ax.plot(df.fecha, df.roi_acumulado, color=colors[rank-1], label=df.name[0], linewidth=2, linestyle="--")

    elif tipo == "Precio": 

      ax.plot(self.df_lott.Fecha, self.df_lott[tipo], color='green', label= 'LOTT Price', linewidth=4, linestyle="-")

    elif tipo == "Cantidad":

      ax.plot(self.df_lott.Fecha, self.df_lott[tipo], color='orange', label= 'LOTT Cantidad', linewidth=4, linestyle="-")

    elif tipo == "fondos_bal":

      ax.plot(self.df_global.Fecha, self.df_global[tipo], color='black', label='Total', linewidth=4, linestyle="-")

    else:

      ax.plot(self.df_cluster_1.Fecha, self.df_cluster_1[tipo], color='red', label='cluster 1', linewidth=3, linestyle="--")
      ax.plot(self.df_cluster_2.Fecha, self.df_cluster_2[tipo], color='blue', label='cluster 2', linewidth=3, linestyle="--")
      ax.plot(self.df_cluster_3.Fecha, self.df_cluster_3[tipo], color='green', label='cluster 3', linewidth=3, linestyle="--")

    
      ax.plot(self.df_global.Fecha, self.df_global[tipo], color='black', label='Total', linewidth=4, linestyle="-")

      if tipo == "roi":

        ax.plot(self.df_btc.Fecha, self.df_btc.roi, color='orange', label='BTC', linewidth=4, linestyle="-")


    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=5))
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

    # Add legend
    plt.legend(fontsize=15)

    # Fontsizes
    plt.title(label=f"{tipo} ({self.estrategia})", fontsize=20)
    plt.yticks(fontsize=14)
    #plt.ylabel(ylabel=f"{tipo}", fontsize=17)
    plt.xlabel(xlabel="Fecha", fontsize=17)
    plt.xticks( fontsize=12)

    fig.autofmt_xdate()

    # Display plot
    plt.show() 


  def __formatt__(self, df):
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    #df['roi'] = df['roi'] * 100
    return df

  def __cumm__(self, df):
    df['transacciones_acumuladas'] = df['transacciones'].cumsum()
    df['costo_acumulado'] = df['costo_operacion'].cumsum()
    return df


  def cluster1(self):
    # cargo los datos
    self.df_cluster_1 = pd.read_csv(self.path + '/' + 'Cluster1' + '/' + 'Metricas_cluster1.csv', dtype={'market_value' : 'float64', 'costo_operacion':'float64', 'transacciones': 'int64', 'roi': 'float64', 'ganancia': 'float64', 'transacciones acumuladas' : 'float64', 'costo acumulado' : 'float64'})
    # formateo datos
    self.df_cluster_1 = self.__formatt__(self.df_cluster_1)


  def cluster2(self):
    # cargo los datos
    self.df_cluster_2 = pd.read_csv(self.path + '/' + 'Cluster2'+ '/' + 'Metricas_cluster2.csv', dtype={'market_value' : 'float64', 'costo_operacion':'float64', 'transacciones': 'int64', 'roi': 'float64', 'ganancia': 'float64', 'transacciones acumuladas' : 'float64', 'costo acumulado' : 'float64'})
    # formateo datos
    self.df_cluster_2 = self.__formatt__(self.df_cluster_2)

  
  def cluster3(self):
    # cargo los datos
    self.df_cluster_3 = pd.read_csv(self.path + '/' + 'Cluster3'+ '/' + 'Metricas_cluster3.csv', dtype={'market_value' : 'float64', 'costo_operacion':'float64', 'transacciones': 'int64', 'roi': 'float64', 'ganancia': 'float64', 'transacciones acumuladas' : 'float64', 'costo acumulado' : 'float64'})
    # formateo datos
    self.df_cluster_3 = self.__formatt__(self.df_cluster_3)


  def total(self):
    self.df_global = pd.read_csv(self.path + '/' + 'Metricas_Globales.csv', index_col=0, parse_dates = [1], dtype={'market_value' : 'float64', 'transacciones': 'int64', 'roi': 'float64', 'ganancia': 'float64', 'transacciones acumuladas' : 'float64', 'costo acumulado' : 'float64', 'fondos_bal':'float64'})
    # formateo datos
    self.df_global = self.__formatt__(self.df_global)


  def btc(self):
    self.df_btc = pd.read_csv(self.path_dir + '/' + 'ROI_BTC.csv')
    self.df_btc['Fecha'] = pd.to_datetime(self.df_btc['Fecha'])
    self.df_btc['roi'] = self.df_btc['ROI_BTC'] * 100



  def lott(self):
    self.df_lott = pd.read_csv(self.path + '/' + 'lott.csv', dtype={'Precio': 'float64', 'Cantidad': 'float64'})    
    self.df_lott['Fecha'] = pd.to_datetime(self.df_lott['Fecha'])
    self.df_lott['Precio'] = round(self.df_lott['Precio'], 3)
    self.df_lott['Cantidad'] = round(self.df_lott['Cantidad'], 3)
    #self.__plott__("lott_price")
    
  #def lott_cantidad(self):
    #self.df_lott_cantidad = pd.read_csv(self.path + '/' + 'lott.csv', dtype={'Precio': 'float64', 'Cantidad':'float64'})    
    #self.df_lott_cantidad['Fecha'] = pd.to_datetime(self.df_lott_cantidad['Fecha'])
    #self.df_lott_cantidad['Cantidad'] = round(self.df_lott_cantidad['Cantidad'], 3)
    #self.__plott__("lott_cantidad")

  def roi(self):
    self.__plott__("roi")

  def fondos_balanceo(self):
    self.__plott__("fondos_bal")

  def transacciones_acumuladas(self):
    self.__plott__("transacciones acumuladas")

  def costo_acumulado(self):
    self.__plott__("costo acumulado")
    
  def ganancia(self):
    self.__plott__("ganancia")
  
  def lott_price(self):  
    self.__plott__("Precio")
    
  def lott_cantidad(self):
    self.__plott__("Cantidad")

  def top_10(self):

    top_25_dir = self.path + '/' + 'top_25'

    self.df_list = []
    self.rank_list = []
    
    for filename in os.listdir(top_25_dir):
      f = os.path.join(top_25_dir, filename)
      rank = int(filename.split('.')[0])
      self.rank_list.append(rank)
      
      df = pd.read_csv(f, dtype={'roi_acumulado' : 'float64'})
      df['fecha'] = pd.to_datetime(df['fecha'])
      self.df_list.append(df)

      if rank == 10:
        break

    self.__plott__("top_10")

  def low_10(self):

    low_25_dir = self.path + '/' + 'low_25'

    self.df_list = []
    self.rank_list = []
    
    for filename in os.listdir(low_25_dir):
      f = os.path.join(low_25_dir, filename)
      rank = int(filename.split('.')[0])-25
      self.rank_list.append(rank)
      
      df = pd.read_csv(f, dtype={'roi_acumulado' : 'float64'})
      df['fecha'] = pd.to_datetime(df['fecha'])
      self.df_list.append(df)

      if rank == 10:
        break

    self.__plott__("low_10")
    
class GraficaEstrategias():
  
  def __init__(self, *args: Grafica):

    self.args = list(args)

    self.estrategias = len(self.args)


  def __plott__(self, tipo):

    fig, ax = plt.subplots(figsize=(25,10))

    
    colors = ['red', 'blue', 'green']
    
    if tipo == "LOTT Price":
      
      for i in range(self.estrategias):
        
        ax.plot(self.args[i].df_lott.Fecha, self.args[i].df_lott.Precio, color=colors[i], label=self.args[i].estrategia, linewidth=3, linestyle="-")
    
    elif tipo == "LOTT Cantidad":
      
      for i in range(self.estrategias):
        
        ax.plot(self.args[i].df_lott.Fecha, self.args[i].df_lott.Cantidad, color=colors[i], label=self.args[i].estrategia, linewidth=3, linestyle="-")

    else:
      
      for i in range(self.estrategias):
        
        ax.plot(self.args[i].df_global.Fecha, self.args[i].df_global[tipo], color=colors[i], label=self.args[i].estrategia, linewidth=3, linestyle="-")
        
      if tipo == "roi":

        ax.plot(self.args[0].df_btc.Fecha, self.args[0].df_btc.roi, color='orange', label='BTC', linewidth=4, linestyle="-")
        
        
        
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=5))
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))


    plt.legend(fontsize=15)
    plt.title(label=f"{tipo}", fontsize=20)
    plt.yticks(fontsize=14)
    #plt.ylabel(ylabel=f"{tipo}", fontsize=17)
    plt.xlabel(xlabel="Fecha", fontsize=17)
    plt.xticks( fontsize=12)

    fig.autofmt_xdate()

    plt.show()

  def roi(self):
    self.__plott__("roi")

  def fondos_balanceo(self):
    self.__plott__("fondos_bal")

  def transacciones_acumuladas(self):
    self.__plott__("transacciones acumuladas")

  def costo_acumulado(self):
    self.__plott__("costo acumulado")
    
  def ganancia_acumulada(self):
    self.__plott__("ganancia acumulada")

  def lott_price(self):
    self.__plott__("LOTT Price")
    
  def lott_cantidad(self):
    self.__plott__("LOTT Cantidad")
    
