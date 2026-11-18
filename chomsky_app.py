import math
import tkinter as tk
from tkinter import messagebox

ANCHO = 700
ALTO = 440
RADIO = 26
NOMBRE_MOD = "Múltiplos de N en binario"

TITULOS = {
    3: "Nivel 3 - Lenguajes regulares - Autómata finito",
    2: "Nivel 2 - Libres de contexto - Autómata de pila",
    1: "Nivel 1 - Sensibles al contexto - Autómata linealmente acotado",
    0: "Nivel 0 - Recursivamente enumerables - Máquina de Turing",
}

DESCRIPCIONES = {
    3: {
        "Cantidad par de 1s": "Cadenas binarias con un número par de 1s. Tiene dos estados: q0 (par) y q1 (impar).",
        "Terminan en 01": "Cadenas binarias que terminan en 01. El autómata recuerda los últimos símbolos leídos.",
        "Contienen aba": "Cadenas con a y b que contienen la subcadena aba. Al llegar a q3 ya se acepta.",
        NOMBRE_MOD: "Números binarios que son múltiplos de N. Cada estado guarda el residuo de dividir entre N. Se puede cambiar N.",
    },
    2: {
        "a^n b^n": "Cadenas con n letras a seguidas de n letras b (n >= 1). Cada a apila una A y cada b desapila una A.",
        "Paréntesis balanceados": "Paréntesis (), [] y {} bien cerrados. Cada apertura se apila y cada cierre debe coincidir con el tope.",
        "w c w^R": "Una cadena de a y b, luego una c, y la misma cadena al revés. Ejemplo: abcba.",
    },
    1: {
        "a^n b^n c^n": "Cadenas con n letras a, n letras b y n letras c (n >= 1). La cinta está limitada por < y >. Se marcan las letras con X, Y y Z.",
    },
    0: {
        "Suma unaria": "Suma dos números en unario. Ejemplo: 11+111 deja 11111 en la cinta.",
        "Palíndromos": "Acepta cadenas de a y b que se leen igual al derecho y al revés.",
        "Incremento binario": "Le suma 1 a un número binario. Ejemplo: 1011 queda como 1100.",
    },
}

EJEMPLOS = {
    "Cantidad par de 1s": ["", "11", "1010", "1", "0111", "10001"],
    "Terminan en 01": ["01", "1101", "0", "10", "0100", "101"],
    "Contienen aba": ["aba", "babab", "aab", "bbb", "abba", "bbabab"],
    "a^n b^n": ["ab", "aaabbb", "aabbb", "abab", "", "aab"],
    "Paréntesis balanceados": ["(())", "()[]{}", "{[()]}", "([)]", "((", ""],
    "w c w^R": ["abcba", "c", "abbcbba", "abcab", "ab", "acb"],
    "a^n b^n c^n": ["abc", "aabbcc", "aaabbbccc", "aabbc", "abcabc", "acb", ""],
    "Suma unaria": ["11+111", "1+1", "+11", "111+", "11", "1++1"],
    "Palíndromos": ["abba", "aba", "aabaa", "ab", "abab", ""],
    "Incremento binario": ["1011", "111", "0", "100", "1"],
}


def crear_afd(nombre, n):
    if nombre == "Cantidad par de 1s":
        estados = ["q0", "q1"]
        t = {("q0", "0"): "q0", ("q0", "1"): "q1",
             ("q1", "0"): "q1", ("q1", "1"): "q0"}
        return estados, t, "q0", ["q0"]
    if nombre == "Terminan en 01":
        estados = ["q0", "q1", "q2"]
        t = {("q0", "0"): "q1", ("q0", "1"): "q0",
             ("q1", "0"): "q1", ("q1", "1"): "q2",
             ("q2", "0"): "q1", ("q2", "1"): "q0"}
        return estados, t, "q0", ["q2"]
    if nombre == "Contienen aba":
        estados = ["q0", "q1", "q2", "q3"]
        t = {("q0", "a"): "q1", ("q0", "b"): "q0",
             ("q1", "a"): "q1", ("q1", "b"): "q2",
             ("q2", "a"): "q3", ("q2", "b"): "q0",
             ("q3", "a"): "q3", ("q3", "b"): "q3"}
        return estados, t, "q0", ["q3"]
    estados = []
    t = {}
    for i in range(n):
        estados.append("q" + str(i))
        for bit in range(2):
            t[("q" + str(i), str(bit))] = "q" + str((2 * i + bit) % n)
    return estados, t, "q0", ["q0"]


