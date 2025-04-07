from machine import Pin, PWM, ADC
import utime
import os
import struct
import uasyncio as asyncio
import aioble
import bluetooth

from display_lcd import desenhar_imagem
from matriz_led import mostrar_numero, limpar, mostrar_exclamacao, mostrar_x
from mnist_inferencia import prever_numero

# --- Botões
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)

# --- LED RGB
led_r = PWM(Pin(12))
led_g = PWM(Pin(13))
led_b = PWM(Pin(11))
for led in (led_r, led_g, led_b):
    led.freq(1000)

def led_rgb(r, g, b):
    led_r.duty_u16(r)
    led_g.duty_u16(g)
    led_b.duty_u16(b)

led_rgb(65535, 0, 0)  # Inicia vermelho

# --- Joystick (horizontal)
vr_x = ADC(Pin(26))
delay_joystick = 500
ultimo_movimento = utime.ticks_ms()

# --- BLE UUIDs
_SERVICO_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
_CARACTERISTICA_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

# --- Serviço e característica BLE
servico = aioble.Service(_SERVICO_UUID)
caracteristica = aioble.Characteristic(
    servico,
    _CARACTERISTICA_UUID,
    read=True,
    notify=False,
    write=False
)
aioble.register_services(servico)

# --- Número detectado mais recente
ultimo_resultado = 0

# --- Lista e carregamento de imagens
def listar_imagens():
    return sorted([f for f in os.listdir() if f.startswith("imagem_") and f.endswith(".txt")])

def carregar_imagem(caminho):
    with open(caminho) as f:
        return [float(x) for x in f.read().strip().split(",")]

# --- Loop principal da aplicação
async def loop_principal():
    global ultimo_resultado
    imagens = listar_imagens()
    indice = 0
    ultima_leitura_b = botao_b.value()
    ultima_leitura_a = botao_a.value()
    global ultimo_movimento

    while True:
        imagem = carregar_imagem(imagens[indice])
        desenhar_imagem(imagem)

        while True:
            leitura_b = botao_b.value()
            leitura_a = botao_a.value()
            agora = utime.ticks_ms()
            vr_x_val = vr_x.read_u16()

            # --- Joystick para mudar imagem
            if utime.ticks_diff(agora, ultimo_movimento) > delay_joystick:
                if vr_x_val > 65000:
                    indice = (indice - 1) % len(imagens)
                    ultimo_movimento = agora
                    break
                elif vr_x_val < 62000:
                    indice = (indice + 1) % len(imagens)
                    ultimo_movimento = agora
                    break

            # --- Botão A = rodar MNIST
            if ultima_leitura_a == 1 and leitura_a == 0:
                mostrar_exclamacao()

                resultado = prever_numero(imagem)
                ultimo_resultado = resultado

                mostrar_numero(resultado)

                while botao_a.value() == 0:
                    await asyncio.sleep_ms(100)
                break

            # --- Botão B = enviar resultado via BLE
            if ultima_leitura_b == 1 and leitura_b == 0:
                mostrar_x()
                try:
                    caracteristica.write(struct.pack("B", ultimo_resultado))
                    print("Número enviado via BLE:", ultimo_resultado)
                except Exception as e:
                    print("Erro ao enviar via BLE:", e)

                while botao_b.value() == 0:
                    await asyncio.sleep_ms(100)
                break

            ultima_leitura_a = leitura_a
            ultima_leitura_b = leitura_b
            await asyncio.sleep_ms(100)

# --- BLE advertising loop
async def ble_anunciar():
    while True:
        try:
            print("Anunciando BLE...")
            connection = await aioble.advertise(250_000, name="PicoMNIST", services=[_SERVICO_UUID])

            # Conectado → LED azul
            led_rgb(0, 0, 65535)
            print("Conectado via BLE.")

            await connection.disconnected()

            # Desconectado → LED vermelho
            led_rgb(65535, 0, 0)
            print("Desconectado.")
        except Exception as e:
            print("Erro BLE:", e)
        await asyncio.sleep(1)

# --- Executar tudo
async def main():
    await asyncio.gather(
        ble_anunciar(),
        loop_principal()
    )

asyncio.run(main())

