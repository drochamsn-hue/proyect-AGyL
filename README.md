# Simulador de Chomsky

Aplicación de escritorio con interfaz gráfica que permite visualizar y simular los modelos computacionales de los cuatro niveles de la Jerarquía de Chomsky. Cada módulo ejecuta la cadena paso a paso (manual o automático) y muestra el estado interno del modelo.

| Nivel | Lenguajes | Modelo | Qué se visualiza |
|---|---|---|---|
| 3 | Regulares | Autómata finito determinista | Diagrama de estados, estado actual y símbolo leído |
| 2 | Libres de contexto | Autómata de pila | Pila LIFO con apilar/desapilar en cada paso |
| 1 | Sensibles al contexto | Autómata linealmente acotado | Cinta acotada con ⊢ y ⊣ y cabezal bidireccional |
| 0 | Recursivamente enumerables | Máquina de Turing | Cinta extendible, alfabeto Γ, cabezal y estado activo |

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido con Python en Windows y macOS)
- Linux (Debian/Ubuntu): `sudo apt install python3-tk`

No necesita instalar librerías externas.

## Instalación y ejecución

```bash
git clone https://github.com/drochamsn-hue/proyect-AGyL.git
cd proyect-AGyL
python chomsky_app.py
```

En Linux/macOS use `python3 chomsky_app.py`.

## Manual de uso

1. En el menú principal elija uno de los cuatro módulos.
2. Seleccione el lenguaje en la lista desplegable (en el Nivel 3 también puede cambiar el valor de N para el lenguaje "Múltiplos de N").
3. Escriba una cadena en el campo de entrada o haga clic en una de las cadenas de prueba de la lista inferior (se carga y se inicia sola).
4. Use los botones:
   - **Iniciar**: carga la cadena y muestra la configuración inicial.
   - **Paso >**: avanza una transición.
   - **Auto >>**: avanza automáticamente; el control deslizante ajusta el retardo.
   - **Pausa**: detiene la animación automática.
   - **Reiniciar**: limpia la simulación.
5. Al terminar se muestra **ACEPTADA** o **RECHAZADA**. El registro inferior lista cada transición aplicada.
6. En los niveles 1 y 0 el botón **Ver tabla de transiciones δ** muestra la función de transición completa.

## Estructura del código

| Elemento | Responsabilidad |
|---|---|
| `dfa_*`, `DFA_LANGS` | Definición de los autómatas finitos |
| `pda_*`, `PDA_LANGS` | Simulación de los autómatas de pila |
| `rule`, `build_*`, `run_machine` | Motor genérico de máquina con cinta, usado por el LBA (cinta acotada) y la Máquina de Turing (cinta infinita) |
| `ModuleFrame` | Interfaz común: controles, ejecución paso a paso, registro |
| `DFAModule`, `PDAModule`, `MachineModule` | Dibujo específico de cada nivel |
| `App` | Ventana principal y menú |

Cada simulación primero calcula la lista completa de configuraciones (pasos) y luego la interfaz solo las recorre y dibuja.

## Cadenas de prueba (✔ acepta, ✘ rechaza)

### Nivel 3 – Autómata finito

- **Cadenas binarias con cantidad par de 1s**: `ε` ✔, `11` ✔, `1010` ✔, `1` ✘, `0111` ✘, `10001` ✔
- **Cadenas binarias que terminan en 01**: `01` ✔, `1101` ✔, `0` ✘, `10` ✘, `0100` ✘, `101` ✔
- **Cadenas sobre {a,b} que contienen 'aba'**: `aba` ✔, `babab` ✔, `aab` ✘, `bbb` ✘, `abba` ✘, `bbabab` ✔
- **Múltiplos de N en binario (N parametrizable)** (con N = 3): `0` ✔, `11` ✔, `110` ✔, `100` ✘, `111` ✘, `1001` ✔

### Nivel 2 – Autómata de pila

- **aⁿbⁿ  (n ≥ 1)**: `ab` ✔, `aaabbb` ✔, `aabbb` ✘, `abab` ✘, `ε` ✘, `aab` ✘
- **Paréntesis balanceados ( ) [ ] { }**: `(())` ✔, `()[]{}` ✔, `{[()]}` ✔, `([)]` ✘, `((` ✘, `ε` ✔
- **w c wᴿ  sobre {a,b}**: `abcba` ✔, `c` ✔, `abbcbba` ✔, `abcab` ✘, `ab` ✘, `acb` ✘

### Nivel 1 – Autómata linealmente acotado

- **aⁿbⁿcⁿ  (n ≥ 1)**: `abc` ✔, `aabbcc` ✔, `aaabbbccc` ✔, `aabbc` ✘, `abcabc` ✘, `acb` ✘, `ε` ✘

### Nivel 0 – Máquina de Turing

- **Suma unaria  (1ᵐ+1ⁿ → 1ᵐ⁺ⁿ)**: `11+111` ✔, `1+1` ✔, `+11` ✔, `111+` ✔, `11` ✘, `1++1` ✘
- **Palíndromos sobre {a,b}**: `abba` ✔, `aba` ✔, `aabaa` ✔, `ab` ✘, `abab` ✘, `ε` ✔
- **Incremento binario (+1)**: `1011` ✔, `111` ✔, `0` ✔, `100` ✔, `1` ✔
