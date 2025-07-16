# Projeto Final: Montagem e Funcionamento do Robô Cachorro

O projeto final consistiu na montagem e no funcionamento completo de um robô quadrúpede. A meta principal era demonstrar o controle do robô por meio de um controle remoto e a execução de todos os movimentos propostos.

---

## Funcionalidades

O robô foi projetado para apresentar as seguintes funcionalidades:

* **Movimentação Básica:**
    * Caminhar para frente e para trás.
    * Girar para ambos os lados (direita e esquerda).
* **Ajuste de Altura:**
    * Variar sua altura, indo da posição totalmente em pé até deitado.
* **Truque "Dar a Patinha":**
    * Sentar e balançar uma das patas dianteiras enquanto move a cabeça.
* **Modo Autônomo:**
    * Andar para frente de forma autônoma e desviar ao encontrar um obstáculo.

---

## Hardware Utilizado

Os seguintes componentes foram utilizados para a construção do projeto:

* **Controlador Principal:** 1x Arduino UNO
* **Módulos de Controle e Sensores:**
    * 1x Módulo PCA9685 (Controlador de Servo Motores)
    * 2x Módulos Bluetooth HC-05 (um para o robô, outro para o controle)
    * 1x Módulo HC-SR04 (Sensor de Distância Ultrassônico)
* **Alimentação:**
    * 1x XL4005 (Regulador de Tensão Step-Down)
    * 1x Suporte duplo para baterias 18650
    * 2x Suportes únicos para baterias 18650 (ligados em série)
    * 4x Baterias 18650
* **Atuadores e Componentes Diversos:**
    * 9x Servos Motores MG90
    * 1x Protoboard
    * Jumpers (macho-macho, macho-fêmea)
    * 1x Botão Switch On/Off
    * 1x LED Vermelho (utilizado como nariz do robô)
    * 1x Resistor de 110 Ω
* **Controle Remoto:**
    * 1x Placa BitDogLab

---

## Ligações dos Componentes

As conexões elétricas foram realizadas da seguinte maneira:

* **Sensor de Distância (HC-SR04):**
    * `Echo` → Pino `A3` do Arduino
    * `Trig` → Pino `A2` do Arduino
    * `VCC` → Saída `5V` do Arduino
    * `GND` → `GND` do Arduino
* **Módulo Bluetooth (HC-05 - Mestre/Controle):**
    * `TX` → Pino `0` (RX) do Arduino
    * `RX` → Pino `1` (TX) do Arduino
    * `VCC` → Alimentação `5V`
* **Controlador de Servos (PCA9685):**
    * `SDA` → Pino `SDA` do Arduino
    * `SCL` → Pino `SCL` do Arduino
    * `VCC` → Saída `3.3V` do Arduino
* **Regulador de Tensão (XL4005):**
    * `IN+` → Saída de `8.4V` das baterias
    * `IN-` → `GND` comum do circuito
    * `OUT+` → Pino `V+` da PCA9685 (para alimentar os servos)

---

## Estrutura do Robô

A estrutura física do robô foi montada com base no modelo encontrado no projeto original que inspirou este trabalho. O link para o projeto de referência pode ser encontrado abaixo:

* **Link do Projeto Original:** [Build yourself this simple, app-controlled robot dog](https://blog.arduino.cc/2024/03/08/build-yourself-this-simple-app-controlled-robot-dog/)
