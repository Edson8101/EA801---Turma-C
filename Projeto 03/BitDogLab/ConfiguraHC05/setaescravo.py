# Script para configurar um módulo HC-05 como ESCRAVO
# ADAPTADO para quando o pino EN está LIGADO DIRETAMENTE em 3.3V

from machine import UART, Pin
import time

# --- Pinos de Conexão ---
UART_TX_PIN = 0  # Conectado ao RXD do HC-05
UART_RX_PIN = 1  # Conectado ao TXD do HC-05
# O pino AT_MODE_PIN não é mais necessário, pois o controle é físico

# --- Configurações do Escravo ---
NOME_ESCRAVO = "HC05_ESCRAVO"
SENHA_ESCRAVO = "1234"
BAUD_RATE_COMUNICACAO = 9600

# O Baud Rate para o modo AT é fixo em 38400
BAUD_RATE_AT = 38400

# Inicializa a comunicação UART para o modo AT
uart = UART(0, baudrate=BAUD_RATE_AT, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN), timeout=1000)

def enviar_comando_at(comando, resposta_esperada="OK"):
    """Envia um comando AT para o HC-05 e verifica a resposta."""
    print(f"Enviando Comando: {comando}")
    uart.write(comando + '\r\n')
    time.sleep(1.2)
    resposta = uart.read()
    if resposta:
        resposta_str = resposta.decode('utf-8').strip()
        print(f"Resposta Recebida: {resposta_str}")
        if resposta_esperada in resposta_str:
            print("Comando executado com sucesso.")
            return True, resposta_str
        else:
            print("Falha na execução do comando.")
            return False, resposta_str
    else:
        print("Nenhuma resposta recebida.")
        return False, None

def configurar_escravo_manual_at():
    """Executa a sequência de comandos AT. Pressupõe que o módulo JÁ ESTÁ em modo AT."""
    print("--- Iniciando Configuração do Módulo Escravo ---")
    print("Garantindo que o pino EN/KEY está conectado a 3.3V.")
    
    # Testa a comunicação
    sucesso, _ = enviar_comando_at("AT")
    if not sucesso:
        print("\nERRO: Não foi possível comunicar com o módulo HC-05.")
        print("Verifique as conexões TX/RX e se o pino EN está firmemente em 3.3V.")
        return

    # Comandos de configuração
    enviar_comando_at("AT+ORGL")
    enviar_comando_at("AT+ROLE=0")
    enviar_comando_at(f"AT+NAME={NOME_ESCRAVO}")
    enviar_comando_at(f"AT+PSWD={SENHA_ESCRAVO}")
    enviar_comando_at(f"AT+UART={BAUD_RATE_COMUNICACAO},0,0")

    # Obtém e exibe o endereço do módulo escravo
    print("\n--- PASSO CRÍTICO: Anote o endereço abaixo! ---")
    sucesso, resposta = enviar_comando_at("AT+ADDR?", resposta_esperada="+ADDR:")
    if sucesso:
        endereco = resposta.replace("+ADDR:", "").strip()
        print(f"*********************************************")
        print(f"* Endereço do Escravo: {endereco}  *")
        print(f"*********************************************")
    
    print("\n--- Configuração Concluída ---")
    print("IMPORTANTE: Para usar o módulo, desconecte o pino EN do 3.3V e reinicie a alimentação.")

# --- Executa a função principal ---
if __name__ == "__main__":
    configurar_escravo_manual_at()