"""
Programa de audiometria que utiliza o DAC PCM5102 para gerar tons puros
em diferentes frequencias, com saida estereo (canais esquerdo e direito separados)
e interface de botoes para resposta do paciente.
Autores: Vitor Rolim Cardoso (v204077@dac.unicamp.br) e Henrique Stumm Rocha (h239694@dac.unicamp.br)
"""

import machine
import rp2
from machine import Pin, I2S
import time
import random
import math
from neopixel import NeoPixel

############################################################
# Configuracao do Clock de 1.024MHz para o PCM5102
############################################################

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def clock_gen():
    """Gera um sinal de clock de 1.024MHz usando PIO"""
    wrap_target()
    set(pins, 1) [1]  # Mantem nivel alto por 1 ciclo
    set(pins, 0) [1]  # Mantem nivel baixo por 1 ciclo
    wrap()

# Inicializa o clock no pino GP16
# Frequencia calculada para 16kHz de sample rate com PLL interno:
# BCK = 64 * Fs = 64 * 16000 = 1.024MHz
clock_pin = machine.Pin(16)
clock_sm = rp2.StateMachine(0, clock_gen, freq=1_024_000, set_base=clock_pin)
clock_sm.active(1)  # Ativa o clock

############################################################
# Configuracoes Globais do Audiometro
############################################################

# Frequencias padrao para teste auditivo (em Hz)
FREQUENCIAS_AUDIOMETRIA = [125, 250, 500, 1000, 2000, 4000, 8000]

# Configuracoes da matriz de LEDs
NUM_LEDS = 25        # Numero de LEDs na matriz
LED_PIN = 7          # Pino de controle da matriz
BRILHO = 20          # Intensidade dos LEDs (0-255)

# Taxa de amostragem do audio (Hz)
SAMPLE_RATE = 16000  # 16kHz, suficiente para frequencias ate 8kHz

############################################################
# Inicializacao de Hardware
############################################################

# Matriz de LEDs NeoPixel (feedback visual)
np = NeoPixel(Pin(LED_PIN), NUM_LEDS)
current_led_index = 0  # Indice do LED atual

# Botoes de resposta do paciente
botao1 = Pin(5, Pin.IN, Pin.PULL_UP)  # Botao para canal esquerdo
botao2 = Pin(6, Pin.IN, Pin.PULL_UP)  # Botao para canal direito

# LED RGB para feedback adicional
led_red = Pin(12, Pin.OUT)    # LED Vermelho
led_green = Pin(13, Pin.OUT)  # LED Verde
led_blue = Pin(11, Pin.OUT)   # LED Azul

############################################################
# Configuracao da Interface I2S para o PCM5102
############################################################

"""
Pinos I2S:
- BCK (Bit Clock): GP18 - Clock de bits (gerado automaticamente)
- LRCK (Word Select): GP19 - Selecao de canal (L/R)
- DIN (Data In): GP20 - Dados de audio

Configuracao do PCM5102:
- SCK aterrado: usa PLL interno
- BCK de 1.024MHz para 16kHz de sample rate
- Formato I2S padrao, 16 bits, estereo
"""
i2s = I2S(
    0,                      # ID do periferico I2S
    sck=Pin(18),            # BCK - Clock de bits
    ws=Pin(19),             # LRCK - Clock de palavras (Left/Right)
    sd=Pin(20),             # DIN - Dados de audio
    mode=I2S.TX,            # Modo transmissap
    bits=16,                # Resolucao de 16 bits
    format=I2S.STEREO,      # Formato estereo
    rate=SAMPLE_RATE,       # Taxa de amostragem
    ibuf=1024               # Tamanho do buffer interno
)

############################################################
# Funcoes Principais
############################################################

def generate_tone_chunk(freq, amplitude, phase, chunk_size, canal):
    """
    Gera um bloco de amostras de audio para um tom senoidal
    Args:
        freq: frequencia do tom em Hz
        amplitude: volume do som (0-32767)
        phase: fase atual do sinal
        chunk_size: numero de amostras a gerar
        canal: 0=esquerdo, 1=direito
    Returns:
        (samples, new_phase): tupla com amostras e nova fase
    """
    samples = bytearray(chunk_size * 4)  # 2 canais x 2 bytes por amostra
    volume = min(amplitude, 32767)      # Limita amplitude maxima
    
    for i in range(chunk_size):
        # Gera valor senoidal para o tom
        value = int(volume * math.sin(2 * math.pi * freq * (phase + i) / SAMPLE_RATE))
        
        if canal == 0:  # Canal esquerdo
            # Preenche canal esquerdo (little endian)
            samples[i*4] = value & 0xff       # Byte menos significativo
            samples[i*4+1] = (value >> 8) & 0xff  # Byte mais significativo
            # Canal direito em silencio
            samples[i*4+2] = 0
            samples[i*4+3] = 0
        else:  # Canal direito
            # Canal esquerdo em silencio
            samples[i*4] = 0
            samples[i*4+1] = 0
            # Preenche canal direito
            samples[i*4+2] = value & 0xff
            samples[i*4+3] = (value >> 8) & 0xff
    
    return samples, (phase + chunk_size) % SAMPLE_RATE

