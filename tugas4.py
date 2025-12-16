import numpy as np

# 1. Fungsi keanggotaan bell-shaped sesuai file
def gbell_mf(x, a, b, c):
    return 1 / (1+abs((x - c) / a) ** (2 * b))

#2. Aturan Sugeno
def f1(x, y):
    return 0.1 * x + 0.1 * y + 0.1

def f2(x, y):
    return 10 * x + 10 * y + 10

#3. Hitung ANFIS untuk input(x, y   
def anfis(x, y):
    
    # Hitung derajat keanggotaan
    A1 = 0.5
    B1 = 0.1
    A2 = 0.25
    B2 = 0.039

    w1 = A1 * B1
    w2 = A2 * B2

    w_sum = w1 + w2
    W1 = w1 / w_sum
    W2 = w2 / w_sum

    out1 = W1 * f1(x, y)
    out2 = W2 * f2(x, y)

    output = out1 + out2

    return {
        "A1": A1, "B1": B1,
        "A2": A2, "B2": B2,
        "w1": w1, "w2": w2,
        "W1": W1, "W2": W2,
        "out1": out1, "out2": out2,
        "final_output": output
    }
# Contoh penggunaan
result = anfis(3, 4)
for k, v in result.items():
    print(f"{k:12s} = {v}")