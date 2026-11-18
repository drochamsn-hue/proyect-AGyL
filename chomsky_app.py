import math
import tkinter as tk
from tkinter import ttk, messagebox

BG = "#1e1f29"
PANEL = "#282a36"
CELL = "#44475a"
FG = "#f8f8f2"
MUTED = "#9aa3c7"
ACC = "#bd93f9"
OK = "#50fa7b"
BAD = "#ff5555"
WARN = "#f1fa8c"
CYAN = "#8be9fd"
DONE = "#2f5d3a"

MONO = ("Courier New", 14, "bold")
UI = ("Segoe UI", 10)
SMALL = ("Segoe UI", 9)
BIG = ("Segoe UI", 16, "bold")


def make_dfa(states, alphabet, delta, start, accept):
    return dict(states=states, alphabet=alphabet, delta=delta, start=start, accept=accept)


def dfa_even_ones():
    d = {("q0", "0"): "q0", ("q0", "1"): "q1", ("q1", "0"): "q1", ("q1", "1"): "q0"}
    return make_dfa(["q0", "q1"], "01", d, "q0", {"q0"})


def dfa_ends_01():
    d = {("q0", "0"): "q1", ("q0", "1"): "q0",
         ("q1", "0"): "q1", ("q1", "1"): "q2",
         ("q2", "0"): "q1", ("q2", "1"): "q0"}
    return make_dfa(["q0", "q1", "q2"], "01", d, "q0", {"q2"})


def dfa_contains_aba():
    d = {("q0", "a"): "q1", ("q0", "b"): "q0",
         ("q1", "a"): "q1", ("q1", "b"): "q2",
         ("q2", "a"): "q3", ("q2", "b"): "q0",
         ("q3", "a"): "q3", ("q3", "b"): "q3"}
    return make_dfa(["q0", "q1", "q2", "q3"], "ab", d, "q0", {"q3"})


def dfa_multiple(n):
    states = [f"q{i}" for i in range(n)]
    d = {(f"q{i}", str(b)): f"q{(2 * i + b) % n}" for i in range(n) for b in (0, 1)}
    return make_dfa(states, "01", d, "q0", {"q0"})


MOD_NAME = "Múltiplos de N en binario (N parametrizable)"

DFA_LANGS = {
    "Cadenas binarias con cantidad par de 1s": dict(
        build=dfa_even_ones,
        desc="L = { w ∈ {0,1}* : w tiene un número par de 1s }. Dos estados: paridad par e impar.",
        ex=["", "11", "1010", "1", "0111", "10001"]),
    "Cadenas binarias que terminan en 01": dict(
        build=dfa_ends_01,
        desc="L = { w ∈ {0,1}* : w termina en 01 }. El autómata recuerda los dos últimos símbolos.",
        ex=["01", "1101", "0", "10", "0100", "101"]),
    "Cadenas sobre {a,b} que contienen 'aba'": dict(
        build=dfa_ends_01,
        desc="L = { w ∈ {a,b}* : 'aba' es subcadena de w }. El estado q3 es una trampa de aceptación.",
        ex=["aba", "babab", "aab", "bbb", "abba", "bbabab"]),
    MOD_NAME: dict(
        build=None,
        desc="L = { w ∈ {0,1}* : el número binario w es múltiplo de N }. Cada estado qi guarda el residuo i mod N. Cambia N con el selector.",
        ex=None),
}
DFA_LANGS["Cadenas sobre {a,b} que contienen 'aba'"]["build"] = dfa_contains_aba


def snap_stack(steps, pos, state, stack, msg):
    steps.append(dict(pos=pos, state=state, stack=list(stack), msg=msg))


def pda_anbn(s):
    steps = []
    st = "q0"
    stack = ["$"]
    snap_stack(steps, 0, st, stack, "Inicio: la pila contiene solo el marcador $")
    for i, c in enumerate(s):
        if c == "a" and st == "q0":
            stack.append("A")
            snap_stack(steps, i + 1, st, stack, "Lee 'a': apila A")
        elif c == "b" and stack[-1] == "A":
            stack.pop()
            st = "q1"
            snap_stack(steps, i + 1, st, stack, "Lee 'b': desapila A y pasa a q1")
        else:
            snap_stack(steps, i, st, stack, f"Lee '{c}': no hay transición válida → rechaza")
            return steps, False
    ok = st == "q1" and stack == ["$"]
    snap_stack(steps, len(s), st, stack,
               "Fin de cadena: estado q1 y pila vacía ($) → acepta" if ok
               else "Fin de cadena: faltan b's, sobran a's o la cadena está vacía → rechaza")
    return steps, ok


