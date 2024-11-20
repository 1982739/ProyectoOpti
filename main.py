#importar bibliotecas
from gurobipy import GRB, Model, quicksum
from datos import cargar_parametros
model = Model()

# Cargar parámetros
P, Z, Q, T, B, B_pq, γ, γ_zq, d_zp, v_p, C_z, f_qj, Φ_q, K, h_z, T_max = cargar_parametros()

### Variables ###

alpha = model.addVars(P, Z, T, vtype = GRB.BINARY, name = "alpha") #Indica si la persona p comienza a evacuar hacia la zona segura z en el instante de tiempo t.

X = model.addVars(Z, T, vtype = GRB.INTEGER, name = "X", lb=0) #Cantidad de personas en la zona segura z en el tiempo t.

w = model.addVars(P, Q, T, vtype = GRB.BINARY, name = "w") #Indica si la persona p se encuentra  en un cuadrante q en el tiempo t.

theta = model.addVars(P, Q, Q, T, vtype = GRB.BINARY, name = "theta") #Indica si la persona p decide viajar a un cuadrante j desde un cuadrante q en el tiempo t.

### FO ###

objetivo = quicksum(X[z, T_max] for z in Z)

model.setObjective(objetivo, GRB.MAXIMIZE)


#### Restricciones ####


model.addConstrs((quicksum(alpha[p, z, t] for z in Z for t in T) <= 1 for p in P), name="r_2") #Restricción de evacuación única

model.addConstrs(
    (alpha[p, z, t] <= (w[p, q, t] + γ_zq[z, q]) / 2 for p in P for q in Q for t in T for z in Z),
    name="r_3"
)
#Restricción a cambio de cuadrante.

model.addConstrs((quicksum(theta[p, q, j, t] for t in T) <= 1 - B_pq[p, q] for p in P for q in Q for j in Q for t in T), name="r_4") #Condición inicial de cambio de cuadrante.

## Condición inicial de cuadrante.

model.addConstrs((w[p, q, 1] == B_pq[p, q] - quicksum(theta[p, q, j, 1] for j in Q if j != q) for p in P for q in Q), name="r_5") #Condición inicial de cuadrante.

##Cuadrante único.

model.addConstrs((quicksum(w[p, q, t] for q in Q) == 1 for p in P for t in T), name="r_6") #Restricción de cuadrante único.

#Posicionamiento de cuadrante.

model.addConstrs((
    w[p, q, t] == w[p, q, t-1] - quicksum(theta[p, q, j, t] for j in Q if j != q)
    for p in P for q in Q for t in range(2, len(T))
), name="r_7")


model.addConstrs((
    w[p, q, t] == w[p, q, t-1] 
                 - quicksum(theta[p, q, j, t] for j in Q if j != q) 
                 + quicksum(
                     theta[p, j, q, t-int(f_qj[j][q])] 
                     for j in Q if j != q and t-int(f_qj[j][q]) >= 1
                 )
    for p in P for q in Q for t in range(2, len(T))
), name="r_8")

#Flujo de cuadrantes.

model.addConstrs((w[p, q, t] >= quicksum(theta[p, q, j, t] for j in Q if j != q)
                  for p in P for q in Q for t in T), name="r_9") # Restricción de flujo de cuadrantes.

#Restricción de cantidad mínima de personas a evacuar.

model.addConstr(quicksum(X[z, T_max]for z in Z) >= K, name="r_10") #Cantidad mínima a evacuar

#Restricción de zonas afectadas por tsunami

model.addConstrs((quicksum(alpha[p, z, t] *γ_zq[z][q] for p in P) <= 1 - (Φ_q[q] + h_z[z] * Φ_q[q])*γ_zq[z][q]
                    for z in Z for t in T for q in Q), name="r_11")


for q in Q:
    for t in T:
        model.addConstr(
            quicksum(w[p, q, t] for p in P) <= 
            quicksum(C_z * γ_zq[z, q] for z in Z) + 
            quicksum(theta[p, q, j, t] for p in P for j in Q if j != q),
            name="r_12"
        )
 #Restricción de flujo de cuadrantes.

#Restricción de inventario de personas de la zona segura.

model.addConstrs((X[z, 1] == 0 for z in Z), name="r_13") #Condición inicial de inventario de las zonas.
model.addConstrs((
    X[z, t] == X[z, t-1] 
               + quicksum(
                   alpha[p, z, t - (d_zp[z][p] // v_p[p]) - int(1.3 * h_z[z])] 
                   for p in P 
                   if t - (d_zp[z][p] // v_p[p]) - int(1.3 * h_z[z]) >= min(T)
               )
    for z in Z for t in T if t > min(T)
), name="restriccion_13") #Inventario de las zonas seguras.

#Restricción de capacidad de las zonas seguras.

model.addConstrs(
    (X[z, t] <= C_z for z in Z for t in T),
    name="r_14"
)
 #Capacidad de zonas seguras.

model.optimize()

print("Objetivo:", model.ObjVal)

