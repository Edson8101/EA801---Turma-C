# Projeto de sistema de audiometria portátil de baixo custo [Parte 3] - EA801/Projeto 3

**Autores:**
- **Henrique Stumm Rocha**
  - *Faculdade de Engenharia Elétrica e de Computação (FEEC), Universidade Estadual de Campinas*
  - *Email: h239694@dac.unicamp.br*
- **Vitor Rolim Cardoso**
  - *Faculdade de Engenharia Elétrica e de Computação (FEEC), Universidade Estadual de Campinas*
  - *Email: v204077@dac.unicamp.br*

---

## Introdução

A elevada complexidade e custo de equipamentos de audiometria tradicional (como o `\cite{formis2023}`, comercializado por R$15.990,00) limitam seu acesso em contextos de baixo orçamento, como clínicas de pequeno porte e regiões com recursos limitados. Sistemas embarcados, como os baseados em ESP32 ou Raspberry Pi, surgem como alternativas promissoras: com componentes de baixo custo, permitem implementar funcionalidades básicas de teste auditivo de forma portátil e acessível. No documento a seguir, apresentamos um sistema de audiometria básico utilizando o microcontrolador RP2350 `\cite{rp2350}` integrado à placa de desenvolvimento BitDogLab `\cite{bitdoglab}`, junto com uma série de componentes periféricos que permitem à placa de circuitos BitDogLab se comunicar com fones de ouvido analógicos P2.

Essa abordagem não substitui equipamentos profissionais, mas pode viabilizar triagens preliminares em condições em que o acesso a equipamentos tradicionais representa um custo proibitivo.

## Descrição Funcional

### Objetivo

O programa é um sistema interativo para avaliação auditiva em formato de jogo, onde o usuário deve identificar e responder a tons de frequências variadas emitidos por dois buzzers. O sistema fornece feedback visual imediato (via LED RGB) e histórico (via matriz de LEDs) sobre a precisão das respostas, simulando um teste de audiometria simplificado. Nessa terceira etapa do projeto, integramos todo o desenvolvimento do hardware em uma placa de circuito impresso (PCB) capaz de realizar a conexão entre todos os componentes e a conversão do sinal diferencial do amplificador classe D para sinal single-ended.

### Componentes Principais

* **Botões (2 unidades):**
    * O usuário deve pressionar o botão correspondente ao buzzer que emitiu o tom durante sua execução.
    * Respostas fora do intervalo do tom ou pressionamento do botão errado são consideradas incorretas.
* **Matriz de LEDs NeoPixel (5x5):**
    * Exibe um histórico sequencial das respostas:
        * Verde: Resposta correta (botão pressionado durante o tom).
        * Vermelho: Resposta ausente, incorreta ou fora do tempo.
    * Os LEDs são preenchidos da direita para a esquerda e de baixo para cima, reiniciando após 25 respostas.
* **LED RGB:**
    * Fornece feedback temporário (1 segundo) após cada resposta:
        * Verde: Resposta incorreta.
        * Vermelho: Resposta correta.
        * Magenta: Resposta ausente ou fora do tempo.
* **PCM5102:**
    * Conversor Digital-Analógico:
        * Recebe um sinal digital em protocolo I2S da BitDogLab e o converte em um sinal analógico de 2.1V centrado no GND.
        * Datasheet `\cite{PCM5102}`.
* **PAM8403:**
    * Amplificador de Áudio:
        * Recebe um sinal analógico do Conversor D/A PCM5102 e o amplifica para 5V de saída.
        * É um amplificador sem filtro, portanto, é necessário colocar um filtro LC na saída para atenuar o ruído no alto-falante.
        * Datasheet `\cite{PAM8403}`.
* **Filtro LC:**
    * Conjunto de indutores e capacitores para atenuar o ruído da saída do amplificador:
        * Para cada saída P2 temos um indutor de 10 uH e um capacitor de 470 nF conectados em série.
        * Foi necessário usar o filtro LC para filtrar o sinal PWM, que é característico de amplificador tipo D.
* **Saída de Áudio:**
    * A saída de áudio do projeto, agora integrada em uma PCB, é composta pelos seguintes elementos:
        * **Circuito de Conversão (LM324):** O sinal de áudio, gerado internamente de forma diferencial, é processado por um amplificador operacional **LM324**. Ele está configurado como um amplificador diferencial com ganho de atenuação (0.082) para converter o sinal para o formato single-ended e, ao mesmo tempo, eliminar o estouramento (clipping) do áudio.
        * **Conector de Saída P2:** O sinal já convertido é disponibilizado em um conector de áudio padrão P2 (3.5mm), permitindo a conexão universal com a maioria dos dispositivos de áudio.
        * **Carga de Saída (Fone de Ouvido):** O circuito foi projetado e validado para alimentar a carga de saída, especificamente um fone de 38.5 ohms (operando a 0.41 V), garantindo que o LM324 forneça o sinal com qualidade e sem perdas, mesmo considerando sua baixa capacidade de fornecer corrente para o fone.