def pda_parens(s):
    steps = []
    stack = ["$"]
    pairs = {")": "(", "]": "[", "}": "{"}
    snap_stack(steps, 0, "q0", stack, "Inicio: la pila contiene solo el marcador $")
    for i, c in enumerate(s):
        if c in "([{":
            stack.append(c)
            snap_stack(steps, i + 1, "q0", stack, f"Lee '{c}': apila '{c}'")
        elif c in pairs and stack[-1] == pairs[c]:
            stack.pop()
            snap_stack(steps, i + 1, "q0", stack, f"Lee '{c}': desapila '{pairs[c]}'")
        else:
            snap_stack(steps, i, "q0", stack, f"Lee '{c}': no coincide con el tope de la pila → rechaza")
            return steps, False
    ok = stack == ["$"]
    snap_stack(steps, len(s), "q0", stack,
               "Fin de cadena: pila vacía ($) → acepta" if ok
               else "Fin de cadena: quedan símbolos sin cerrar en la pila → rechaza")
    return steps, ok


def pda_wcwr(s):
    steps = []
    st = "q0"
    stack = ["$"]
    snap_stack(steps, 0, st, stack, "Inicio: la pila contiene solo el marcador $")
    for i, c in enumerate(s):
        if st == "q0" and c in "ab":
            stack.append(c)
            snap_stack(steps, i + 1, st, stack, f"Lee '{c}': apila '{c}'")
        elif st == "q0" and c == "c":
            st = "q1"
            snap_stack(steps, i + 1, st, stack, "Lee 'c' (centro): pasa a q1 sin tocar la pila")
        elif st == "q1" and c in "ab" and stack[-1] == c:
            stack.pop()
            snap_stack(steps, i + 1, st, stack, f"Lee '{c}': coincide con el tope, desapila")
        else:
            snap_stack(steps, i, st, stack, f"Lee '{c}': no hay transición válida → rechaza")
            return steps, False
    ok = st == "q1" and stack == ["$"]
    snap_stack(steps, len(s), st, stack,
               "Fin de cadena: estado q1 y pila vacía ($) → acepta" if ok
               else "Fin de cadena: no se vació la pila o no hubo centro 'c' → rechaza")
    return steps, ok


PDA_LANGS = {
    "aⁿbⁿ  (n ≥ 1)": dict(
        run=pda_anbn,
        desc="L = { aⁿbⁿ : n ≥ 1 }. Se apila una A por cada 'a' y se desapila una por cada 'b'. Requiere memoria LIFO: no es regular.",
        ex=["ab", "aaabbb", "aabbb", "abab", "", "aab"]),
    "Paréntesis balanceados ( ) [ ] { }": dict(
        run=pda_parens,
        desc="Lenguaje de Dyck con tres tipos de paréntesis. Se apila cada apertura y el cierre debe coincidir con el tope.",
        ex=["(())", "()[]{}", "{[()]}", "([)]", "((", ""]),
    "w c wᴿ  sobre {a,b}": dict(
        run=pda_wcwr,
        desc="L = { w c wᴿ : w ∈ {a,b}* }. Palíndromos con marca central: se apila w y luego se compara en orden inverso.",
        ex=["abcba", "c", "abbcbba", "abcab", "ab", "acb"]),
}


def rule(delta, states, symbols, new=None, write=None, move="R"):
    for q in states.split():
        for sym in symbols:
            delta[(q, sym)] = (new or q, sym if write is None else write, move)


def build_lba_anbncn():
    d = {}
    rule(d, "q0", "⊢", "q1", None, "R")
    rule(d, "q1", "a", "q2", "X", "R")
    rule(d, "q1", "X", "q1", None, "R")
    rule(d, "q1", "Y", "q5", None, "R")
    rule(d, "q2", "aY", "q2", None, "R")
    rule(d, "q2", "b", "q3", "Y", "R")
    rule(d, "q3", "bZ", "q3", None, "R")
    rule(d, "q3", "c", "q4", "Z", "L")
    rule(d, "q4", "abcXYZ", "q4", None, "L")
    rule(d, "q4", "⊢", "q1", None, "R")
    rule(d, "q5", "YZ", "q5", None, "R")
    rule(d, "q5", "⊣", "qa", None, "S")
    return dict(delta=d, start="q0", accept={"qa"}, alphabet="abc")


def build_tm_add():
    d = {}
    rule(d, "s0", "1", "s0", None, "R")
    rule(d, "s0", "+", "s1", "1", "R")
    rule(d, "s1", "1", "s1", None, "R")
    rule(d, "s1", "_", "s2", "_", "L")
    rule(d, "s2", "1", "halt", "_", "S")
    return dict(delta=d, start="s0", accept={"halt"}, alphabet="1+")


