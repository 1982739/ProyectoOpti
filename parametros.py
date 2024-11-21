import pandas as pd
import numpy as np

def cargar_parametros2():
    P = 10000
    p = np.arange(1, P+1)
    T = int(14/(7/9))
    t = np.arange(1, T+1)
    Q = 31
    q = np.arange(1, Q+1)
    Z = 40
    z = np.arange(1, Z+1)
    zq = [
        [1, 2],
        [3.0],
        [4.0],
        [5.0],
        [6.0, 7.0],
        [8.0, 9.0],
        [10.0],
        [11.0, 12.0, 13.0, 14.0],
        [15.0],
        [16.0],
        [17.0, 18.0],
        [19.0, 20.0],
        [],
        [],
        [],
        [21.0],
        [22.0],
        [23.0],
        [24.0, 25.0],
        [],
        [],
        [26.0],
        [],
        [27.0, 28.0, 29.0],
        [30.0],
        [31.0, 32.0],
        [33.0, 34.0],
        [35.0, 36.0],
        [37.0],
        [38.0, 39.0, 40.0]
    ]

    B = np.random.randint(0, Q, P) # A qué cuadrante pertenece cada persona, es aleatorio.
    B_pq = np.zeros((P, Q)) # Persona p en cuadrante q
    for i in range(P):
        for j in range(Q):
            if B[i] == q[j]:
                B_pq[i][j] = 1

    γ_zq = np.zeros((Z, Q-1))
    for i in range(Z):
        for j in range(Q-1):
            if len(zq[j]) > 0: 
                for k in range(len(zq[j])):
                    if zq[j][k] == z[i]:
                        γ_zq[i][j] = 1

    f_qj = np.genfromtxt('datos.csv', delimiter=',', dtype=float) # Distancia entre cuadrantes

    d_pz = np.random.uniform(20, 106, (Z, P))

    vp = np.random.uniform(0.95, 1.25, P)

    C_z = np.round(100 / 0.93 * 4, 0)

    K = 0.1 * P

    h_z = np.ones(Z)

    Φ_q = np.ones(Q)
    for i in range(Q):
        Φ_q[i] = round(np.random.random(),0)

    return p, z, q, t, T, B, B_pq, γ_zq, d_pz, vp, C_z, f_qj, Φ_q, K, h_z