### Funcionamento do Sistema

#### 1. Geração de Tons Aleatórios
* **Frequências:** Selecionadas aleatoriamente da lista `FREQUENCIAS_AUDIOMETRIA` (125 Hz a 8000 Hz).
* **Volume:** Amplitude aleatória (128 a 2048) para simular variações de intensidade sonora.
* **Buzzer Ativo:** Escolhido aleatoriamente (Buzzer 1 ou 2) a cada rodada.

#### 2. Lógica de Resposta
* **Tempo de Resposta:** O usuário tem 1 segundo para pressionar o botão correto após o início do tom.
* **Validação:**
    * Acerto: Botão correto pressionado durante o tom → LED RGB vermelho + LED verde na matriz.
    * Erro:
        * Botão errado pressionado → LED RGB verde + LED vermelho na matriz.
        * Nenhum botão pressionado → LED RGB magenta + LED vermelho na matriz.

#### 3. Matriz de LEDs (NeoPixel)
* **Sequenciamento:** Cada resposta acende um LED na posição atual (`current_led_index`), avançando até o 25º LED.
* **Reinício:** Ao chegar ao 25º LED, a matriz é apagada e o sequenciamento recomeça.
* **Brilho:** Configurado em nível reduzido (`BRILHO = 10`) para evitar saturação visual.

#### 4. LED RGB
* **Controle:**
    * Verde: `set_led_color(0, 1, 0)` (resposta incorreta).
    * Vermelho: `set_led_color(1, 0, 0)` (resposta correta).
    * Magenta: `set_led_color(0, 0, 1)` (resposta fora do tempo).
    * Desligado: Após 1 segundo, independentemente do resultado.

#### 5. Temporização e Aleatoriedade
* **Intervalo entre Tons:** 2 a 5 segundos (aleatório) para evitar padrões previsíveis.
* **Duração do Tom:** 1 segundo por padrão.

### Fluxo de Operação
1.  **Inicialização:**
    * LEDs RGB e matriz são desligados.
2.  **Loop Principal:**
    * Aguarda um intervalo aleatório (2-5 segundos).
    * Seleciona buzzer, frequência e volume aleatoriamente.
    * Toca o tom no buzzer escolhido.
    * Monitora pressionamento do botão correspondente durante o tom.
    * Atualiza a matriz de LEDs e o LED RGB conforme a resposta.
    * Repete o processo indefinidamente.

### Casos de Uso
* Teste Auditivo: Avaliação da capacidade do usuário de identificar tons em diferentes frequências e volumes.
* Treino de Discriminação Sonora: Prática para distinguir sons entre dois pontos (fones esquerdo/direito).
* Demonstração Visual: A matriz de LEDs serve como placar dinâmico para acompanhamento de progresso.

### Notas Técnicas
* **Microcontrolador:** Raspberry Pi Pico (RP2040) com suporte a PIO para geração de clock dedicado.
* **Clock de Alta Precisão:**
    * Gerador de clock de 1.024MHz via PIO (GP16).
    * Configuração PLL para sincronismo com PCM5102.
* **Conexões Principais:**
    * Interface I2S para PCM5102:
        * BCK: GP18 (Bit Clock)
        * LRCK: GP19 (Word Select)
        * DIN: GP20 (Dados de Áudio)
    * Controles:
        * Botões: GP5 (Canal Esquerdo), GP6 (Canal Direito)
        * Matriz NeoPixel: GP7 (25 LEDs, brilho configurável)
        * LED RGB: GP11 (Azul), GP12 (Vermelho), GP13 (Verde)
* **Parâmetros Customizáveis:**
    * Audio:
        * Taxa de amostragem (16kHz padrão)
        * Buffer I2S (1024 bytes)
        * Faixas de frequência (125Hz-8kHz)
    * Visuais:
        * Brilho LEDs (0-255)
        * Padrões de matriz (histórico de 25 testes)
        * Cores de feedback RGB
    * Lógica:
        * Intervalos entre testes (2-5s)
        * Níveis de amplitude (128-2048)
        * 
A equação abaixo descreve o comportamento da saída $V_o$ do amplificador diferencial, em função da entrada inversora $V_-$ e a entrada não inversora $V_+$. Os resistores estão rotulados como no esquemático.

$$
V_{o}=-\frac{R_{2}}{R_{1}}V_{-}+\frac{R_{4}}{R_{3}+R_{4}}\cdot\frac{R_{1}+R_{2}}{R_{1}} \cdot V_{+}
$$

###
Código de software do projeto disponível no arquivo .py dentro do diretório projetoReduzido
