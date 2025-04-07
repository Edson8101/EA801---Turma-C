from machine import Pin
import neopixel

# --- Inicializar matriz de LED
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

# --- Mapeamento da matriz física
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# --- Brilho e cores
BRILHO = 0.1
COR = (0, 255, 0)
OFF = (0, 0, 0)

COR = tuple(int(c * BRILHO) for c in COR)

# --- Fontes 5x5 para números
NUMEROS = {
    0: [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]][::-1],
    1: [[0,0,1,0,0],[0,1,1,0,0],[1,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]][::-1],
    2: [[1,1,1,1,0],[0,0,0,0,1],[0,1,1,1,0],[1,0,0,0,0],[1,1,1,1,1]][::-1],
    3: [[1,1,1,1,1],[0,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[1,1,1,1,1]][::-1],
    4: [[1,0,0,1,0],[1,0,0,1,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,0,1,0]][::-1],
    5: [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[0,0,0,0,1],[1,1,1,1,0]][::-1],
    6: [[0,1,1,1,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[0,1,1,1,0]][::-1],
    7: [[1,1,1,1,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0]][::-1],
    8: [[0,1,1,1,0],[1,0,0,0,1],[0,1,1,1,0],[1,0,0,0,1],[0,1,1,1,0]][::-1],
    9: [[0,1,1,1,0],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,1,1,1,0]][::-1]
}

# --- Limpar matriz
def limpar():
    for i in range(NUM_LEDS):
        np[i] = OFF
    np.write()

# --- Mostrar um número (0-9)
def mostrar_numero(n):
    limpar()
    matriz = NUMEROS.get(n)
    if not matriz:
        return
    for y in range(5):
        for x in range(5):
            if matriz[y][x]:
                np[LED_MATRIX[y][x]] = COR
    np.write()

# --- Mostrar ponto de exclamação (!)
def mostrar_exclamacao():
    limpar()
    desenho = [
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,0,0,0],
        [0,0,1,0,0],
    ][::-1]
    for y in range(5):
        for x in range(5):
            if desenho[y][x]:
                np[LED_MATRIX[y][x]] = COR
    np.write()

# --- Mostrar X

def mostrar_x():
    limpar()
    desenho = [
        [1,0,0,0,1],
        [0,1,0,1,0],
        [0,0,1,0,0],
        [0,1,0,1,0],
        [1,0,0,0,1]
    ][::-1]
    for y in range(5):
        for x in range(5):
            if desenho[y][x]:
                np[LED_MATRIX[y][x]] = COR
    np.write()

