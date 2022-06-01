
# Simulador de Inversion Cripto

Se realiza una inversion mensual en las 500 monedas con mayor capitalizacion de mercado durante 11 meses


# Simulador de Inversion Cripto

Se realiza una inversion mensual en las 500 monedas con mayor capitalizacion de mercado durante 11 meses

### Motivacion
En un mercado actual muy *joven* como el Cripto, la tendencia en el mediano plazo es que siga subiendo (mayor capitalizacion)  a pesar de su alta volatilidad.

A diferencia de una estrategia donde se estudian y  eligen para invertir unos pocos proyectos, aca se intenta simular una inversion mensual basado exclusivamente en las 500 monedas de mayor  capitalizacion de mercado.



## Estrategia

* Las 500 monedas se dividen y agrupan en  3 clusters:

    * **10** primeras monedas del ranking en el **cluster 3**
    * **11-50** siguientes en el **cluster 2**
    * **50-500** restantes en el **cluster 1**
* Dependiendo del cluster y de la posicion que ocupe la moneda sera el porcentaje de inversion que reciba:

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


