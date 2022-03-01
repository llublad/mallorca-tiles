# Informe de la pràctica: *Applying genetic algorithms to zone design*

## Introducció 

A l'article de [Bação, F., Lobo, V. & Painho, M. (2005)](https://doi.org/10.1007/s00500-004-0413-4)
es desgrana una proposta per al disseny de zones electorals. 
El que es pretén a l'article és exposar un algorisme genètic
que permeti trobar propostes de divisió d'una determinada regió
composta per *n* unitats de població 
agrupant aquestes, en només *k* zones 
amb similar població amb dret a vot.

### Funció a optimitzar

Donat que els algorismes genètics requereixen minimitzar 
o maximitzar una funció de cost que relacioni 
els paràmetres de les zones amb l'objectiu, 
el treball en proposa algunes 
que involucren la desviació entre la població 
de cada zona i la població objectiva
(la mitjana de la població). 
Altres aspectes que es proposen ponderar són una 
mesura de la compacitat radial de la zona, definida 
com el sumatori de totes les distàncies entre el
centre de masses de la zona i cada un dels centroids
de les unitats que la componen o 
també una mesura del seu arrodoniment, 
que és definit com el quocient 
entre el perímetre al quadrat de la zona i la seva àrea.

Com a exemple del que s'hi exposa, 
la següent funció a minimitzar té en compte 
la desviació poblacional, així com la compacitat 
radial:
$$\sum_j\left(\left|P_j - \mu\right| * \sum_{i \in Z_j}d_{ij}\right)$$

On $P_j$ és el valor de la població amb dret a vot 
de la zona j-èssima, 
$\mu$ és el total de la població dividit per la 
quantitat de zones a dissenyar ($k$) 
i $d_{ij}$ és la distància entre el centroid
de la unitat de població i-èssima i 
el centroid de la zona j-èssima.

### Espai de solucions
També es quantifica quina és la complexitat de 
l'espai de solucions del problema. 
De fet la quantitat total de solucions és semblant 
al número de solucions d'un problema de *clustering*. 
Per tant la fórmula que ho aproxima és la dels
números de *Stirling* de segona espècie:
$$S(n, k) = \frac{1}{k!} \sum_{i=1}^k(-1)^i\left(\frac{k}{(k-i)! i!}\right)(k-i)^n$$

Com a exemple, si disposàssim de només 100 unitats
poblacionals a agrupar en 8 zones, 
$S(100, 8) \aprox 5.052 * 10^{85}$. 
És a dir un espai de solucions enorme, 
si bé es pot reduir en certa mesura
si tenim en compte que les 
zones han de ser contínues.

### Genotip

Es proposen dues codificacions. 

>Bação, F., Lobo, V. & Painho, M.
*Applying genetic algorithms to zone design.*
Soft Comput 9, 341–348 (2005).
https://doi.org/10.1007/s00500-004-0413-4

## Solució adoptada

Al nostre treball 

b) Se tiene que explicar brevemente 
cada función implementada.

## Exemples

c) Se deben mostrar distintos ejemplos de uso con distintos grados de dificultad, 
explicando con detalle cómo se deben introducir los inputs. 
Se deben analizar los resultados obtenidos y probar distintas configuraciones.

d) Hay que aplicarlo al caso de Mallorca considerando la población de los municipios, 
excepto Palma que se considerará por barrios.