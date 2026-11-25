# Escenas de Open Industry Project

Escenas de [Open Industry Project](https://github.com/Open-Industry-Project/Open-Industry-Project)
(OIP), un simulador libre (licencia MIT) parecido a Factory I/O, para los notebooks de la banda
simple. Cada `.oip` es la carpeta del proyecto comprimida: la escena, el programa ST que genera el
notebook y una prueba del proyecto.

| Escena | Notebook | Programa |
|---|---|---|
| `banda_simple.oip` | `LCS_banda_simple_emisor_openplc.ipynb` | `Banda_simple_emisor.st` |
| `banda_tres_cajas.oip` | `LCS_banda_simple_emisor_tres_cajas_openplc.ipynb` | `Banda_simple_emisor_tres_cajas*.st` |

La escena tiene las mismas señales que la de Factory I/O. Los sensores son retrorreflectivos y valen
1 cuando no hay caja. El removedor de OIP no se cablea: retira las cajas siempre, que es lo que hace
`Remover := TRUE`.

| Parte | Señal | Dirección |
|---|---|---|
| sensor al comienzo de la banda | `SensorInicio` | `%IX100.0` |
| sensor al final de la banda | `SensorFin` | `%IX100.1` |
| banda | `Banda` | `%QX100.0` |
| emisor de cajas | `Emisor` | `%QX100.1` |
| segunda banda (solo tres cajas) | `Banda0` | `%QX100.3` |

## Con el PLC interno, en el navegador

Abra <https://www.openindustryproject.org/app/>, importe el `.oip` desde el menú del proyecto y pulse
Play. El programa del notebook corre en el PLC de OIP.

## Con OpenPLC Runtime

1. Instale la aplicación de escritorio de OIP (Windows o Linux); el navegador no abre conexiones de
   red. Abra la escena y, en *Simulation > PLC Controllers…*, elija *An external PLC* y luego
   *The PLC polls the simulator*, puerto 5020.
2. En OpenPLC, en *Slave Devices*, agregue un *Generic Modbus TCP Device* con la IP del computador
   donde corre OIP, el puerto 5020 y Slave ID 1. En OIP la dirección `%IXb.n` es la entrada
   discreta 8b+n y `%QXb.n` la bobina 8b+n, así que los inicios son 800:
   * *Discrete Inputs*: inicio 800, tamaño 2.
   * *Coils*: inicio 800, tamaño 3 (banda simple) o 4 (tres cajas, por `Banda0`).
3. Cargue y compile el `.st` del notebook, ponga la escena en Play y pulse *Start PLC*.

Las dos escenas se probaron con OpenPLC Runtime v3 (revisión `b5d4135`) consultando la escena de
OIP corrida sin ventana: la banda simple saca una caja a la vez (12 en 60 s) y la de tres cajas
saca tandas de tres (24 cajas en 90 s).
