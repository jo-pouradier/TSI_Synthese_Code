import math
from matplotlib import pyplot as plt


# -----Quel tableau choisir temps ou force: ----------------------
case = "force"
jump_force = 1000  # precision (en kg.m.s-2)
jump_force_offset = 0

dt = 0.017  # (en s) soit 6fps (calcul trop long pour 60fps)
masse = 60  # (en Kg)
gravity_obj = -9.81  # (en m.s-2)
acceleration = 0  # (en Kg.m-2)
vitesse = 0.0  # (en m.s-1)
position = 0.0  # (en m)
# ----------------------------------------------------------------

if case == "force":
    count = 30
    max = [0 for i in range(count)]
    for i in range(count):
        acceleration = ((i * jump_force) + jump_force_offset) / masse + gravity_obj
        vitesse += acceleration * dt
        while True:
            position += vitesse * dt
            if max[i] < position:
                max[i] = position
            acceleration = gravity_obj
            vitesse += acceleration * dt
            if position < 0:
                position = 0
                vitesse = 0
                break
    plt.plot([(jump_force*i)+jump_force_offset for i in range(count)], max)
    plt.xlabel("force du saut (en kg.m.s-2)")
    plt.ylabel("hauteur max du saut (en m)")
    plt.title("hauteur d'un saut en fct de la force du saut")
    plt.autoscale = True
    plt.show()


if case == "temps":
    positions = [0]
    # jump_force doit etre modifier en fct du saut voulue (choisi avec le graphe des forces)
    jump_force = 19910
    acceleration = (jump_force + jump_force_offset)/masse + gravity_obj
    vitesse += acceleration * dt
    print(vitesse)
    while True:
        position += vitesse * dt
        acceleration = gravity_obj
        vitesse += acceleration * dt
        positions.append(position)
        if position < 0:
            break
    plt.plot([i*dt for i in range(len(positions))], positions)
    plt.xlabel("temps (en s)")
    plt.ylabel("hauteur max du saut (en m)")
    plt.title("hauteur d'un saut en fct du temps")
    plt.autoscale = True
    plt.show()
