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

| Función | Descripción |
|---|---|
| `draw(G1, G2, ..., style='beamer')` | En un notebook muestra cada autómata inline. Fuera de un notebook escribe una página HTML con todas las figuras y la abre en el navegador (`view=False` para no abrirla). Estilos: `'beamer'` (colores y título, por defecto), `'figurecolor'` (colores) y `'figure'` (blanco y negro). Como en el original, el estilo también puede ser el último argumento: `draw(G1, 'figure')`. |
| `savefig(G, 'G.pdf')` | Guarda la figura (`pdf`, `png`, `svg`, `dot`, `tex`). |
| `automaton2graphviz(G)` | Objeto `graphviz.Digraph` para personalizar la figura. |
| `automaton2tikz(G)` | Código TikZ (librería `automata`) con la disposición calculada por Graphviz. |
| `drawlatex(G1, G2, style='beamer', filename='figuras')` | Documento LaTeX (beamer o figuras) compilado con `pdflatex`, como el DESlab original. |

Las etiquetas LaTeX de la tabla (`q_1`, `\alpha_1`, `\sigma_f`, `\{x_1,x_2\}`, `K^{\uparrow C}`, ...)
se convierten a subíndices, superíndices y letras griegas en los dibujos inline; no se necesita LaTeX.
Si los programas de Graphviz no están instalados, `draw` usa matplotlib como alternativa.

Los ejemplos de `examples/` reproducen los ejemplos del DESlab original con la nueva API y el
notebook `notebooks/DESlab_Colab.ipynb` recorre las operaciones principales.

### Toolboxes

* Diagnóstico: `labelfailaut`, `diagnoser`, `observerdelta`.
* Control supervisor: `iscontrollable`, `is2controllable`, `supcontrollable`
  (con `supcontrollablegeneral` y `supcontrollablepfclosed`), tomados de `examples/supervisory.py`
  y `toolboxes/supervisory.py` del original.

## Diferencias con la versión original

Compatibilidad con Python 3 y networkx ≥ 2: sintaxis (`print`, `raise`, `<>`, `has_key`,
importaciones relativas), métodos de networkx que ya no existen (`out_edges_iter`, `nodes_iter`,
`Graph.node`, `write_dot`, ...), y orden determinista de estados y eventos (en Python 3 el orden de
los conjuntos de cadenas cambia en cada ejecución; ahora la numeración de `renamestates('number')` y
los dibujos son reproducibles).

Errores corregidos (verificados con las pruebas de `tests/`):

* `Gamma(x)` de un estado sin transiciones de salida lanzaba `KeyError` con networkx ≥ 2.
* `issublanguage` y `are_langequiv` con alfabetos distintos llamaban a `addevents`, que no existía.
  Ahora `addevent`/`addevents` aceptan un evento o una lista de eventos.
* `renamevents` volvía observables todos los eventos, no actualizaba `Sigcon` y fallaba con
  transiciones no deterministas. Ahora los eventos renombrados conservan sus propiedades.
* `invproj` agregaba autolazos también de los eventos originales no activos, lo que cambiaba el
  lenguaje. Ahora solo agrega los eventos nuevos.
* `langquotient` (`G1 / G2`) marcaba estados incorrectos cuando las cadenas de `Lm(G2)` tienen más de
  un evento. Se reimplementó: un estado `x` se marca si alguna cadena de `Lm(G2)` lleva de `x` a un
  estado marcado de `G1`.
* `complement` de un autómata no determinista no era el complemento; ahora se determiniza primero.
* `G1 - G2` con alfabetos distintos: el complemento se toma sobre la unión de los alfabetos.
* `proj` podía perder estados marcados según el orden de exploración; se reescribió.
* `G * fsa()` devolvía `G` en lugar del autómata vacío.
* `union` y `concatenation` lanzaban `KeyError` si un evento solo tenía etiqueta en el segundo
  autómata.
* Producto y composición paralela de autómatas con `epsilon` en ambos alfabetos sincronizaban
  `epsilon`; ahora cada autómata ejecuta sus transiciones `epsilon` por separado.
* `coac` dejaba en `X0` estados iniciales eliminados; `setpar(X0=...)` no actualizaba `is_dfa()`.
* `ispfclosed` comparaba estructuras; ahora prueba si `Lm(G)` es cerrado por prefijos
  (equivalencia de lenguajes con `pclosure(G)`).
* `buildmapping('xrefine'/'yrefine')` devolvía un valor con la forma equivocada.
* `observerdelta` y `is2controllable` usaban la API anterior (`G.E`, `G.Eobs`, `G.gamma`, ...).

Cambio de semántica: un autómata con estados pero con alfabeto vacío ya no se considera el
autómata vacío (por ejemplo, `sigmakleeneclos([])` marca la cadena vacía, `{ε}`).

No se portaron: `src/monoid.py` y `src/diagnosismonoid.py` (usaban la API anterior y no se
importaban), `src/common.py` (duplicaba `exceptions.py` y `syms`), `oldtests/` y el flujo
`graphics/working` con `dot2tex`, que se reemplazó por el dibujo inline y por `automaton2tikz`.

## Pruebas

```bash
pip install pytest matplotlib
pytest tests/
```

Las pruebas comparan cada operación con una enumeración por fuerza bruta de los lenguajes generado
y marcado (cadenas de longitud acotada) sobre autómatas aleatorios, deterministas y no deterministas.

## Licencia

DESlab se distribuye bajo la licencia MIT. Vea el archivo [LICENSE](LICENSE).