def build_tm_palindrome():
    d = {}
    rule(d, "q0", "a", "qa", "_", "R")
    rule(d, "q0", "b", "qb", "_", "R")
    rule(d, "q0", "_", "halt", "_", "S")
    rule(d, "qa", "ab", "qa", None, "R")
    rule(d, "qa", "_", "ra", "_", "L")
    rule(d, "qb", "ab", "qb", None, "R")
    rule(d, "qb", "_", "rb", "_", "L")
    rule(d, "ra", "a", "back", "_", "L")
    rule(d, "ra", "_", "halt", "_", "S")
    rule(d, "rb", "b", "back", "_", "L")
    rule(d, "rb", "_", "halt", "_", "S")
    rule(d, "back", "ab", "back", None, "L")
    rule(d, "back", "_", "q0", "_", "R")
    return dict(delta=d, start="q0", accept={"halt"}, alphabet="ab")


def build_tm_increment():
    d = {}
    rule(d, "r", "01", "r", None, "R")
    rule(d, "r", "_", "c", "_", "L")
    rule(d, "c", "1", "c", "0", "L")
    rule(d, "c", "0", "halt", "1", "S")
    rule(d, "c", "_", "halt", "1", "S")
    return dict(delta=d, start="r", accept={"halt"}, alphabet="01")


LBA_MACHINES = {
    "aⁿbⁿcⁿ  (n ≥ 1)": dict(
        build=build_lba_anbncn,
        desc="L = { aⁿbⁿcⁿ : n ≥ 1 }, lenguaje sensible al contexto que no es libre de contexto. La cinta está limitada por ⊢ y ⊣ y el cabezal marca una a, una b y una c con X, Y, Z en cada pasada.",
        ex=["abc", "aabbcc", "aaabbbccc", "aabbc", "abcabc", "acb", ""]),
}

TM_MACHINES = {
    "Suma unaria  (1ᵐ+1ⁿ → 1ᵐ⁺ⁿ)": dict(
        build=build_tm_add,
        desc="Función aritmética: suma en unario. Cambia el '+' por 1 y borra el último 1. Ejemplo: 11+111 deja 11111 en la cinta.",
        ex=["11+111", "1+1", "+11", "111+", "11", "1++1"]),
    "Palíndromos sobre {a,b}": dict(
        build=build_tm_palindrome,
        desc="Acepta w tal que w = wᴿ. Borra el primer símbolo, viaja al final y compara con el último, y repite.",
        ex=["abba", "aba", "aabaa", "ab", "abab", ""]),
    "Incremento binario (+1)": dict(
        build=build_tm_increment,
        desc="Función aritmética: suma 1 a un número binario. Va al extremo derecho y propaga el acarreo hacia la izquierda; puede extender la cinta.",
        ex=["1011", "111", "0", "100", "1"]),
}


def run_machine(m, text, bounded, max_steps=1500):
    delta = m["delta"]
    state = m["start"]
    blank = "_"
    if bounded:
        tape = {0: "⊢"}
        for i, c in enumerate(text):
            tape[i + 1] = c
        tape[len(text) + 1] = "⊣"
        lo, hi = 0, len(text) + 1
    else:
        tape = {i: c for i, c in enumerate(text)}
        lo, hi = 0, 0
    head = 0
    steps = []

    def snap(msg):
        steps.append(dict(tape=dict(tape), head=head, state=state, msg=msg))

    snap(f"Configuración inicial: estado {state}, cabezal en la posición 0")
    for _ in range(max_steps):
        if state in m["accept"]:
            return steps, True
        sym = tape.get(head, blank)
        key = (state, sym)
        if key not in delta:
            snap(f"No existe δ({state}, {sym}) → la máquina rechaza")
            return steps, False
        new, write, move = delta[key]
        tape[head] = write
        head += {"R": 1, "L": -1, "S": 0}[move]
        old = state
        state = new
        if bounded and not lo <= head <= hi:
            snap("El cabezal intenta salir de los delimitadores → rechaza")
            return steps, False
        snap(f"δ({old}, {sym}) = ({new}, {write}, {move})")
    snap("Se superó el límite de pasos → la simulación se detiene")
    return steps, False