def simular_afd(afd, cadena):
    estados, t, inicial, finales = afd
    estado = inicial
    pasos = [{"pos": 0, "estado": estado, "arista": None, "texto": "Estado inicial: " + estado}]
    for i in range(len(cadena)):
        simbolo = cadena[i]
        if (estado, simbolo) not in t:
            pasos.append({"pos": i, "estado": estado, "arista": None,
                          "texto": f"El símbolo '{simbolo}' no pertenece al alfabeto, se rechaza"})
            return pasos, False
        nuevo = t[(estado, simbolo)]
        pasos.append({"pos": i + 1, "estado": nuevo, "arista": (estado, nuevo),
                      "texto": f"Lee '{simbolo}': pasa de {estado} a {nuevo}"})
        estado = nuevo
    acepta = estado in finales
    if acepta:
        texto = "Termina en " + estado + ", que es de aceptación"
    else:
        texto = "Termina en " + estado + ", que NO es de aceptación"
    pasos.append({"pos": len(cadena), "estado": estado, "arista": None, "texto": texto})
    return pasos, acepta


def paso_pila(pasos, pos, estado, pila, texto):
    pasos.append({"pos": pos, "estado": estado, "pila": list(pila), "texto": texto})


def pila_anbn(cadena):
    pasos = []
    estado = "q0"
    pila = ["$"]
    paso_pila(pasos, 0, estado, pila, "Inicio: la pila solo tiene el marcador $")
    for i in range(len(cadena)):
        simbolo = cadena[i]
        if simbolo == "a" and estado == "q0":
            pila.append("A")
            paso_pila(pasos, i + 1, estado, pila, "Lee 'a': apila A")
        elif simbolo == "b" and pila[-1] == "A":
            pila.pop()
            estado = "q1"
            paso_pila(pasos, i + 1, estado, pila, "Lee 'b': desapila A y pasa a q1")
        else:
            paso_pila(pasos, i, estado, pila, f"Lee '{simbolo}': no hay regla, se rechaza")
            return pasos, False
    acepta = estado == "q1" and pila == ["$"]
    if acepta:
        texto = "Fin de la cadena: estado q1 y pila vacía, se acepta"
    else:
        texto = "Fin de la cadena: no se cumple la condición, se rechaza"
    paso_pila(pasos, len(cadena), estado, pila, texto)
    return pasos, acepta


def pila_parentesis(cadena):
    pasos = []
    pila = ["$"]
    pares = {")": "(", "]": "[", "}": "{"}
    paso_pila(pasos, 0, "q0", pila, "Inicio: la pila solo tiene el marcador $")
    for i in range(len(cadena)):
        simbolo = cadena[i]
        if simbolo in "([{":
            pila.append(simbolo)
            paso_pila(pasos, i + 1, "q0", pila, f"Lee '{simbolo}': lo apila")
        elif simbolo in pares and pila[-1] == pares[simbolo]:
            pila.pop()
            paso_pila(pasos, i + 1, "q0", pila, f"Lee '{simbolo}': coincide con el tope, lo desapila")
        else:
            paso_pila(pasos, i, "q0", pila, f"Lee '{simbolo}': no coincide con el tope, se rechaza")
            return pasos, False
    acepta = pila == ["$"]
    if acepta:
        texto = "Fin de la cadena: la pila quedó vacía, se acepta"
    else:
        texto = "Fin de la cadena: quedaron símbolos sin cerrar, se rechaza"
    paso_pila(pasos, len(cadena), "q0", pila, texto)
    return pasos, acepta


