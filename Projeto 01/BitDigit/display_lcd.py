from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

# --- Inicialização do display
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# --- Parâmetros
ESCALA = 2
LARG = 28
ALT = 28
offset_x = (128 - LARG * ESCALA) // 2
offset_y = (64 - ALT * ESCALA) // 2

# --- Função pública para uso no main
def desenhar_imagem(imagem):
    oled.fill(0)
    for y in range(ALT):
        for x in range(LARG):
            idx = y * LARG + x
            cor = 1 if imagem[idx] > 0.3 else 0
            if cor:
                oled.fill_rect(offset_x + x * ESCALA, offset_y + y * ESCALA, ESCALA, ESCALA, 1)
    oled.show()

