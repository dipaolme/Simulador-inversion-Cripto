# Simulador de Inversion Cripto

Simulacion de inversion en las 500 criptomonedas con mayor capitalizacion 
    de mercado mensual a lo largo de 11 meses.

## Autores
- [@matiasdipaola](https://github.com/dipaolme)
- [@gastonaraujo]()

### Motivacion
En un mercado *joven* como el Cripto, la tendencia en el mediano plazo es 
    que la capitalizacion total de mercado siga en aumento a pesar de la alta 
    volatilidad.

A diferencia de una estrategia donde se estudia y elige invertir en unos 
    pocos proyectos/criptomonedas, aqui se intenta simular una inversion 
    mensual basado exclusivamente en las 500 monedas de mayor  capitalizacion 
    de mercado para cada mes.

La idea es que el mercado eventualmente crecera, segmentar la inversion 
    permite resguardar el capital en las criptomonedas de mayor capitalizacion 
    y a la vez capturar y beneficiarse de aquellas con bajo capitalizacion pero 
    con un potencial de crecimiento y retorno mayor.

## Estrategia

* Las 500 criptomonedas se dividen y agrupan en  3 clusters:

    * Las **10** primeras del ranking en el **cluster 1**
    * Las **40** siguientes en el **cluster 2**
    * Las **450** restantes en el **cluster 3**

* El ranking que ocupe la criptomoneda en ese mes determinara 
    el porcentaje del fondo/valor del cluster que se le asigne. 
    Los porcentajes sumados representan el 100% del fondo y  se mantienen 
    constantes durante todo el ejercicio.

* Se crea ademas un **Fondo de Balanceo**, y se define la **Exposicion**  
    que tendra respecto a los clusters previamente definidos. 
    Esto permite mantener el valor de los clusters en un determinado rango 
    de porcentajes repecto a dicho fondo, de esta manera si el valor de 
    mercado sufre una baja considerable se podran inyectar 
    fondos y comprar mas tokens,  y viceversa (se venden tokens) para 
    generar liquidez.
* El primer mes, se distribuye, de acuerdo a un **porcentaje de inversion**, 
    la cantidad de del fondo que recibira cada cluster. El fondo de blanceo, 
    por default se le asigna el 10% de lo invertido. Luego se realizan las 
    compras de las criptomonedas segun el ranking que ocupen en cada cluster 
    (ver tablas mas abajo).

* A partir del segundo mes
    * Se realiza el balanceo entre los cluster y el fondo de balanceo, segun 
    la exposicion definida previamente. El valor del cluster se calcula como 
    la suma de la cantidad disponible de cada criptomoneda que compone el 
    cluster multiplicada por su precio actual.
    * Las criptomonedas nuevas se les asiganara el porcentaje correspondiente
    para su compra de acuerdo a la posicion que ocupen.
    * Las que permanecen dentro del ranking, a partir de la cantidad 
    acumulada del mes anterior, el precio actual y el puesto que ocupen 
    se procedera a la venta/compra parcial para mantener los porcentajes 
    asigandos. Ademas se define una **Tolerancia de Balanceo**, es la variacion 
    porcentual tolerada del token respecto al mes anterior, en ese caso no se 
    realizara la compra/venta. 
    * Por ultimo las criptomonedas que salen del ranking (>500) se venderan 
    a precio de mercado  y los fondos generados se 
    suman al **Fondo de Balanceo** 

* Cada compra/venta tiene un **costo** de **0.01%** de 
    la operacion. Este monto se descuenta del Fondo de Balanceo.



### Requerimientos

Se requiere tener una suscripcion **"PROFESSIONAL"** a la 
    API de *Coinmarketcap*, ya que permite acceder a 12 meses de data historica.

Igualmente todos los datos utilizados  se encuentran guardados en 
    archivos '.csv' si se quieren realizar corridas en las mismas fechas.

### Variables Globales

Dentro del archivo *Config.py* se podra setear:

* KEY provista por Coinmarketcap
* % inversion segun cluster/ranking (ver ejemplo abajo)
* % asignado al Fondo de Balanceo
* dia del mes de la inversion

### % a invertir segun ranking de Cap. Mercado en cada cluster


**Cluster 1**

| Ranking / Posicion  | % inversion |    
| :-: |  :-: |   
|  1  | 14.5 |
|  2  | 13.5 |
| ... |  ... |
|  9  |  6.5 |
|  10 |  5.5 |

**Cluster 2**

| Ranking / Posicion  | % inversion |    
| :-: | :-: |   
|  11 | 3.7 |
|  12 | 3.6 |
| ... | ... |
|  49 | 1.34 |
|  50 | 1.28 |

**Cluster 3**

| sub-cluster | Ranking / Posicion  | % inversion |    
|:---:|   :-:   | :-:  |   
|  1  |  51- 80 | 11.3 |
|  2  | 81- 110 | 11.3 |
| ... |   ...   |  ... |
| 14  |441- 470 | 11.3 |
|  15 |471- 500 |   2  |

*\*Se agrupa en en 15 subclusters compuesto de 30 monedas cada uno por cuestion de espacio*

### Parametros de corrida

Ejemplo de parametros de 2 estrategias 

    fecha_inicio = (2021, 7, 5)                    # el dia tiene que coincidir con el dia seleccionado para la inversion
    fecha_final = (2022, 6, 6)                     # el dia tiene que ser un dia despues del seleccionado para la inversion
    fondos = 100000                                # inversion que se desea realizar    
    porcentajes_a_repartir = [0.3, 0.3, 0.4]       # que porcentaje recibira cada cluster, previamente descontando el % al fondo de balanceo
    tolerancia_balanceo = [0.02, 0.02, 0.02]       # variacion maxima tolerada de la cantidad de tokens respecto al mes anterior 
    exposicion = [0.1, 0.2]                        # exposicion mini y max del fondo de balanceo respecto a los clusters  
    estrategia = "estrategia_1"                    # nombre de la estrategia   

    fecha_inicio = (2021, 6, 5)
    fecha_final = (2021, 12, 6)
    fondos = 100000
    porcentajes_a_repartir = [0.2, 0.2, 0.6]
    tolerancia_balanceo = [0.05, 0.1, 0.2]
    exposicion = [0.1, 0.2]
    estrategia = "estrategia_2"

### Resultados

La corrida genera una carpeta con el nombre de la fecha incial elegida, 
y dentro una carpeta para cada estrategia (si hubo mas de una).

Ademas de una carpeta para cada cluster con sus metricas,  se entcontrara:

* top 25 Criptomonedas con mayor roi acumulado
* top 25 Criptomonedas con mayor roi acumulado
* ventas de los tokens que salieron del ranking


#### Metricas

Se calculan para cada cluster y kuego se agrupan en una tabla global, algunas son:

*market value* : Cantidad * Precio

*ganancia* : market value - inversion inicial

*roi* : ( market value - inversion inicial ) /  inversion inicial  * 100


### Graficos

Por estrategia se puede graficar:

*roi, fondos_balance, transacciones_acumulada, costo_acumulado, top_10, low_10*

![roi](https://github.com/dipaolme/Simulador-de-inversion-Cripto/blob/main/imagenes/roi.png))






Se pueden comparar estrategia:

*roi, fondos_balanceo, transacciones_acumuladas, costo_acumulado*

#### ROI

#### GANANCIA

#### FONDO BALANCEO



#### ROI


### to do
* unittest
