#importar bibliotecas
from gurobipy import GRB, Model, quicksum
from datos import cargar_parametros

from collections import defaultdict # Hay q justificar que utilizamos estoo!!

model = Model()

### Cargar parámetros ###
P, Z, Q, T, B, B_pq, γ, γ_zq, d_zp, v_p, C_z, f_qj, Φ_q, K, h_z, T_max = cargar_parametros()

### variables ###

#alpha_pzt
alpha = model.addVars(P, Z, T, vtype = GRB.BINARY, name = "alpha") #Indica si la persona p comienza a evacuar hacia la zona segura z en el instante de tiempo t.
#X_zt
x = model.addVars(Z, T, vtype = GRB.INTEGER, name = "X", lb=0) #Cantidad de personas en la zona segura z en el tiempo t.
#w_pqt
w = model.addVars(P, Q, T, vtype = GRB.BINARY, name = "w") #Indica si la persona p se encuentra  en un cuadrante q en el tiempo t.
#theta_pqjt
theta = model.addVars(P, Q, Q, T, vtype = GRB.BINARY, name = "theta") #Indica si la persona p decide viajar a un cuadrante j desde un cuadrante q en el tiempo t.

model.update()

### FO ###

objetivo = quicksum(x[z,T_max] for z in Z )

model.setObjective(objetivo, GRB.MAXIMIZE)

model.update()

#### Restricciones ####

#R2 / Restricción de evacuación única
model.addConstrs((quicksum(alpha[p, z, t] for z in Z for t in T) <= 1
                  for p in P),
                 name="r_2")


#R4 / Restriccion de cambio de cuadrante
model.addConstrs((quicksum(theta[p, q, j, t] for t in T) <= 1 - B_pq[p, j]
                  for p in P for q in Q for j in Q for t in T),
                 name="r_4")

#R5 / Condicion inicial de cuadrante
model.addConstrs((w[p, q, 1] == B_pq[p, q]
                  for p in P for q in Q),
                 name="r_5")

#R6 / Restriccion de cuadrante unico
model.addConstrs((quicksum(w[p,q,t] for q in Q) == 1
                  for p in P for t in T),
                 name="r_6")

#R7 / Posicionamiento de cuadrante 
model.addConstrs((w[p, q, t] == w[p, q, t-1] - quicksum(theta[p, q, j, t] for j in Q if j != q)
                  + quicksum(theta[p, j, q, t-int(f_qj[j][q]//(v_p[p]*60))] for j in Q if j != q and max(T) >= t-int(f_qj[j][q]//(v_p[p]*60)) >= 2)
                  for p in P for q in Q for t in range(2, max(T))),
                 name="r_7")

#R8 / Flujo de cuadrantes
model.addConstrs((w[p,q,t] >= quicksum(theta[p,q,j,t] for j in Q if j != q)
                  for p in P for q in Q for t in T),
                 name="r_8")

#R9 / Cantidad minima a evacuar
model.addConstr((quicksum(x[z,T_max]for z in Z) >= K),
                 name="r_9")

#R10 / Restriccion de zonas afectadas por tsunami **
model.addConstrs((alpha[p, z, t] <= 1+ (h_z[z]-1)*γ_zq[z,q]*Φ_q[q]
                  for z in Z for t in T for q in Q for p in P),
                 name="r_10")

#R11 / Restriccion de activacion de theta_pqjt
model.addConstrs((w[p,q,t] + quicksum(x[z,t]*γ_zq[z,q] for z in Z) <= quicksum(C_z*γ_zq[z,q] for z in Z)
                  + quicksum(theta[p,q,j,t] for j in Q if j != q)
                  for q in Q for p in P for t in T),
                 name="r_11")

#R12 / Restriccion de inventario de personas de la zona segura
model.addConstrs((x[z,t] == x[z,t-1]
                  + quicksum(alpha[p, z, t - d_zp[z, p] // (v_p[p]*60) - int(1.3 * h_z[z])]for p in P if 2 <= t - d_zp[z, p] // (v_p[p]*60) - int(1.3 * h_z[z]) <= max(T))
                  for z in Z for t in T if t > min(T)),
                 name="r_12")

#R13 / Condicion inicial de inventario de la zona segura
model.addConstrs((x[z,1] == 0
                  for z in Z),
                 name="r_13")

#R14 / capacidad de la zona segura
model.addConstrs((x[z,t] <= C_z
                  for z in Z for t in T),
                 name="r_14")

model.setParam(GRB.Param.TimeLimit, 30)

model.optimize()

try:
    print("Objetivo:", model.ObjVal)
    porcentaje_phi_q = (sum(Φ_q) / len(Φ_q)) * 100
    print(f'Cantidad de cuadrantes (Q): {len(Q)}')
    print(f'Cantidad de zonas por cuadrante: {len(Z)//len(Q)}')
    print(f'Cantidad de puntos (P): {len(P)}')
    print(f'Cantidad de capacidades de zona (C_z): {C_z}')
    print(f'Porcentaje de cuadrantes inundados: {porcentaje_phi_q:.2f}%')
    print(f'Valor de T_max: {T_max}')
    restricciones_activas = defaultdict(list)

    for constr in model.getConstrs():
        if constr.slack == 0: 
            nombre_base = constr.ConstrName.split('[')[0]
            restricciones_activas[nombre_base].append(constr.ConstrName)

    for nombre_base, activas in restricciones_activas.items():
        print(f"{nombre_base} tiene {len(activas)} restricciones activas.")

    model.write("modelo_guardado.lp")
except:
    model.computeIIS()
    model.write("infeasible_model.ilp") 

