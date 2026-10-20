"""
Conversion of the LaTeX labels used by DESlab (for instance 'q_1',
'\\alpha_{1}', '\\sigma_f', '\\{x_1,x_2\\}') to graphviz HTML-like
labels and to plain unicode text. Only a small subset of LaTeX is
supported: greek letters, common symbols, subscripts, superscripts,
groups and a few font commands. Unknown commands are written
without the backslash.
"""
#    Copyright (C) 2011-2012 by
#    Leonardo Bermeo <lbermeoc@unal.edu.co>
#    Joao Carlos Basilio <basilio@poli.ufrj.br>
#    BSD license.

import html

GREEK = {'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ϵ',
         'varepsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'vartheta': 'ϑ',
         'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ',
         'pi': 'π', 'varpi': 'ϖ', 'rho': 'ρ', 'varrho': 'ϱ', 'sigma': 'σ',
         'varsigma': 'ς', 'tau': 'τ', 'upsilon': 'υ', 'phi': 'ϕ', 'varphi': 'φ',
         'chi': 'χ', 'psi': 'ψ', 'omega': 'ω', 'Gamma': 'Γ', 'Delta': 'Δ',
         'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ', 'Pi': 'Π', 'Sigma': 'Σ',
         'Upsilon': 'Υ', 'Phi': 'Φ', 'Psi': 'Ψ', 'Omega': 'Ω'}

SYMBOLS = {'emptyset': '∅', 'varnothing': '∅', 'infty': '∞', 'uparrow': '↑',
           'downarrow': '↓', 'rightarrow': '→', 'to': '→', 'leftarrow': '←',
           'Rightarrow': '⇒', 'Leftarrow': '⇐', 'leftrightarrow': '↔', 'mapsto': '↦',
           'times': '×', 'cdot': '·', 'circ': '∘', 'cup': '∪', 'cap': '∩',
           'setminus': '∖', 'backslash': '\\', 'in': '∈', 'notin': '∉', 'subset': '⊂',
           'subseteq': '⊆', 'supset': '⊃', 'supseteq': '⊇', 'leq': '≤', 'le': '≤',
           'geq': '≥', 'ge': '≥', 'neq': '≠', 'ne': '≠', 'pm': '±', 'star': '⋆',
           'ast': '∗', 'diamond': '⋄', 'Diamond': '◇', 'clubsuit': '♣',
           'spadesuit': '♠', 'heartsuit': '♡', 'diamondsuit': '♢', 'bullet': '•',
           'dagger': '†', 'prime': '′', 'ell': 'ℓ', 'partial': '∂', 'nabla': '∇',
           'forall': '∀', 'exists': '∃', 'neg': '¬', 'lnot': '¬', 'wedge': '∧',
           'land': '∧', 'vee': '∨', 'lor': '∨', 'sum': '∑', 'prod': '∏', 'int': '∫',
           'parallel': '∥', 'mid': '|', 'vert': '|', 'Vert': '‖', 'ldots': '…',
           'cdots': '⋯', 'dots': '…', 'lbrace': '{', 'rbrace': '}', 'langle': '⟨',
           'rangle': '⟩', 'checkmark': '✓', 'square': '□', 'blacksquare': '■',
           'triangle': '△', 'bot': '⊥', 'top': '⊤', 'surd': '√', 'hbar': 'ℏ',
           'aleph': 'ℵ', 'models': '⊨', 'vdash': '⊢', 'equiv': '≡', 'approx': '≈',
           'sim': '∼', 'oplus': '⊕', 'otimes': '⊗', 'uplus': '⊎', 'sqcup': '⊔',
           'LaTeX': 'LaTeX', 'TeX': 'TeX'}

# spaces and escaped characters
SPACES = {',': ' ', ';': ' ', ':': ' ', '!': '', ' ': ' ', '\\': ' ', '>': ' ',
          '|': '‖', 'quad': '  ', 'qquad': '    '}

ACCENTS = {'hat': '̂', 'widehat': '̂', 'tilde': '̃',
           'widetilde': '̃', 'bar': '̄', 'vec': '⃗', 'dot': '̇',
           'ddot': '̈', 'check': '̌', 'acute': '́', 'grave': '̀',
           'breve': '̆'}

FONTS = {'textrm': 'rm', 'mathrm': 'rm', 'text': 'rm', 'mbox': 'rm', 'hbox': 'rm',
         'operatorname': 'rm', 'mathsf': 'rm', 'textsf': 'rm', 'mathtt': 'rm',
         'texttt': 'rm', 'mathcal': 'rm', 'mathscr': 'rm', 'mathfrak': 'rm',
         'textsc': 'rm', 'textup': 'rm', 'mathbb': 'bb', 'mathit': 'it',
         'textit': 'it', 'emph': 'it', 'textsl': 'it', 'mathbf': 'bf', 'textbf': 'bf',
         'boldsymbol': 'bf', 'bm': 'bf', 'overline': 'over', 'underline': 'under'}

IGNORE = {'left', 'right', 'big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr', 'Bigl',
          'Bigr', 'displaystyle', 'textstyle', 'scriptstyle', 'scriptscriptstyle',
          'limits', 'nolimits', 'tiny', 'scriptsize', 'footnotesize', 'small',
          'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge', 'noindent',
          'centering', 'relax'}

DOUBLESTRUCK = {'N': 'ℕ', 'Z': 'ℤ', 'Q': 'ℚ', 'R': 'ℝ', 'C': 'ℂ', 'P': 'ℙ'}

SUBSCRIPTS = dict(zip('0123456789+-=()aeoxhklmnpstijruv',
                      '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜᵢⱼᵣᵤᵥ'))
