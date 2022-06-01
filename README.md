# Simulador de Inversion Cripto

Simulacion de una inversion mensual en las 500 criptomonedas con mayor capitalizacion de mercado durante 11 meses

### Motivacion
En un mercado actual muy *joven* como el Cripto, la tendencia en el mediano plazo es que la capitalizacion totoal del mercado siga en aumento a pesar de la alta volatilidad.

A diferencia de una estrategia donde se estudian y  eligen para invertir unos pocos proyectos/monedas, aca se intenta simular una inversion mensual basado exclusivamente en las 500 monedas de mayor  capitalizacion de mercado.



## Estrategia

* Las 500 criptomonedas se dividen y agrupan en  3 clusters:

    * Las **10** primeras del ranking en el **cluster 1**
    * Las **40** siguientes en el **cluster 2**
    * Las **450** restantes en el **cluster 3**
* El ranking que ocupe la criptomoneda en ese mes determinara el porcentaje del fondo/valor del cluster que se le asigne. Los porcentajes sumados representan el 100% del fondo y  se mantienen constantes durante todo el ejercicio.

* Se define ademas un **Fondo de Balanceo**, el cual permite mantener el valor de los clusters en un determinado rango de porcentajes repecto a dicho a fondo, modulado por una **Tolerancia de balanceo**
* El primer mes, se distribuye la inversion deseada entre los clusters y el fondo de blanceo, y se realizan las compras de las monedas segun el ranking que ocupen en cada cluster.
* A partir del segundo mes, aquellas monedas que salen del ranking (>500) se venderan a precio de mercado (los fondos generados se suman al **Fondo de Balanceo**), las recien incoporadas se les asiganara el porcentaje correspondiente para su compra de acuerdo a la posicion que ocupen, y por ultimo las que permanecen dentro del ranking, a partir de la cantidad, el precio actual y el puesto que ocupen se procedera a la venta/compra parcial para mantener los porcentajes. 
* Cada compra/venta tiene un **costo** de **0.01%** de la operacion. Este monto se descuenta del Fondo de Balanceo 

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
|  2  |  51- 80 | 11.3 |
| ... |   ...   |  ... |
| 14  |  51- 80 | 11.3 |
|  15 |471- 500 |   2  |