def pila_wcwr(cadena):
    pasos = []
    estado = "q0"
    pila = ["$"]
    paso_pila(pasos, 0, estado, pila, "Inicio: la pila solo tiene el marcador $")
    for i in range(len(cadena)):
        simbolo = cadena[i]
        if estado == "q0" and (simbolo == "a" or simbolo == "b"):
            pila.append(simbolo)
            paso_pila(pasos, i + 1, estado, pila, f"Lee '{simbolo}': lo apila")
        elif estado == "q0" and simbolo == "c":
            estado = "q1"
            paso_pila(pasos, i + 1, estado, pila, "Lee 'c' (el centro): pasa a q1")
        elif estado == "q1" and simbolo == pila[-1]:
            pila.pop()
            paso_pila(pasos, i + 1, estado, pila, f"Lee '{simbolo}': coincide con el tope, lo desapila")
        else:
            paso_pila(pasos, i, estado, pila, f"Lee '{simbolo}': no hay regla, se rechaza")
            return pasos, False
    acepta = estado == "q1" and pila == ["$"]
    if acepta:
        texto = "Fin de la cadena: estado q1 y pila vacía, se acepta"
    else:
        texto = "Fin de la cadena: no se cumple la condición, se rechaza"
    paso_pila(pasos, len(cadena), estado, pila, texto)
    return pasos, acepta


def simular_pila(nombre, cadena):
    if nombre == "a^n b^n":
        return pila_anbn(cadena)
    if nombre == "Paréntesis balanceados":
        return pila_parentesis(cadena)
    return pila_wcwr(cadena)


def agregar(reglas, estados, simbolos, nuevo, escribe, mueve):
    for estado in estados.split():
        for simbolo in simbolos:
            estado_nuevo = nuevo
            if estado_nuevo is None:
                estado_nuevo = estado
            simbolo_escrito = escribe
            if simbolo_escrito is None:
                simbolo_escrito = simbolo
            reglas[(estado, simbolo)] = (estado_nuevo, simbolo_escrito, mueve)


def crear_maquina(nombre):
    reglas = {}
    if nombre == "a^n b^n c^n":
        agregar(reglas, "q0", "<", "q1", None, "R")
        agregar(reglas, "q1", "a", "q2", "X", "R")
        agregar(reglas, "q1", "X", None, None, "R")
        agregar(reglas, "q1", "Y", "q5", None, "R")
        agregar(reglas, "q2", "aY", None, None, "R")
        agregar(reglas, "q2", "b", "q3", "Y", "R")
        agregar(reglas, "q3", "bZ", None, None, "R")
        agregar(reglas, "q3", "c", "q4", "Z", "L")
        agregar(reglas, "q4", "abcXYZ", None, None, "L")
        agregar(reglas, "q4", "<", "q1", None, "R")
        agregar(reglas, "q5", "YZ", None, None, "R")
        agregar(reglas, "q5", ">", "qa", None, "S")
        return reglas, "q0", ["qa"], "abc"
    if nombre == "Suma unaria":
        agregar(reglas, "s0", "1", None, None, "R")
        agregar(reglas, "s0", "+", "s1", "1", "R")
        agregar(reglas, "s1", "1", None, None, "R")
        agregar(reglas, "s1", "_", "s2", "_", "L")
        agregar(reglas, "s2", "1", "fin", "_", "S")
        return reglas, "s0", ["fin"], "1+"
    if nombre == "Palíndromos":
        agregar(reglas, "q0", "a", "qa", "_", "R")
        agregar(reglas, "q0", "b", "qb", "_", "R")
        agregar(reglas, "q0", "_", "fin", "_", "S")
        agregar(reglas, "qa", "ab", None, None, "R")
        agregar(reglas, "qa", "_", "ra", "_", "L")
        agregar(reglas, "qb", "ab", None, None, "R")
        agregar(reglas, "qb", "_", "rb", "_", "L")
        agregar(reglas, "ra", "a", "volver", "_", "L")
        agregar(reglas, "ra", "_", "fin", "_", "S")
        agregar(reglas, "rb", "b", "volver", "_", "L")
        agregar(reglas, "rb", "_", "fin", "_", "S")
        agregar(reglas, "volver", "ab", None, None, "L")
        agregar(reglas, "volver", "_", "q0", "_", "R")
        return reglas, "q0", ["fin"], "ab"
    agregar(reglas, "r", "01", None, None, "R")
    agregar(reglas, "r", "_", "c", "_", "L")
    agregar(reglas, "c", "1", None, "0", "L")
    agregar(reglas, "c", "0", "fin", "1", "S")
    agregar(reglas, "c", "_", "fin", "1", "S")
    return reglas, "r", ["fin"], "01"