SUPERSCRIPTS = dict(zip('0123456789+-=()ni*′',
                        '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ*′'))


class _TeXParser:
    """ Recursive parser that converts a LaTeX string into a list
    of nodes (kind, value). kind is one of 'text', 'group', 'sub',
    'sup', 'rm', 'it', 'bf', 'bb', 'over', 'under' or 'accent'."""

    def __init__(self, s, math):
        self.s, self.i, self.math = s, 0, math

    def parse(self):
        nodes = []
        while self.i < len(self.s):
            if self.s[self.i] == '}':  # unbalanced brace
                self.i += 1
                continue
            nodes.extend(self.token())
        return nodes

    def group(self):
        """ parses the content of a group, after the opening brace"""
        nodes = []
        while self.i < len(self.s) and self.s[self.i] != '}':
            nodes.extend(self.token())
        self.i += 1
        return nodes

    def argument(self):
        """ parses the argument of a command or a sub(super)script"""
        while self.i < len(self.s) and self.s[self.i] == ' ':
            self.i += 1
        if self.i >= len(self.s):
            return []
        return self.token()

    def token(self):
        s, c = self.s, self.s[self.i]
        if c == '{':
            self.i += 1
            return [('group', self.group())]
        if c == '$':
            self.i += 1
            self.math = not self.math
            return []
        if c in '_^' and self.math:
            self.i += 1
            arg = self.argument()
            return [('sub' if c == '_' else 'sup', arg)]
        if c == '\\':
            return self.command()
        if c == '~':
            self.i += 1
            return [('text', ' ')]
        if self.math and c == ' ':
            self.i += 1
            return []
        if self.math and c == "'":
            self.i += 1
            return [('sup', [('text', '′')])]
        if not self.math and s.startswith('---', self.i):
            self.i += 3
            return [('text', '—')]
        if not self.math and s.startswith('--', self.i):
            self.i += 2
            return [('text', '–')]
        self.i += 1
        return [('text', c)]

    def command(self):
        s = self.s
        i = self.i + 1
        if i >= len(s):
            self.i = i
            return [('text', '\\')]
        if not s[i].isalpha():  # \{ \} \_ \, \; ...
            self.i = i + 1
            return [('text', SPACES.get(s[i], s[i]))]
        j = i
        while j < len(s) and s[j].isalpha():
            j += 1
        name = s[i:j]
        self.i = j
        # TeX ignores the spaces after a control word
        while self.i < len(s) and s[self.i] == ' ':
            self.i += 1
        if name in GREEK:
            return [('text', GREEK[name])]
        if name in SYMBOLS:
            return [('text', SYMBOLS[name])]
        if name in SPACES:
            return [('text', SPACES[name])]
        if name in ACCENTS:
            return [('accent', (ACCENTS[name], self.argument()))]
        if name in FONTS:
            return [(FONTS[name], self.argument())]
        if name == 'textcolor':
            self.argument()
            return [('group', self.argument())]
        if name == 'color':
            self.argument()
            return []
        if name in ('frac', 'dfrac', 'tfrac'):
            num, den = self.argument(), self.argument()
            return num + [('text', '/')] + den
        if name == 'sqrt':
            return [('text', '√'), ('group', self.argument())]
        if name in IGNORE:
            return []
        return [('text', name)]


def _parse(s, math):
    return _TeXParser(str(s), math).parse()


def _to_text(nodes):
    out = []
    for kind, val in nodes:
        if kind == 'text':
            out.append(val)
        elif kind == 'sub':
            txt = _to_text(val)
            if txt and all(ch in SUBSCRIPTS for ch in txt):
                out.append(''.join(SUBSCRIPTS[ch] for ch in txt))
            elif txt:
                out.append('_' + (txt if len(txt) == 1 else '{' + txt + '}'))
        elif kind == 'sup':
            txt = _to_text(val)
            if txt and all(ch in SUPERSCRIPTS for ch in txt):
                out.append(''.join(SUPERSCRIPTS[ch] for ch in txt))
            elif txt:
                out.append('^' + (txt if len(txt) == 1 else '{' + txt + '}'))
        elif kind == 'bb':
            out.append(''.join(DOUBLESTRUCK.get(ch, ch) for ch in _to_text(val)))
        elif kind == 'accent':
            mark, arg = val
            txt = _to_text(arg)
            out.append(txt[:1] + mark + txt[1:])
        elif kind == 'over':
            out.append(''.join(ch + '̅' for ch in _to_text(val)))
        else:  # groups and fonts
            out.append(_to_text(val))
    return ''.join(out)


def _to_html(nodes):
    tags = {'sub': 'SUB', 'sup': 'SUP', 'it': 'I', 'bf': 'B', 'over': 'O', 'under': 'U'}
    out = []
    for kind, val in nodes:
        if kind == 'text':
            out.append(html.escape(val, quote=False))
        elif kind in tags:
            inner = _to_html(val)
            if inner:
                out.append('<%s>%s</%s>' % (tags[kind], inner, tags[kind]))
        elif kind in ('bb', 'accent'):
            out.append(html.escape(_to_text([(kind, val)]), quote=False))
        else:  # groups and roman fonts
            out.append(_to_html(val))
    return ''.join(out)


def latex2text(label, math=True):
    """ Converts a LaTeX label to plain unicode text.
    If math is False the label is a text with formulas
    delimited by $...$ (as in the names of automata)"""
    return _to_text(_parse(label, math))


def latex2html(label, math=True):
    """ Converts a LaTeX label to the body of a graphviz
    HTML-like label (without the enclosing < >)"""
    return _to_html(_parse(label, math))