def draw_strip(cv, text, pos, y=50, W=700):
    cv.create_text(W / 2, y - 32, text="Cadena de entrada", fill=MUTED, font=SMALL)
    if not text:
        cv.create_text(W / 2, y, text="ε  (cadena vacía)", fill=FG, font=BIG)
        if pos is not None:
            cv.create_text(W / 2, y + 28, text="▲", fill=ACC)
        return
    n = len(text)
    cw = min(36, (W - 40) / n)
    x0 = (W - cw * n) / 2
    for i, c in enumerate(text):
        x = x0 + i * cw
        if pos is None:
            fill, fg = CELL, FG
        elif i < pos:
            fill, fg = DONE, FG
        elif i == pos:
            fill, fg = ACC, BG
        else:
            fill, fg = CELL, FG
        cv.create_rectangle(x, y - 17, x + cw, y + 17, fill=fill, outline=BG)
        cv.create_text(x + cw / 2, y, text=c, fill=fg, font=MONO)
    if pos is not None:
        cv.create_text(x0 + pos * cw + (cw / 2 if pos < n else 0), y + 28, text="▲", fill=ACC)


def draw_msg(cv, text, x, y, width, anchor="center"):
    cv.create_text(x, y, text=text, fill=FG, font=("Segoe UI", 11), width=width,
                   anchor=anchor, justify="center" if anchor == "center" else "left")


