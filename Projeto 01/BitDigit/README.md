# 📷 Reconhecimento de Dígitos com Raspberry Pi Pico W (MNIST + OLED + LEDs + Bluetooth)

Este projeto implementa um sistema embarcado completo de reconhecimento de dígitos usando uma imagem em formato MNIST. Ele roda localmente no **Raspberry Pi Pico W** com firmware MicroPython, utilizando uma interface interativa com:

- Display OLED
- Matriz de LEDs RGB (5x5)
- Joystick e botões físicos
- Comunicação Bluetooth BLE com celular

---

## 👥 Autores

- **Enzo Guimarães Campos** – RA: 247069
- **Rafael Pissaia Savitsky** – RA: 248459  

---

## 🚀 Visão Geral

O sistema permite ao usuário percorrer imagens de dígitos usando o joystick, visualizar a imagem no OLED e, ao pressionar o botão A, realizar a inferência local do dígito. O resultado é mostrado na matriz de LEDs. Em seguida, o usuário pode enviar o resultado via BLE para um dispositivo conectado pressionando o botão B.

---

## 🔧 Especificações do Sistema

### 🔌 Firmware e Ambiente
- **Firmware MicroPython**: v1.24.1
- **Pico SDK**: v2.0.0
- **Toolchain**: ARM GCC 10.x

### 📚 Bibliotecas Utilizadas
- `aioble`: para comunicação Bluetooth BLE
- `bluetooth`: nativo do MicroPython
- `uasyncio`: para multitarefa assíncrona
- `ssd1306.py`: biblioteca para controle do display OLED via I2C

### 🧩 Periféricos Conectados
| Periférico              | Função                            | GPIO(s)                     |
|-------------------------|-----------------------------------|-----------------------------|
| Display OLED (SSD1306)  | Exibição da imagem MNIST          | GPIO14 (SDA), GPIO15 (SCL)  |
| Matriz de LEDs RGB (5x5)| Exibição do resultado/animações   | GPIO7                       |
| Botão A                 | Iniciar inferência                | GPIO5                       |
| Botão B                 | Enviar resultado via BLE          | GPIO6                       |
| Joystick Horizontal     | Navegar entre imagens             | GPIO26 (VRx)                |
| LED RGB Discreto        | Indicação de status BLE           | GPIO11, GPIO12, GPIO13      |

---

## 🧠 Como Funciona o Sistema

1. **Inicialização**
   - Display OLED e matriz de LED são apagados.
   - O LED RGB inicia em **vermelho**, indicando que não há conexão BLE ativa.

2. **Conexão BLE**
   - A placa entra em modo de anúncio BLE com o nome `PicoMNIST`.
   - Ao conectar via celular (ex: aplicativo BLE Scanner), o LED RGB muda para **azul**.

3. **Escolha da Imagem**
   - Use o **joystick** para navegar entre as imagens `imagem_X.txt`.
   - A imagem correspondente é exibida no OLED.

4. **Inferência do Dígito (Botão A)**
   - Pressione o **botão A** para iniciar a inferência.
   - A matriz de LEDs exibe `!` enquanto processa.
   - A inferência ocorre localmente com o algoritmo `predict()`.
   - O resultado (0 a 9) aparece na matriz de LEDs.

5. **Envio do Resultado (Botão B)**
   - Pressione o **botão B** para enviar o resultado via BLE.
   - Um `X` é exibido na matriz e o número é transmitido como `uint8` via GATT.

6. **Repetição**
   - O usuário pode selecionar outra imagem e repetir o processo.

---

## 📁 Estrutura de Arquivos Sugerida

```
/
├── main.py                 # Arquivo principal
├── display_lcd.py         # Controle do OLED
├── matriz_led.py          # Funções para LED RGB e matriz
├── mnist_inferencia.py    # Inferência do modelo MNIST
├── ssd1306.py             # Biblioteca OLED
├── weights.bin            # Pesos do modelo (binário)
├── biases.txt             # Biases do modelo (texto)
├── imagem_1.txt           # Imagens MNIST simuladas
├── imagem_2.txt
├── ...
```

---

## 📲 Como Testar a Conexão BLE

1. Baixe um app como **nRF Connect** ou **BLE Scanner** no celular.
2. Ligue a placa e verifique se o dispositivo `PicoMNIST` aparece.
3. Conecte ao dispositivo. O LED RGB ficará **azul**.
4. Pressione o botão A para inferir e o botão B para enviar.
5. Leia o valor transmitido na característica GATT.

---
