import numpy as np
import pandas as pd
## Hiperparametros
def cargar_parametros():
    T_max = 20


    # Conjuntos
    P = np.arange(0, 10)
    Z = np.arange(0, 3)
    Q = np.arange(0,3)
    T = np.arange(1,T_max+1)

    # Parametros

    B = np.random.randint(1, len(Q), len(P)) # A qué cuadrante pertenece cada persona, es aleatorio.
    B_pq = np.zeros((len(P), len(Q))) # Persona p en cuadrante q
    for i in range(len(P)):
        for j in range(len(Q)):
            if B[i] == Q[j]:
                B_pq[i][j] = 1

    γ = np.zeros(len(Z), dtype=int) # Inicializar γ con ceros
    num_zonas_seguras = 3
    γ_zq = np.zeros((len(Z), len(Q))) # Zona z en cuadrante q

    for q in range(len(Q)): # Asignar zonas seguras
        zonas_seguras = np.random.choice(len(Z), num_zonas_seguras, replace=False)
        for z in zonas_seguras:
            γ[z] = q
            γ_zq[z][q] = 1

    # Asignar las zonas restantes de manera aleatoria
    zonas_restantes = [z for z in range(len(Z)) if γ[z] == 0]
    for z in zonas_restantes:
        q = np.random.randint(1, len(Q))  # Verifica que q esté dentro del rango de Q
        if q >= len(Q):
            print(f"Índice q fuera de rango: {q}")
        γ[z] = q
        γ_zq[z][q] = 1

    d_zp = np.random.uniform(20, 106, (len(Z), len(P))) # Distancia persona p a zona z

    v_p = np.random.uniform(0.95, 1.25, len(P)) # Velocidad de persona p

    C_z = np.round(100 / 0.93 * 4, 0) # 100 m2 por piso, 4 pisos, 1 persona usa 0.93 m2. Se supone que todas las vías de evacuación serán verticales. 

    f_qj = np.genfromtxt('datos.csv', delimiter=',', dtype=float) # Tiempo de viaje entre cuadrantes q y j


    K = len(P)*0.1 #personas minimas a evacuar


    h_z = np.zeros(len(Z), dtype=int)
    num_zonas_verticales = int(0.9 * num_zonas_seguras) # 90% de las zonas seguras tendrán vías de evacuación verticales
    zonas_verticales = np.random.choice(num_zonas_seguras, num_zonas_verticales, replace=False)
    for z in zonas_verticales:
        h_z[z] = 1

    Φ_q = np.zeros(len(Q), dtype=int)
    Φ_q[0] = 1 ## Cuadrantes costeros
    print("Datos cargados")
    
    return P, Z, Q, T, B, B_pq, γ, γ_zq, d_zp, v_p, C_z, f_qj, Φ_q, K, h_z, T_max
