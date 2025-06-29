from machine import Pin, ADC
import utime
import machine

uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1)) #modulo bluetooth em modo mestre

joy_button = Pin(22, Pin.IN, Pin.PULL_UP) 
joy_x = ADC(Pin(27))  # Joystick X
joy_y = ADC(Pin(26))  # Joystick Y

BUTTON_B = 6       # GPIO6 para o botão B altura para cima
BUTTON_A = 5       # GPIO5 para o botão A altura para baixo

button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)
button_a = Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)

last_joystick_check = 0
joystick_interval = 50  # ms (mesmo intervalo do timer anterior)
last_x = 32768
last_y = 32768
threshold = 10000
direction = "S"
ciclico = 0  
LAST_COMAND = "S"
DEBOUNCE_DELAY = 0.5  # segundos


mode = "M"

Comando_enviado = "S"

HEIGHT_STATES = ["U", "U", "U", "D", "D", "D"]
current_height_state = 2

def read_joystick():
    """Lê o joystick e retorna a direção"""
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    if x < 15000: return "L"
    elif x > 50000: return "R"
    elif y < 15000: return "B"
    elif y > 50000: return "F"
    else:
        #se o joystick estiver no centro, retorna "S" (parado)
        return "S"
    
def set_mode():
    """Checa se o botao do joystick foi pressionado e muda o modo"""
    global mode
    if not joy_button.value():  # Verifica se o botão do joystick foi pressionado
        mode = "M" if mode == "A" else "A"
        print(f"Modo alterado para: {mode}")
        utime.sleep(0.5)  # Debounce do botão
    
    return mode


def check_joystick_movement():
    """função de controle do joystick"""
    global direction, last_x, last_y, last_joystick_check
    
    now = utime.ticks_ms()
    new_direction = direction  
    if utime.ticks_diff(now, last_joystick_check) >= joystick_interval:
        last_joystick_check = now
        
        x = joy_x.read_u16()
        y = joy_y.read_u16()
        
        if abs(x - last_x) > threshold or abs(y - last_y) > threshold:
            new_direction = read_joystick()

    return new_direction


while True:
    if not joy_button.value():  # Verifica se o botão do joystick foi pressionado
        print("Botão pressionado!")
        modo = set_mode()#checa se o botão do joystick foi pressionado para mudar o modo
        Comando_enviado = modo  # Reseta o comando quando o botão é pressionado
        utime.sleep(0.5)  # Debounce do botão

    
    new_direction = check_joystick_movement()
    
    if new_direction != direction:
        print(f"Direção: {new_direction}")
        direction = new_direction
        last_x = joy_x.read_u16()
        last_y = joy_y.read_u16()
        Comando_enviado = direction

    elif not button_b.value():
        utime.sleep(DEBOUNCE_DELAY)
        print("Botão B pressionado! Altura ajustada")
        Comando_enviado = HEIGHT_STATES[current_height_state]
        current_height_state = (current_height_state + 1) % len(HEIGHT_STATES)


    elif not button_a.value():
        print("Botão A pressionado!")
        Comando_enviado = 'V' #sai hi

    
    ##envia comando para o bluetooth baudrate 9600
    if Comando_enviado != LAST_COMAND:
        # Envia o comando apenas se for diferente do último enviado
        #EVITA SOBRECARGA DE ENVIO XDD
        LAST_COMAND = Comando_enviado
        uart.write(Comando_enviado)
        print(f"Comando enviado: {Comando_enviado}")

    if Comando_enviado in ["U","D"]:
        uart.write(Comando_enviado)
        Comando_enviado = "null"
        print(f"Comando enviado: {Comando_enviado}")


        
    utime.sleep(0.1)  # Intervalo para evitar sobrecarga de lesitura


       