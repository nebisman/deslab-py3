# DESlab para Python 3

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nebisman/deslab-py3/blob/main/notebooks/DESlab_Colab.ipynb)

DESlab es una herramienta para el análisis y la síntesis de sistemas a eventos discretos (DES)
modelados como autómatas, escrita originalmente en Python 2 (L. Bermeo, J. C. Basilio, 2011-2012).
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
G1 = fsa(X, Sigma, T, X0, Xm, table, Sigobs=[a1, b1], name='$G_1$ -- example 1')

draw(G1, observer(G1), ~G1)      # tres figuras inline en el notebook
G1                               # en la última línea de una celda también se dibuja
```



## Licencia

DESlab se distribuye bajo la licencia MIT. Vea el archivo [LICENSE](LICENSE).