def ejecutar_maquina(reglas, inicio, aceptacion, cadena, acotada):
    cinta = {}
    limite = 0
    if acotada:
        cinta[0] = "<"
        for i in range(len(cadena)):
            cinta[i + 1] = cadena[i]
        cinta[len(cadena) + 1] = ">"
        limite = len(cadena) + 1
    else:
        for i in range(len(cadena)):
            cinta[i] = cadena[i]
    cabezal = 0
    estado = inicio
    pasos = [{"cinta": dict(cinta), "cabezal": cabezal, "estado": estado,
              "texto": "Configuración inicial: cabezal en la posición 0"}]
    contador = 0
    while contador < 1000:
        if estado in aceptacion:
            return pasos, True
        simbolo = cinta.get(cabezal, "_")
        if (estado, simbolo) not in reglas:
            pasos.append({"cinta": dict(cinta), "cabezal": cabezal, "estado": estado,
                          "texto": f"No hay regla para ({estado}, {simbolo}): se rechaza"})
            return pasos, False
        nuevo, escribe, mueve = reglas[(estado, simbolo)]
        cinta[cabezal] = escribe
        if mueve == "R":
            cabezal = cabezal + 1
        elif mueve == "L":
            cabezal = cabezal - 1
        texto = f"Regla ({estado}, {simbolo}) = ({nuevo}, {escribe}, {mueve})"
        estado = nuevo
        if acotada and (cabezal < 0 or cabezal > limite):
            pasos.append({"cinta": dict(cinta), "cabezal": cabezal, "estado": estado,
                          "texto": "El cabezal se salió de la cinta acotada: se rechaza"})
            return pasos, False
        pasos.append({"cinta": dict(cinta), "cabezal": cabezal, "estado": estado, "texto": texto})
        contador = contador + 1
    pasos.append({"cinta": dict(cinta), "cabezal": cabezal, "estado": estado,
                  "texto": "Se llegó al límite de 1000 pasos, se detiene"})
    return pasos, False


def alfabeto_cinta(reglas, alfabeto, acotada):
    simbolos = []
    for s in alfabeto:
        if s not in simbolos:
            simbolos.append(s)
    if not acotada and "_" not in simbolos:
        simbolos.append("_")
    for (estado, simbolo), (nuevo, escribe, mueve) in reglas.items():
        if simbolo not in simbolos:
            simbolos.append(simbolo)
        if escribe not in simbolos:
            simbolos.append(escribe)
    simbolos.sort()
    return "{" + ", ".join(simbolos) + "}"


