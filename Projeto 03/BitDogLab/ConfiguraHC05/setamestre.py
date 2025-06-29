# Script Final Corrigido para configurar um módulo HC-05 como MESTRE
# Versão inclui pausa estratégica para estabilização do módulo após o comando ROLE.

from machine import UART, Pin
import time

# =================================================================
#               VERIFIQUE ESTA INFORMAÇÃO
# Confirme se este é o endereço do seu módulo ESCRAVO.
# =================================================================
ENDERECO_ESCRAVO = "98da:50:03c600"
# =================================================================

# --- Pinos de Conexão ---
UART_TX_PIN = 0  # Conectado ao RXD do HC-05
UART_RX_PIN = 1  # Conectado ao TXD do HC-05

# --- Configurações do Mestre ---
SENHA_PAREAMENTO = "1234"      # Deve ser a mesma senha configurada no escravo
BAUD_RATE_COMUNICACAO = 9600 # Baud rate para a comunicação normal (pós-configuração)

# Baud Rate para o modo AT é fixo em 38400
BAUD_RATE_AT = 38400

# Inicializa a comunicação UART
uart = UART(0, baudrate=BAUD_RATE_AT, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN))


def enviar_comando_at(comando, resposta_esperada="OK", timeout=3000):
    """
    Envia um comando AT para o HC-05, aguarda a resposta e verifica se foi bem-sucedido.
    Timeout aumentado para 3000ms para maior robustez.
    """
    print(f"Enviando Comando: {comando}")
    uart.write(comando + '\r\n')
    time.sleep_ms(timeout)
    
    resposta = uart.read()
    
    if resposta:
        resposta_str = resposta.decode('utf-8', 'ignore').strip()
        print(f"Resposta Recebida: {resposta_str}")
        if resposta_esperada in resposta_str:
            print(">>> Comando executado com sucesso.")
            return True
        else:
            print(">>> Falha na execução do comando.")
            return False
    else:
        print(">>> Nenhuma resposta recebida.")
        return False

def configurar_mestre():
    """
    Executa a sequência de comandos para configurar o módulo como mestre,
    incluindo pausas para estabilização.
    """
    print("--- Iniciando Configuração do Módulo Mestre (Versão Corrigida) ---")
    print("Certifique-se que o pino EN/KEY está conectado a 3.3V.")
    time.sleep(1)

    # Formata o endereço do escravo para o formato do comando BIND
    endereco_formatado = ENDERECO_ESCRAVO.replace(':', ',')

    # Inicia a sequência de configuração
    if not enviar_comando_at("AT"):
        print("\nERRO CRÍTICO: Não foi possível comunicar com o módulo.")
        print("Verifique a alimentação e as conexões TX/RX.")
        return

    enviar_comando_at("AT+ORGL")
    
    # Comando crítico que causa a reinicialização interna
    enviar_comando_at("AT+ROLE=1")

    # === PAUSA ESTRATÉGICA ===
    print("\n[AVISO] Módulo reconfigurado. Aguardando reinicialização interna...")
    time.sleep(2) # Pausa de 2 segundos para o módulo estabilizar.
    print("Continuando configuração...\n")
    # =========================
    
    # Re-testar a comunicação para garantir que o módulo está respondendo novamente
    if not enviar_comando_at("AT"):
        print("\nERRO CRÍTICO: Módulo não respondeu após a reconfiguração de ROLE.")
        return
        
    # Continua com o resto dos comandos
    enviar_comando_at(f"AT+PSWD={SENHA_PAREAMENTO}")
    enviar_comando_at("AT+CMODE=0")
    enviar_comando_at(f"AT+UART={BAUD_RATE_COMUNICACAO},0,0")
    enviar_comando_at(f"AT+BIND={endereco_formatado}")
    enviar_comando_at("AT+INIT")
    
    print("\n--- Configuração do Mestre Concluída! ---")
    print("TODOS OS COMANDOS ENVIADOS.")
    print("\nIMPORTANTE: Para usar, desconecte o pino EN do 3.3V e reinicie a alimentação.")
    print("O Mestre agora tentará se conectar ao Escravo automaticamente.")


# --- Executa a função principal ---
if __name__ == "__main__":
    configurar_mestre()