def update_led_matrix(correct):
    """
    Atualiza a matriz de LEDs com o historico de respostas
    Args:
        correct: True para resposta correta, False para incorreta
    """
    global current_led_index
    
    # Reinicia a matriz quando chega ao final
    if current_led_index >= NUM_LEDS:
        np.fill((0, 0, 0))
        np.write()
        current_led_index = 0
    
    # Define cor conforme acerto (verde) ou erro (vermelho)
    color = (0, BRILHO, 0) if correct else (BRILHO, 0, 0)
    np[current_led_index] = color
    np.write()
    current_led_index += 1

def set_led_color(red, green, blue):
    """
    Controla o LED RGB principal
    Args:
        red: estado do LED vermelho (0 ou 1)
        green: estado do LED verde (0 ou 1)
        blue: estado do LED azul (0 ou 1)
    """
    led_red.value(red)
    led_green.value(green)
    led_blue.value(blue)

def play_tone(freq, duration, correct_button, amplitude, canal):
    """
    Reproduz um tom pelo I2S e aguarda resposta do paciente
    Args:
        freq: frequencia do tom em Hz
        duration: duracao em segundos
        correct_button: botao correto para esta resposta
        amplitude: volume do som (0-32767)
        canal: 0=esquerdo, 1=direito
    """
    phase = 0  # Fase inicial do sinal
    start_time = time.ticks_ms()
    button_pressed = False
    correct_response = False
    chunk_size = 256  # Tamanho do bloco de amostras
    
    # Loop de reproducao do tom
    while time.ticks_diff(time.ticks_ms(), start_time) < duration * 1000:
        # Gera e envia bloco de amostras
        chunk, phase = generate_tone_chunk(freq, amplitude, phase, chunk_size, canal)
        i2s.write(chunk)
        
        # Verifica botoes
        if correct_button.value() == 0:  # Botao correto pressionado
            button_pressed = True
            correct_response = True
        elif ((canal == 0 and botao2.value() == 0) or 
              (canal == 1 and botao1.value() == 0)):
            button_pressed = True
            correct_response = False
    
    # Finaliza reproducao
    i2s.deinit()
    
    # Feedback visual
    if button_pressed:
        update_led_matrix(correct_response)
        set_led_color(0, 1 if correct_response else 0, 0 if correct_response else 1)
    else:
        update_led_matrix(False)  # Nenhuma resposta
        set_led_color(1, 1, 0)   # Amarelo para timeout
    
    time.sleep(1)  # Pausa entre tons
    set_led_color(0, 0, 0)  # Desliga LED RGB

############################################################
# Loop Principal
############################################################

def main():
    """Funcao principal do programa"""
    # Inicializa hardware
    clock_sm.active(1)  # Garante clock ativo
    set_led_color(0, 0, 0)  # LED RGB desligado
    np.fill((0, 0, 0))  # Matriz de LEDs apagada
    np.write()
    
    # Loop infinito de teste auditivo
    while True:
        # Seleciona canal aleatorio (0=esquerdo, 1=direito)
        canal = random.choice([0, 1])
        botao_correto = botao1 if canal == 0 else botao2
        
        # Intervalo aleatorio entre tons (2-5 segundos)
        time.sleep(random.uniform(2, 5))
        
        # Configura parametros do tom
        nivel_sinal = random.randint(128, 2048)  # Amplitude aleatoria
        tom_freq = random.choice(FREQUENCIAS_AUDIOMETRIA)  # Frequencia padrao
        
        # Reconfigura interface I2S para garantir sincronismo
        global i2s
        i2s = I2S(
            0,
            sck=Pin(18),
            ws=Pin(19),
            sd=Pin(20),
            mode=I2S.TX,
            bits=16,
            format=I2S.STEREO,
            rate=SAMPLE_RATE,
            ibuf=1024
        )
        
        # Reproduz o tom e aguarda resposta
        play_tone(tom_freq, 1, botao_correto, nivel_sinal, canal)

# Ponto de entrada do programa
if __name__ == "__main__":
    main()
