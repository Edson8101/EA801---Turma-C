import math
import struct

# Carrega os biases (vetor de 10 floats)
def carregar_biases():
    with open("biases.txt") as f:
        return [float(x) for x in f.read().strip().split(",")]

# Carrega os 10 pesos correspondentes a uma entrada (pixel) i
def carregar_linha_pesos(i):
    with open("weights.bin", "rb") as f:
        f.seek(i * 10 * 4)  # 10 floats * 4 bytes cada
        data = f.read(10 * 4)
        return list(struct.unpack("10f", data))

# Softmax para converter logits em probabilidades
def softmax(x):
    e = [math.exp(i) for i in x]
    s = sum(e)
    return [i / s for i in e]

# Inferência completa: imagem → índice do número previsto
def prever_numero(imagem):
    biases = carregar_biases()
    logits = []
    for j in range(10):
        soma = 0.0
        for i in range(784):
            pesos = carregar_linha_pesos(i)
            soma += imagem[i] * pesos[j]
        soma += biases[j]
        logits.append(soma)
    probs = softmax(logits)
    return probs.index(max(probs))

