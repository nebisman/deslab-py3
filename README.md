# DESlab para Python 3

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nebisman/deslab-py3/blob/main/notebooks/DESlab_Colab.ipynb)

**Notebook de la clase:** [notebooks/DESlab_Colab_class.ipynb](notebooks/DESlab_Colab_class.ipynb)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nebisman/deslab-py3/blob/main/notebooks/DESlab_Colab_class.ipynb)

**Control supervisorio (dos máquinas y un buffer):** [notebooks/DESlab_Colab_supervisorio.ipynb](notebooks/DESlab_Colab_supervisorio.ipynb)
[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nebisman/deslab-py3/blob/main/notebooks/DESlab_Colab_supervisorio.ipynb)

**Del modelo al PLC:** [Pequeña factoría sin fallas](notebooks/pequena_factoria_sin_fallas.ipynb).
El notebook explica los supuestos, la síntesis y verificación del supervisor, el mapa de
entradas/salidas, el rearme de los comandos y todos los parámetros del generador OpenPLC.
Guarda el archivo ST y las versiones del entorno para conservar los resultados.

DESlab es una herramienta para el análisis y la síntesis de sistemas a eventos discretos (DES)
modelados como autómatas, escrita originalmente en Python 2.
Esta versión conserva la misma API (`fsa`, `syms`, `draw`, `&`, `//`, `+`, `*`, `~`, `-`, `/`,
`observer`, `diagnoser`, ...) y funciona con Python 3 y las versiones actuales de
[networkx](https://networkx.org) y [graphviz](https://graphviz.readthedocs.io).

El cambio principal es el dibujo: **`draw(G1, G2, ...)` muestra cada autómata directamente en el
notebook** (Jupyter o Google Colab) como una imagen SVG, en lugar de compilar un PDF con LaTeX y
abrir un visor. La salida en LaTeX/TikZ sigue disponible como opción (`drawlatex`, `automaton2tikz`).

## Uso en Google Colab (sin instalar nada en su computador)

**Opción 1: abrir el notebook de ejemplo.**

1. Haga clic en el botón **Abrir en Colab** de arriba (o abra
   <https://colab.research.google.com/github/nebisman/deslab-py3/blob/main/notebooks/DESlab_Colab.ipynb>).
2. Ejecute la primera celda, *Instalación de DESlab desde GitHub*. Instala el paquete con
   `%pip install git+https://github.com/nebisman/deslab-py3.git`. Si Colab advierte que el notebook
   no fue creado por Google, elija *Ejecutar de todos modos*.
3. Ejecute las demás celdas en orden (*Entorno de ejecución → Ejecutar todas*).
4. Para conservar sus cambios use *Archivo → Guardar una copia en Drive*.

El notebook de la clase, con los mismos ejemplos más el algoritmo de verificación de
diagnosticabilidad de Moreira, está en
<https://colab.research.google.com/github/nebisman/deslab-py3/blob/main/notebooks/DESlab_Colab_class.ipynb>.

También puede abrirlo desde Colab con *Archivo → Abrir cuaderno → GitHub*, escribiendo
`nebisman/deslab-py3` y eligiendo `notebooks/DESlab_Colab.ipynb`.

**Opción 2: en un notebook nuevo de Colab**, escriba en la primera celda:

```python
%pip install -q git+https://github.com/nebisman/deslab-py3.git
from deslab import *
```

Colab ya trae `networkx`, `graphviz` y los programas de Graphviz. Cada vez que se reinicia el entorno
de ejecución de Colab hay que volver a ejecutar la celda de instalación.

## Instalación en su computador

Requisitos: Python ≥ 3.9, `networkx` ≥ 2.6, `graphviz` ≥ 0.20 (paquete de Python) y los programas
de [Graphviz](https://graphviz.org/download/) (`dot`). En Ubuntu: `sudo apt install graphviz`;
en macOS: `brew install graphviz`; en Windows: instalador de graphviz.org.

```bash
pip install git+https://github.com/nebisman/deslab-py3.git
```

o, para modificar el código:

```bash
git clone https://github.com/nebisman/deslab-py3.git
cd deslab-py3
pip install -e .
```

Para dibujar inline use Jupyter (`pip install notebook` o JupyterLab) o VS Code con notebooks.

## Uso

```python
from deslab import *

syms('q1 q2 q3 a1 b1 e')
table = [(a1, '\\alpha_1'), (b1, '\\beta_1'), (q1, 'q_1'), (q2, 'q_2'), (q3, 'q_3')]
X = [q1, q2, q3]
Sigma = [a1, b1, e]
X0 = [q1]
Xm = [q1, q3]
T = [(q1, b1, q2), (q2, b1, q3), (q2, e, q3), (q3, a1, q1), (q2, a1, q2)]
G1 = fsa(X, Sigma, T, X0, Xm, table, Sigobs=[a1, b1], Sigcon=Sigma,
         name='$G_1$ -- example 1')

draw(G1, observer(G1), ~G1)      # tres figuras inline en el notebook
G1                               # en la última línea de una celda también se dibuja
```

Dé siempre `Sigcon`, los eventos controlables, en la definición de cada autómata. Si se omite,
DESlab considera controlables todos los eventos, y la composición paralela hereda esa
clasificación. `Sigcon=[]` también se toma como omitido; para un autómata sin eventos
controlables use `Sigcon=set()`.

## Generación de Structured Text para OpenPLC

El generador está integrado en DESlab y no requiere TCT ni el proyecto `deslab-st`:

```python
from deslab import generate_ST_OPENPLC

# S y G son autómatas DESlab; actuators asocia eventos con señales del PLC.
st = generate_ST_OPENPLC([S], plants=[G], actuators=actuators,
                         namest="controlador", output_dir="ST_Generated")
```

Devuelve el texto ST y escribe `ST_Generated/controlador.st`. Con varios supervisores,
se requiere una planta por supervisor en el mismo orden. Los autómatas auxiliares, que tienen
su propio estado pero no se sintetizan, se pasan en `Isolated`, y las parejas que convierten una
petición interna en una orden, cuando hacen falta, en `event_pairs`. La función y sus ayudantes
privados están en [`deslab/toolboxes/codegen.py`](deslab/toolboxes/codegen.py), sin dependencias adicionales.
Su docstring documenta la API; el [notebook completo](notebooks/pequena_factoria_sin_fallas.ipynb)
presenta un caso ejecutable con señales y auxiliares de rearme.

La carpeta [`notebooks/factory_io`](notebooks/factory_io) reúne otros notebooks
que generan programas ST y, en `Factory scenes`, las escenas de Factory I/O de la pequeña fábrica,
la línea de transferencia y la línea de ensamble:

- [Pequeña fábrica con un supervisor](notebooks/factory_io/LCS_pequena_factoria_st.ipynb):
  el caso de introducción. Explica cómo se definen el contrato con las máquinas, el diccionario
  `actuators` y los autómatas de rearme, revisa el programa línea por línea contra el supervisor
  y sigue su ejecución scan por scan.
- [Pequeña fábrica con averías](notebooks/factory_io/LCS_modular_control_small_factory_openplc.ipynb):
  la versión DESlab de `Small_factory.py`, con un supervisor, el supervisor de la alimentación y
  los autómatas auxiliares de las máquinas, el buffer, la cuchilla y la reparación. Explica
  `state_order` y `transition_order`, que numeran los estados y ordenan las transiciones como TCT.
- [Pequeña fábrica con un supervisor monolítico](notebooks/factory_io/LCS_monolithic_control_small_factory_openplc.ipynb):
  un solo supervisor para las máquinas y la cinta de alimentación. Los modelos tienen tres cambios:
  el pulsador de arranque es un componente de la planta, en lugar de autolazos de `start`; una
  sola especificación, `REQ_start`, pide esperarlo antes de cualquier orden; y el supervisor da
  directamente las órdenes `M1-ON` y `M2-ON`, sin peticiones ni parejas. Explica qué cambia en el
  programa del PLC.
- [Pequeña fábrica con un supervisor para las máquinas y otro para la alimentación](notebooks/factory_io/LCS_modular_by_device_small_factory_openplc.ipynb):
  la versión modular del monolítico, con los mismos eventos, planta y especificaciones. Divide
  `REQ_start` por equipo para que los dos supervisores no compartan órdenes; cada uno da las suyas
  directamente, sin parejas. Comprueba que juntos son iguales al supervisor monolítico y explica
  qué cambia en el PLC.
- [Pequeña fábrica con control modular local](notebooks/factory_io/LCS_local_modular_control_small_factory_openplc.ipynb):
  los modelos del monolítico con dos supervisores, cada uno con su planta local: uno para
  `REQ_Buffer` y `REQ_repair` y otro para `REQ_start`. Comprueba que son no conflictivos y que
  juntos son iguales al supervisor monolítico. Como los dos comparten las órdenes de arranque, las
  dan con las peticiones $e_1$ y $e_2$ y las parejas, y el notebook explica cómo el programa
  combina las peticiones compartidas.
- [Línea de transferencia](notebooks/factory_io/LCS_modular_control_transfer_line_openplc.ipynb):
  la versión DESlab de `Transfer_line.py`, con cuatro supervisores locales y dos supervisores de
  la línea que son conflictivos; el generador detecta el conflicto y agrega el coordinador.
- [Línea de ensamble](notebooks/factory_io/LCS_assembly_line_openplc.ipynb): la versión DESlab
  de `Assembly_line.py`, con cinco supervisores locales.

Los notebooks de la pequeña fábrica con averías, la línea de transferencia y la línea de ensamble
definen sus modelos con `fsa` y solo con los autolazos necesarios, y generan un programa idéntico,
byte por byte, al que genera TCT con el script correspondiente de TCT_Proyect (copiados en la
misma carpeta). Los programas para las escenas, incluidos los del supervisor monolítico y de sus
dos versiones modulares, están en
[`notebooks/factory_io/ST_generated`](notebooks/factory_io/ST_generated). La prueba
[`tests/test_openplc_notebooks.py`](tests/test_openplc_notebooks.py) ejecuta las celdas de los
notebooks, simula scan por scan el programa de la pequeña fábrica con un supervisor, compara los
de TCT con la huella SHA-256 de los programas de TCT y comprueba que los archivos de
`ST_generated` son los que generan los notebooks.

Las salidas conservan su valor hasta que otra acción las cambie. El ejemplo explicita
el protocolo de arranque, fin y rearme, así como el supuesto de eventos en scans distintos.
El programa configura una tarea de 20 ms e incluye un bloque aleatorio específico de
OpenPLC. Generar el archivo no sustituye su compilación y prueba con el runtime y las
direcciones de E/S elegidas. La coordinación entre pares tampoco sustituye el análisis
de no bloqueo global cuando hay más de dos supervisores.

Para ejecutar las pruebas del módulo y del resto de DESlab:

```bash
python -m pip install -e ".[test,plot]"
python -m pytest tests
```



## Licencia

DESlab se distribuye bajo la licencia MIT. Vea el archivo [LICENSE](LICENSE).
