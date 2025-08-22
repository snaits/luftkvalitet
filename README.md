# luftkvalitet
Fork av groharam/luftkvalitet

## Forklaring

Settings-filene inneholder de forskjellige lovkravene til hvert år.
Oppdaterte lovkrav finnes her:
[https://lovdata.no/forskrift/2004-06-01-931/§7-9](https://lovdata.no/forskrift/2004-06-01-931/§7-9)


## Oppsett
Skriptene krever powershell og python 3. 

Python 3 krever også noen pakker som du kan installere slik:

```
pip install python-dateutil
pip install requests
pip install orjson
```


## :warning: Spesialtilfeller
Kristiansand - Hennig Olsen er en stasjon med kun årlige målinger. Den dukker ikke riktig opp fra APIet og er derfor ikke håndtert som del av skriptet. Fila ligger under output, men må manuelt / for hånd redigeres med nye årsverdier.