class ModuleFrame(tk.Frame):
    W = 700
    H = 430

    def __init__(self, master, app, title, langs):
        super().__init__(master, bg=BG)
        self.app = app
        self.langs = langs
        self.steps = []
        self.index = 0
        self.running = False
        self.job = None
        self.text = ""
        self.verdict = None
        self.ex_list = []

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=(12, 6))
        tk.Button(top, text="← Menú principal", command=app.show_menu, bg=CELL, fg=FG,
                  activebackground=ACC, relief="flat", padx=10, pady=4, cursor="hand2").pack(side="left")
        tk.Label(top, text=title, bg=BG, fg=ACC, font=("Segoe UI", 15, "bold")).pack(side="left", padx=16)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        left = tk.Frame(body, bg=PANEL, width=290)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.lang = tk.StringVar(value=list(langs)[0])
        self.section(left, "Lenguaje")
        cb = ttk.Combobox(left, textvariable=self.lang, values=list(langs), state="readonly")
        cb.pack(fill="x", padx=12)
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_lang())

        self.extra = tk.Frame(left, bg=PANEL)
        self.extra.pack(fill="x", padx=12, pady=(6, 0))
        self.build_extra(self.extra)

        self.desc = tk.Label(left, bg=PANEL, fg=MUTED, font=SMALL, justify="left", wraplength=262, anchor="w")
        self.desc.pack(fill="x", padx=12, pady=8)

        self.section(left, "Cadena de entrada")
        self.entry = tk.Entry(left, font=MONO, bg=CELL, fg=FG, insertbackground=FG, relief="flat")
        self.entry.pack(fill="x", padx=12, ipady=4)
        self.entry.bind("<Return>", lambda e: self.start())

        bar = tk.Frame(left, bg=PANEL)
        bar.pack(fill="x", padx=12, pady=8)
        buttons = [("Iniciar", self.start, ACC, BG), ("Paso ▶", self.next, CELL, FG),
                   ("Auto ▶▶", self.auto, CELL, FG), ("Pausa", self.stop, CELL, FG),
                   ("Reiniciar", self.reset, CELL, FG)]
        for i, (t, c, bgc, fgc) in enumerate(buttons):
            b = tk.Button(bar, text=t, command=c, bg=bgc, fg=fgc, activebackground=ACC, relief="flat",
                          pady=3, cursor="hand2")
            b.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=1)

        self.speed = tk.Scale(left, from_=100, to=1500, orient="horizontal", bg=PANEL, fg=FG,
                              highlightthickness=0, troughcolor=CELL, label="Retardo automático (ms)")
        self.speed.set(600)
        self.speed.pack(fill="x", padx=12)

        self.section(left, "Cadenas de prueba (clic para cargar)")
        self.listbox = tk.Listbox(left, height=8, bg=CELL, fg=FG, selectbackground=ACC, selectforeground=BG,
                                  relief="flat", font=("Courier New", 11), activestyle="none",
                                  exportselection=False, highlightthickness=0)
        self.listbox.pack(fill="x", padx=12, pady=(0, 10))
        self.listbox.bind("<<ListboxSelect>>", self.pick_example)

        self.cv = tk.Canvas(right, width=self.W, height=self.H, bg="#191a21", highlightthickness=0)
        self.cv.pack(anchor="n")
        self.status = tk.Label(right, text="", bg=BG, fg=FG, font=("Segoe UI", 12, "bold"))
        self.status.pack(pady=6)
        self.log = tk.Text(right, height=7, bg=PANEL, fg=FG, font=("Courier New", 10), relief="flat",
                           state="disabled", highlightthickness=0)
        self.log.pack(fill="both", expand=True)

        self.on_lang()

    def section(self, parent, text):
        tk.Label(parent, text=text, bg=PANEL, fg=FG, font=("Segoe UI", 10, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(10, 3))

    def build_extra(self, parent):
        pass

    def validate(self, text):
        pass

    def examples(self):
        raise NotImplementedError

    def compute(self, text):
        raise NotImplementedError

    def draw(self, s):
        raise NotImplementedError

    def on_lang(self):
        self.desc.config(text=self.langs[self.lang.get()])
        self.reset()
        self.ex_list = self.examples()
        self.listbox.delete(0, "end")
        for t in self.ex_list:
            ok = self.compute(t)[1]
            self.listbox.insert("end", f"{(t or 'ε'):<14}{'✔ acepta' if ok else '✘ rechaza'}")

    def pick_example(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.entry.delete(0, "end")
        self.entry.insert(0, self.ex_list[sel[0]])
        self.start()

    def write_log(self, line):
        self.log.config(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def reset(self):
        self.stop()
        self.steps = []
        self.index = 0
        self.text = ""
        self.clear_log()
        self.status.config(text="", fg=FG)
        self.draw(None)

    def start(self):
        self.stop()
        text = self.entry.get().strip()
        try:
            self.validate(text)
        except ValueError as e:
            messagebox.showwarning("Cadena no válida", str(e))
            return False
        self.steps, self.verdict = self.compute(text)
        self.text = text
        self.index = 0
        self.clear_log()
        self.show()
        return True

    def show(self):
        s = self.steps[self.index]
        self.draw(s)
        self.write_log(f"{self.index:>3}. {s['msg']}")
        if self.index == len(self.steps) - 1:
            self.status.config(text="✔ Cadena ACEPTADA" if self.verdict else "✘ Cadena RECHAZADA",
                               fg=OK if self.verdict else BAD)
        else:
            self.status.config(text=f"Paso {self.index} de {len(self.steps) - 1}", fg=FG)

    def next(self):
        if not self.steps:
            self.start()
            return
        if self.index < len(self.steps) - 1:
            self.index += 1
            self.show()

    def auto(self):
        if not self.steps or self.index >= len(self.steps) - 1:
            if not self.start():
                return
        self.running = True
        self.job = self.after(int(self.speed.get()), self.tick)

    def tick(self):
        if not self.running:
            return
        if self.index < len(self.steps) - 1:
            self.index += 1
            self.show()
            self.job = self.after(int(self.speed.get()), self.tick)
        else:
            self.running = False

    def stop(self):
        self.running = False
        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None


class DFAModule(ModuleFrame):
    R = 26

    def __init__(self, master, app):
        super().__init__(master, app, "Nivel 3 · Lenguajes regulares · Autómata finito",
                         {k: v["desc"] for k, v in DFA_LANGS.items()})

    def build_extra(self, parent):
        self.n = tk.IntVar(value=3)
        tk.Label(parent, text="N (solo para múltiplos de N):", bg=PANEL, fg=MUTED, font=SMALL).pack(side="left")
        sp = ttk.Spinbox(parent, from_=2, to=7, width=4, textvariable=self.n, command=self.on_lang)
        sp.pack(side="left", padx=6)
        sp.bind("<Return>", lambda e: self.on_lang())

    def get_n(self):
        try:
            return max(2, min(7, int(self.n.get())))
        except (tk.TclError, ValueError):
            return 3

    def dfa(self):
        name = self.lang.get()
        if name == MOD_NAME:
            return dfa_multiple(self.get_n())
        return DFA_LANGS[name]["build"]()

    def examples(self):
        name = self.lang.get()
        if name != MOD_NAME:
            return DFA_LANGS[name]["ex"]
        n = self.get_n()
        out = ["0", bin(n)[2:], bin(3 * n)[2:], bin(n + 1)[2:], bin(2 * n + 1)[2:], bin(5 * n)[2:]]
        return list(dict.fromkeys(out))

    def compute(self, text):
        d = self.dfa()
        st = d["start"]
        steps = [dict(pos=0, state=st, edge=None, msg=f"Estado inicial: {st}")]
        for i, c in enumerate(text):
            if (st, c) not in d["delta"]:
                steps.append(dict(pos=i, state=st, edge=None,
                                  msg=f"Símbolo '{c}' fuera del alfabeto {{{', '.join(d['alphabet'])}}} → rechaza"))
                return steps, False
            nxt = d["delta"][(st, c)]
            steps.append(dict(pos=i + 1, state=nxt, edge=(st, nxt), msg=f"Lee '{c}': δ({st}, {c}) = {nxt}"))
            st = nxt
        ok = st in d["accept"]
        steps.append(dict(pos=len(text), state=st, edge=None,
                          msg=f"Fin de la cadena en {st}: " + ("estado de aceptación" if ok else "no es estado de aceptación")))
        return steps, ok

    def draw(self, s):
        cv = self.cv
        cv.delete("all")
        draw_strip(cv, self.text, s["pos"] if s else None, 45)
        self.draw_graph(self.dfa(), s)
        if s:
            draw_msg(cv, s["msg"], self.W / 2, self.H - 20, self.W - 40)

    def draw_graph(self, d, s):
        cv = self.cv
        R = self.R
        states = d["states"]
        n = len(states)
        cx, cy, rx, ry = self.W / 2, 238, 250, 78
        pos = {}
        for i, q in enumerate(states):
            a = math.pi - 2 * math.pi * i / n
            pos[q] = (cx + rx * math.cos(a), cy - ry * math.sin(a), math.cos(a), -math.sin(a))
        groups = {}
        for (a, sym), b in d["delta"].items():
            groups.setdefault((a, b), []).append(sym)
        hot = s["edge"] if s else None
        for (a, b), syms in groups.items():
            label = ",".join(sorted(syms))
            is_hot = hot == (a, b)
            color = WARN if is_hot else MUTED
            width = 3 if is_hot else 1.5
            x1, y1, ux, uy = pos[a]
            if a == b:
                px, py = -uy, ux

                def pt(r, t):
                    return (x1 + r * (math.cos(t) * ux + math.sin(t) * px),
                            y1 + r * (math.cos(t) * uy + math.sin(t) * py))

                pts = [pt(R, -0.6), pt(R + 36, -0.35), pt(R + 36, 0.35), pt(R + 2, 0.6)]
                cv.create_line(*[c for p in pts for c in p], smooth=True, arrow="last", fill=color, width=width)
                lx, ly = pt(R + 48, 0)
                cv.create_text(lx, ly, text=label, fill=color, font=SMALL)
            else:
                x2, y2 = pos[b][0], pos[b][1]
                dx, dy = x2 - x1, y2 - y1
                L = math.hypot(dx, dy)
                px, py = -dy / L, dx / L
                off = 34
                mx, my = (x1 + x2) / 2 + px * off, (y1 + y2) / 2 + py * off

                def trim(x, y, gap):
                    vx, vy = mx - x, my - y
                    v = math.hypot(vx, vy)
                    return x + vx / v * gap, y + vy / v * gap

                sx, sy = trim(x1, y1, R)
                ex, ey = trim(x2, y2, R + 2)
                cv.create_line(sx, sy, mx, my, ex, ey, smooth=True, arrow="last", fill=color, width=width)
                lx = 0.25 * sx + 0.5 * mx + 0.25 * ex + px * 10
                ly = 0.25 * sy + 0.5 * my + 0.25 * ey + py * 10
                cv.create_text(lx, ly, text=label, fill=color, font=SMALL)
        current = s["state"] if s else None
        for q in states:
            x, y, ux, uy = pos[q]
            fill = ACC if q == current else PANEL
            cv.create_oval(x - R, y - R, x + R, y + R, fill=fill, outline=FG, width=2)
            if q in d["accept"]:
                cv.create_oval(x - R + 5, y - R + 5, x + R - 5, y + R - 5, outline=FG, width=2)
            cv.create_text(x, y, text=q, fill=BG if q == current else FG, font=("Segoe UI", 11, "bold"))
        x, y, ux, uy = pos[d["start"]]
        px, py = -uy, ux
        cv.create_line(x + px * (R + 40), y + py * (R + 40), x + px * (R + 2), y + py * (R + 2),
                       arrow="last", fill=CYAN, width=2)
        cv.create_text(x + px * (R + 52), y + py * (R + 52), text="inicio", fill=CYAN, font=SMALL)


class PDAModule(ModuleFrame):
    def __init__(self, master, app):
        super().__init__(master, app, "Nivel 2 · Libres de contexto · Autómata de pila",
                         {k: v["desc"] for k, v in PDA_LANGS.items()})

    def examples(self):
        return PDA_LANGS[self.lang.get()]["ex"]

    def compute(self, text):
        return PDA_LANGS[self.lang.get()]["run"](text)

    def draw(self, s):
        cv = self.cv
        cv.delete("all")
        draw_strip(cv, self.text, s["pos"] if s else None, 45)
        stack = s["stack"] if s else ["$"]
        state = s["state"] if s else "q0"
        cv.create_text(30, 125, text=f"Estado: {state}", anchor="w", fill=ACC, font=BIG)
        if s:
            draw_msg(cv, s["msg"], 30, 165, 330, "nw")
        shown = stack[-8:]
        base = self.H - 36
        for i, item in enumerate(shown):
            y1 = base - (i + 1) * 32
            y2 = y1 + 30
            top = i == len(shown) - 1
            cv.create_rectangle(455, y1, 585, y2, fill=ACC if top else CELL, outline=FG)
            cv.create_text(520, (y1 + y2) / 2, text=item, fill=BG if top else FG, font=MONO)
            if top:
                cv.create_text(598, (y1 + y2) / 2, text="← tope", anchor="w", fill=WARN, font=SMALL)
        if len(stack) > 8:
            cv.create_text(520, base - 8 * 32 - 8, text="⋮", fill=MUTED, font=BIG)
        cv.create_text(520, self.H - 14, text="PILA (LIFO)", fill=MUTED, font=SMALL)


class MachineModule(ModuleFrame):
    def __init__(self, master, app, title, machines, bounded):
        self.machines = machines
        self.bounded = bounded
        self.cache = {}
        super().__init__(master, app, title, {k: v["desc"] for k, v in machines.items()})

    def build_extra(self, parent):
        tk.Button(parent, text="Ver tabla de transiciones δ", command=self.show_table, bg=CELL, fg=FG,
                  activebackground=ACC, relief="flat", pady=3, cursor="hand2").pack(fill="x")

    def machine(self):
        name = self.lang.get()
        if name not in self.cache:
            self.cache[name] = self.machines[name]["build"]()
        return self.cache[name]

    def examples(self):
        return self.machines[self.lang.get()]["ex"]

    def validate(self, text):
        al = self.machine()["alphabet"]
        bad = sorted({c for c in text if c not in al})
        if bad:
            raise ValueError(f"Símbolos no permitidos: {' '.join(bad)}\nAlfabeto de entrada: {' '.join(al)}")

    def gamma(self):
        m = self.machine()
        g = set(m["alphabet"])
        if not self.bounded:
            g.add("_")
        for (q, sym), (new, w, mv) in m["delta"].items():
            g.add(sym)
            g.add(w)
        return "Alfabeto de la cinta Γ = { " + ", ".join(sorted(g)) + " }" + ("     (_ = blanco)" if not self.bounded else "")

    def compute(self, text):
        m = self.machine()
        steps, ok = run_machine(m, text, self.bounded)
        if ok:
            last = dict(steps[-1])
            content = "".join(last["tape"][k] for k in sorted(last["tape"]) if last["tape"][k] not in "_⊢⊣")
            last["msg"] = f"Estado de aceptación {last['state']} alcanzado → acepta. Contenido de la cinta: '{content}'"
            steps.append(last)
        return steps, ok

    def show_table(self):
        m = self.machine()
        win = tk.Toplevel(self)
        win.title("Tabla de transiciones δ")
        win.configure(bg=BG)
        t = tk.Text(win, width=46, height=28, bg=PANEL, fg=FG, font=("Courier New", 11), relief="flat")
        t.pack(padx=10, pady=10)
        t.insert("end", f"Estado inicial: {m['start']}\nEstados de aceptación: {', '.join(sorted(m['accept']))}\n\n")
        t.insert("end", "δ(estado, leído) = (nuevo, escribe, mueve)\n\n")
        for (q, sym), (new, w, mv) in sorted(m["delta"].items()):
            t.insert("end", f"δ({q}, {sym}) = ({new}, {w}, {mv})\n")
        t.config(state="disabled")

    def draw(self, s):
        cv = self.cv
        W = self.W
        cv.delete("all")
        cv.create_text(W / 2, 28, text=self.gamma(), fill=MUTED, font=UI)
        if self.bounded:
            cv.create_text(W / 2, 52, text="Cinta acotada: ⊢ w ⊣  (solo |w| + 2 celdas, el cabezal no puede salir)", fill=MUTED, font=SMALL)
        else:
            cv.create_text(W / 2, 52, text="Cinta infinita en ambos sentidos: se extiende con blancos (□)", fill=MUTED, font=SMALL)
        if s is None:
            cv.create_text(W / 2, self.H / 2, text="Escribe una cadena y presiona Iniciar", fill=MUTED, font=UI)
            return
        cv.create_text(W / 2, 95, text=f"Estado activo: {s['state']}", fill=ACC, font=BIG)
        head, tape = s["head"], s["tape"]
        cw, cells = 46, 13
        x0 = (W - cells * cw) / 2
        y1, y2 = 150, 196
        half = cells // 2
        for k in range(-half, half + 1):
            p = head + k
            if self.bounded and p not in tape:
                continue
            x = x0 + (k + half) * cw
            sym = tape.get(p, "_")
            disp = "□" if sym == "_" else sym
            if k == 0:
                fill, fg = ACC, BG
            elif sym in "⊢⊣":
                fill, fg = CELL, WARN
            elif sym in "XYZ":
                fill, fg = CELL, CYAN
            else:
                fill, fg = CELL, FG
            cv.create_rectangle(x, y1, x + cw, y2, fill=fill, outline=BG, width=2)
            cv.create_text(x + cw / 2, (y1 + y2) / 2, text=disp, fill=fg, font=("Courier New", 18, "bold"))
            cv.create_text(x + cw / 2, y2 + 12, text=str(p), fill=MUTED, font=SMALL)
        if not self.bounded:
            cv.create_text(x0 - 16, (y1 + y2) / 2, text="⋯", fill=MUTED, font=BIG)
            cv.create_text(x0 + cells * cw + 16, (y1 + y2) / 2, text="⋯", fill=MUTED, font=BIG)
        xc = x0 + half * cw + cw / 2
        cv.create_polygon(xc, y2 + 28, xc - 9, y2 + 46, xc + 9, y2 + 46, fill=WARN, outline="")
        cv.create_text(xc, y2 + 60, text="cabezal de lectura/escritura", fill=WARN, font=SMALL)
        draw_msg(cv, s["msg"], W / 2, 330, W - 60)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de la Jerarquía de Chomsky")
        self.geometry("1120x780")
        self.minsize(1100, 760)
        self.configure(bg=BG)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=CELL, background=CELL, foreground=FG, arrowcolor=FG)
        style.map("TCombobox", fieldbackground=[("readonly", CELL)], foreground=[("readonly", FG)])
        style.configure("TSpinbox", fieldbackground=CELL, background=CELL, foreground=FG, arrowcolor=FG)
        self.option_add("*TCombobox*Listbox.background", CELL)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        self.option_add("*TCombobox*Listbox.selectBackground", ACC)
        self.option_add("*TCombobox*Listbox.selectForeground", BG)
        self.current = None
        self.modules = {
            3: DFAModule(self, self),
            2: PDAModule(self, self),
            1: MachineModule(self, self, "Nivel 1 · Sensibles al contexto · Autómata linealmente acotado",
                             LBA_MACHINES, True),
            0: MachineModule(self, self, "Nivel 0 · Recursivamente enumerables · Máquina de Turing",
                             TM_MACHINES, False),
        }
        self.menu = self.build_menu()
        self.show_menu()

    def build_menu(self):
        f = tk.Frame(self, bg=BG)
        tk.Label(f, text="Jerarquía de Chomsky", bg=BG, fg=ACC, font=("Segoe UI", 30, "bold")).pack(pady=(60, 4))
        tk.Label(f, text="Selecciona un módulo para simular el modelo computacional de cada nivel",
                 bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(pady=(0, 40))
        grid = tk.Frame(f, bg=BG)
        grid.pack()
        cards = [
            (3, "Nivel 3", "Lenguajes regulares", "Autómata finito determinista"),
            (2, "Nivel 2", "Lenguajes libres de contexto", "Autómata de pila (memoria LIFO)"),
            (1, "Nivel 1", "Lenguajes sensibles al contexto", "Autómata linealmente acotado"),
            (0, "Nivel 0", "Lenguajes recursivamente enumerables", "Máquina de Turing"),
        ]
        for i, (key, lvl, name, model) in enumerate(cards):
            b = tk.Button(grid, text=f"{lvl}\n{name}\n{model}", width=36, height=6, bg=PANEL, fg=FG,
                          activebackground=ACC, activeforeground=BG, relief="flat", font=("Segoe UI", 12),
                          cursor="hand2", command=lambda k=key: self.open(k))
            b.grid(row=i // 2, column=i % 2, padx=14, pady=14)
        tk.Label(f, text="Sistemas · Politécnico Grancolombiano", bg=BG, fg=MUTED, font=SMALL).pack(pady=30)
        return f

    def show_menu(self):
        if self.current is not None:
            self.current.stop()
            self.current.pack_forget()
            self.current = None
        self.menu.pack(fill="both", expand=True)

    def open(self, key):
        self.menu.pack_forget()
        self.current = self.modules[key]
        self.current.pack(fill="both", expand=True)


if __name__ == "__main__":
    App().mainloop()