class Modulo(tk.Frame):
    def __init__(self, master, app, nivel):
        tk.Frame.__init__(self, master)
        self.app = app
        self.nivel = nivel
        self.pasos = []
        self.indice = 0
        self.automatico = False
        self.trabajo = None
        self.cadena = ""
        self.acepta = False
        self.ejemplos = []
        self.n = None

        arriba = tk.Frame(self)
        arriba.pack(fill="x", padx=10, pady=8)
        tk.Button(arriba, text="< Menú principal", command=app.mostrar_menu).pack(side="left")
        tk.Label(arriba, text=TITULOS[nivel], font=("Arial", 13, "bold")).pack(side="left", padx=15)

        cuerpo = tk.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=10)
        izq = tk.Frame(cuerpo, width=260)
        izq.pack(side="left", fill="y")
        izq.pack_propagate(False)
        der = tk.Frame(cuerpo)
        der.pack(side="left", padx=10)

        tk.Label(izq, text="Lenguaje:", font=("Arial", 10, "bold")).pack(anchor="w")
        nombres = list(DESCRIPCIONES[nivel])
        self.lenguaje = tk.StringVar(value=nombres[0])
        tk.OptionMenu(izq, self.lenguaje, *nombres, command=self.cambiar_lenguaje).pack(fill="x")

        if nivel == 3:
            fila = tk.Frame(izq)
            fila.pack(fill="x", pady=4)
            tk.Label(fila, text="N (solo múltiplos de N):").pack(side="left")
            self.n = tk.Spinbox(fila, from_=2, to=6, width=4, command=self.cambiar_lenguaje)
            self.n.delete(0, "end")
            self.n.insert(0, "3")
            self.n.pack(side="left", padx=5)

        self.descripcion = tk.Label(izq, wraplength=245, justify="left", fg="dimgray")
        self.descripcion.pack(fill="x", pady=8)

        tk.Label(izq, text="Cadena de entrada:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.entrada = tk.Entry(izq, font=("Courier", 14))
        self.entrada.pack(fill="x", pady=3)
        self.entrada.bind("<Return>", lambda e: self.iniciar())

        botones = tk.Frame(izq)
        botones.pack(fill="x", pady=6)
        tk.Button(botones, text="Iniciar", command=self.iniciar).grid(row=0, column=0, sticky="ew")
        tk.Button(botones, text="Paso", command=self.siguiente).grid(row=0, column=1, sticky="ew")
        tk.Button(botones, text="Auto", command=self.auto).grid(row=1, column=0, sticky="ew")
        tk.Button(botones, text="Pausa", command=self.pausar).grid(row=1, column=1, sticky="ew")
        tk.Button(botones, text="Reiniciar", command=self.reiniciar).grid(row=2, column=0, columnspan=2, sticky="ew")
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        if nivel < 2:
            tk.Button(izq, text="Ver tabla de reglas", command=self.mostrar_tabla).pack(fill="x", pady=4)

        tk.Label(izq, text="Cadenas de prueba (clic para usar):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 2))
        self.lista = tk.Listbox(izq, height=8, font=("Courier", 10), exportselection=False)
        self.lista.pack(fill="x")
        self.lista.bind("<<ListboxSelect>>", self.elegir_ejemplo)

        self.lienzo = tk.Canvas(der, width=ANCHO, height=ALTO, bg="white", highlightthickness=1)
        self.lienzo.pack()
        self.estado_label = tk.Label(der, text="", font=("Arial", 12, "bold"))
        self.estado_label.pack(pady=4)
        self.registro = tk.Text(der, height=7, width=85, state="disabled", font=("Courier", 9))
        self.registro.pack()

        self.cambiar_lenguaje()

    def obtener_n(self):
        try:
            n = int(self.n.get())
        except ValueError:
            n = 3
        if n < 2:
            n = 2
        if n > 6:
            n = 6
        return n

    def obtener_afd(self):
        return crear_afd(self.lenguaje.get(), self.obtener_n())

    def obtener_ejemplos(self):
        nombre = self.lenguaje.get()
        if nombre == NOMBRE_MOD:
            n = self.obtener_n()
            lista = ["0", bin(n)[2:], bin(3 * n)[2:], bin(n + 1)[2:], bin(2 * n + 1)[2:]]
            sin_repetir = []
            for x in lista:
                if x not in sin_repetir:
                    sin_repetir.append(x)
            return sin_repetir
        return EJEMPLOS[nombre]

    def calcular(self, cadena):
        nombre = self.lenguaje.get()
        if self.nivel == 3:
            return simular_afd(self.obtener_afd(), cadena)
        if self.nivel == 2:
            return simular_pila(nombre, cadena)
        reglas, inicio, aceptacion, alfabeto = crear_maquina(nombre)
        pasos, acepta = ejecutar_maquina(reglas, inicio, aceptacion, cadena, self.nivel == 1)
        if acepta:
            ultimo = dict(pasos[-1])
            contenido = ""
            for pos in sorted(ultimo["cinta"]):
                simbolo = ultimo["cinta"][pos]
                if simbolo not in "_<>":
                    contenido = contenido + simbolo
            ultimo["texto"] = "Estado de aceptación: " + ultimo["estado"] + ". Cinta final: '" + contenido + "'"
            pasos.append(ultimo)
        return pasos, acepta

    def cambiar_lenguaje(self, valor=None):
        self.descripcion.config(text=DESCRIPCIONES[self.nivel][self.lenguaje.get()])
        self.reiniciar()
        self.ejemplos = self.obtener_ejemplos()
        self.lista.delete(0, "end")
        for e in self.ejemplos:
            resultado = self.calcular(e)[1]
            texto = e
            if e == "":
                texto = "(vacía)"
            if resultado:
                self.lista.insert("end", texto.ljust(14) + "ACEPTA")
            else:
                self.lista.insert("end", texto.ljust(14) + "RECHAZA")

    def elegir_ejemplo(self, evento):
        seleccion = self.lista.curselection()
        if len(seleccion) == 0:
            return
        self.entrada.delete(0, "end")
        self.entrada.insert(0, self.ejemplos[seleccion[0]])
        self.iniciar()

    def escribir_registro(self, linea):
        self.registro.config(state="normal")
        self.registro.insert("end", linea + "\n")
        self.registro.see("end")
        self.registro.config(state="disabled")

    def limpiar_registro(self):
        self.registro.config(state="normal")
        self.registro.delete("1.0", "end")
        self.registro.config(state="disabled")

    def reiniciar(self):
        self.pausar()
        self.pasos = []
        self.indice = 0
        self.cadena = ""
        self.limpiar_registro()
        self.estado_label.config(text="", fg="black")
        self.dibujar(None)

    def iniciar(self):
        self.pausar()
        cadena = self.entrada.get().strip()
        if self.nivel < 2:
            alfabeto = crear_maquina(self.lenguaje.get())[3]
            for letra in cadena:
                if letra not in alfabeto:
                    messagebox.showwarning("Cadena no válida",
                                           "Solo se permiten estos símbolos: " + alfabeto)
                    return False
        self.cadena = cadena
        self.pasos, self.acepta = self.calcular(cadena)
        self.indice = 0
        self.limpiar_registro()
        self.mostrar()
        return True

    def mostrar(self):
        paso = self.pasos[self.indice]
        self.dibujar(paso)
        self.escribir_registro(str(self.indice) + ". " + paso["texto"])
        if self.indice == len(self.pasos) - 1:
            if self.acepta:
                self.estado_label.config(text="CADENA ACEPTADA", fg="green")
            else:
                self.estado_label.config(text="CADENA RECHAZADA", fg="red")
        else:
            self.estado_label.config(text="Paso " + str(self.indice) + " de " + str(len(self.pasos) - 1), fg="black")

    def siguiente(self):
        if len(self.pasos) == 0:
            self.iniciar()
            return
        if self.indice < len(self.pasos) - 1:
            self.indice = self.indice + 1
            self.mostrar()

    def auto(self):
        if len(self.pasos) == 0 or self.indice >= len(self.pasos) - 1:
            if not self.iniciar():
                return
        self.automatico = True
        self.trabajo = self.after(600, self.repetir)

    def repetir(self):
        if not self.automatico:
            return
        if self.indice < len(self.pasos) - 1:
            self.indice = self.indice + 1
            self.mostrar()
            self.trabajo = self.after(600, self.repetir)
        else:
            self.automatico = False

    def pausar(self):
        self.automatico = False
        if self.trabajo is not None:
            self.after_cancel(self.trabajo)
            self.trabajo = None

    def mostrar_tabla(self):
        reglas, inicio, aceptacion, alfabeto = crear_maquina(self.lenguaje.get())
        ventana = tk.Toplevel(self)
        ventana.title("Tabla de reglas")
        texto = tk.Text(ventana, width=45, height=28, font=("Courier", 10))
        texto.pack(padx=10, pady=10)
        texto.insert("end", "Estado inicial: " + inicio + "\n")
        texto.insert("end", "Estado de aceptación: " + ", ".join(aceptacion) + "\n\n")
        texto.insert("end", "(estado, lee) = (nuevo estado, escribe, mueve)\n\n")
        for clave in sorted(reglas):
            nuevo, escribe, mueve = reglas[clave]
            texto.insert("end", f"({clave[0]}, {clave[1]}) = ({nuevo}, {escribe}, {mueve})\n")
        texto.config(state="disabled")

    def dibujar(self, paso):
        if self.nivel == 3:
            self.dibujar_afd(paso)
        elif self.nivel == 2:
            self.dibujar_pila(paso)
        else:
            self.dibujar_cinta(paso)

    def dibujar_cadena(self, pos):
        c = self.lienzo
        c.create_text(ANCHO / 2, 14, text="Cadena de entrada")
        cadena = self.cadena
        if cadena == "":
            c.create_text(ANCHO / 2, 45, text="(cadena vacía)", font=("Arial", 14))
            return
        ancho = min(36, (ANCHO - 40) / len(cadena))
        inicio = (ANCHO - ancho * len(cadena)) / 2
        for i in range(len(cadena)):
            x = inicio + i * ancho
            color = "lightgray"
            if i < pos:
                color = "lightgreen"
            elif i == pos:
                color = "gold"
            c.create_rectangle(x, 28, x + ancho, 62, fill=color)
            c.create_text(x + ancho / 2, 45, text=cadena[i], font=("Courier", 14, "bold"))
        if pos < len(cadena):
            marca = inicio + pos * ancho + ancho / 2
        else:
            marca = inicio + len(cadena) * ancho
        c.create_text(marca, 76, text="^", font=("Arial", 12, "bold"))

    def dibujar_afd(self, paso):
        c = self.lienzo
        c.delete("all")
        arista_actual = None
        if paso is not None:
            self.dibujar_cadena(paso["pos"])
            arista_actual = paso["arista"]
        estados, t, inicial, finales = self.obtener_afd()
        n = len(estados)
        centro_x = ANCHO / 2
        centro_y = 240
        coordenadas = {}
        for i in range(n):
            angulo = 2 * math.pi * i / n - math.pi / 2
            coordenadas[estados[i]] = (centro_x + 230 * math.cos(angulo), centro_y + 100 * math.sin(angulo))
        aristas = {}
        for (origen, simbolo), destino in t.items():
            clave = (origen, destino)
            if clave not in aristas:
                aristas[clave] = []
            aristas[clave].append(simbolo)
        for (origen, destino), simbolos in aristas.items():
            etiqueta = ",".join(sorted(simbolos))
            color = "black"
            grosor = 1
            if (origen, destino) == arista_actual:
                color = "red"
                grosor = 3
            x1, y1 = coordenadas[origen]
            if origen == destino:
                dx = x1 - centro_x
                dy = y1 - centro_y
                largo = math.hypot(dx, dy)
                ux = dx / largo
                uy = dy / largo
                cx = x1 + ux * (RADIO + 8)
                cy = y1 + uy * (RADIO + 8)
                c.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, outline=color, width=grosor)
                c.create_text(x1 + ux * (RADIO + 32), y1 + uy * (RADIO + 32), text=etiqueta, fill=color)
            else:
                x2, y2 = coordenadas[destino]
                dx = x2 - x1
                dy = y2 - y1
                largo = math.hypot(dx, dy)
                ux = dx / largo
                uy = dy / largo
                px = -uy * 6
                py = ux * 6
                ini_x = x1 + ux * RADIO + px
                ini_y = y1 + uy * RADIO + py
                fin_x = x2 - ux * RADIO + px
                fin_y = y2 - uy * RADIO + py
                c.create_line(ini_x, ini_y, fin_x, fin_y, arrow="last", fill=color, width=grosor)
                c.create_text(ini_x + (fin_x - ini_x) * 0.3 + px * 2, ini_y + (fin_y - ini_y) * 0.3 + py * 2,
                              text=etiqueta, fill=color)
        for nombre_estado in estados:
            x, y = coordenadas[nombre_estado]
            fondo = "white"
            if paso is not None and paso["estado"] == nombre_estado:
                fondo = "gold"
            c.create_oval(x - RADIO, y - RADIO, x + RADIO, y + RADIO, fill=fondo, width=2)
            if nombre_estado in finales:
                c.create_oval(x - RADIO + 5, y - RADIO + 5, x + RADIO - 5, y + RADIO - 5, width=2)
            c.create_text(x, y, text=nombre_estado, font=("Arial", 11, "bold"))
        x, y = coordenadas[inicial]
        c.create_line(x - RADIO - 40, y, x - RADIO, y, arrow="last", width=2, fill="blue")
        c.create_text(x - RADIO - 40, y - 12, text="inicio", fill="blue")
        if paso is not None:
            c.create_text(ANCHO / 2, ALTO - 18, text=paso["texto"], font=("Arial", 11))

    def dibujar_pila(self, paso):
        c = self.lienzo
        c.delete("all")
        pila = ["$"]
        estado = "q0"
        if paso is not None:
            self.dibujar_cadena(paso["pos"])
            pila = paso["pila"]
            estado = paso["estado"]
            c.create_text(30, 165, text=paso["texto"], anchor="nw", width=320, font=("Arial", 11))
        c.create_text(30, 120, text="Estado: " + estado, anchor="w", font=("Arial", 16, "bold"))
        visibles = pila[-8:]
        base = ALTO - 40
        for i in range(len(visibles)):
            y1 = base - (i + 1) * 32
            y2 = y1 + 30
            color = "lightblue"
            if i == len(visibles) - 1:
                color = "orange"
            c.create_rectangle(455, y1, 585, y2, fill=color)
            c.create_text(520, (y1 + y2) / 2, text=visibles[i], font=("Courier", 14, "bold"))
            if i == len(visibles) - 1:
                c.create_text(598, (y1 + y2) / 2, text="<- tope", anchor="w")
        if len(pila) > 8:
            c.create_text(520, base - 8 * 32 - 8, text="...")
        c.create_text(520, ALTO - 15, text="PILA (LIFO)")

    def dibujar_cinta(self, paso):
        c = self.lienzo
        c.delete("all")
        reglas, inicio, aceptacion, alfabeto = crear_maquina(self.lenguaje.get())
        acotada = self.nivel == 1
        c.create_text(ANCHO / 2, 20, text="Alfabeto de la cinta: " + alfabeto_cinta(reglas, alfabeto, acotada))
        if acotada:
            nota = "Cinta acotada: < cadena >  (el cabezal no puede salir de los delimitadores)"
        else:
            nota = "Cinta infinita: se extiende con blancos (_) hacia los dos lados"
        c.create_text(ANCHO / 2, 42, text=nota, fill="dimgray")
        if paso is None:
            c.create_text(ANCHO / 2, ALTO / 2, text="Escribe una cadena y presiona Iniciar")
            return
        c.create_text(ANCHO / 2, 85, text="Estado activo: " + paso["estado"], font=("Arial", 16, "bold"))
        cabezal = paso["cabezal"]
        cinta = paso["cinta"]
        ancho = 46
        inicio_x = (ANCHO - 13 * ancho) / 2
        for k in range(-6, 7):
            p = cabezal + k
            if acotada and p not in cinta:
                continue
            x = inicio_x + (k + 6) * ancho
            simbolo = cinta.get(p, "_")
            color = "lightgray"
            if k == 0:
                color = "gold"
            c.create_rectangle(x, 130, x + ancho, 176, fill=color)
            c.create_text(x + ancho / 2, 153, text=simbolo, font=("Courier", 18, "bold"))
            c.create_text(x + ancho / 2, 188, text=str(p), fill="gray")
        centro = inicio_x + 6 * ancho + ancho / 2
        c.create_polygon(centro, 205, centro - 9, 223, centro + 9, 223, fill="red")
        c.create_text(centro, 238, text="cabezal (lee y escribe)")
        c.create_text(ANCHO / 2, 310, text=paso["texto"], font=("Arial", 11), width=ANCHO - 60)


class Aplicacion(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Simulador de la Jerarquía de Chomsky")
        self.geometry("1020x720")
        self.minsize(1000, 700)
        self.modulos = {}
        for nivel in (3, 2, 1, 0):
            self.modulos[nivel] = Modulo(self, self, nivel)
        self.menu = tk.Frame(self)
        tk.Label(self.menu, text="Jerarquía de Chomsky", font=("Arial", 28, "bold")).pack(pady=(60, 5))
        tk.Label(self.menu, text="Elige un módulo para simular", font=("Arial", 12)).pack(pady=(0, 30))
        cuadro = tk.Frame(self.menu)
        cuadro.pack()
        textos = [
            (3, "Nivel 3\nLenguajes regulares\nAutómata finito"),
            (2, "Nivel 2\nLibres de contexto\nAutómata de pila"),
            (1, "Nivel 1\nSensibles al contexto\nAutómata linealmente acotado"),
            (0, "Nivel 0\nRecursivamente enumerables\nMáquina de Turing"),
        ]
        for i in range(4):
            nivel = textos[i][0]
            boton = tk.Button(cuadro, text=textos[i][1], width=32, height=6, font=("Arial", 12),
                              command=lambda n=nivel: self.abrir(n))
            boton.grid(row=i // 2, column=i % 2, padx=12, pady=12)
        self.actual = None
        self.mostrar_menu()

    def mostrar_menu(self):
        if self.actual is not None:
            self.actual.pausar()
            self.actual.pack_forget()
            self.actual = None
        self.menu.pack(fill="both", expand=True)

    def abrir(self, nivel):
        self.menu.pack_forget()
        self.actual = self.modulos[nivel]
        self.actual.pack(fill="both", expand=True)


if __name__ == "__main__":
    Aplicacion().mainloop()
