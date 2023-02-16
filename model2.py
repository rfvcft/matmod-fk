import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Car:
    def __init__(self, v_max, reaction_time, acceleration, position) -> None:
        self.v_max : int = v_max
        self.r : int = reaction_time
        self.a : int = acceleration
        self.pos : int = position
        self.v : int = v_max
        self.pre_car : Car = None

    def __repr__(self) -> str:
        return "Car(v=%i, r=%i, a=%i, pos=%i, v_max=%i)" % (self.v, self.r, self.a, self.pos, self.v_max)

class MemCell:
    def __init__(self, v, pos) -> None:
        self.v = v
        self.pos = pos

    def __repr__(self) -> str:
        return "MemCell(v=%i, pos=%i)" % (self.v, self.pos)

N = 50
V_MAX = 400
D_TOT = 31415
REACTION_TIME = 1
ACCELERATION = 30
dt = 1

def setup_cars():
    cars = [Car(V_MAX, REACTION_TIME, ACCELERATION, int(i/N*D_TOT)) for i in range(N)]
    memory = []

    for i in range(REACTION_TIME):
        time_instance = []
        for car in cars:
            time_instance.append(MemCell(car.v, car.pos))
        memory.append(time_instance)

    cars[0].v = 0
    cars[1].v = 0
    cars[2].v = 0
    return cars, memory

def move(car, pre_speed, dt):
    if car.v > pre_speed:
        car.v -= car.a * dt
    elif car.v >= car.v_max:
        car.v = car.v_max
    else:
        car.v += car.a * dt
    car.pos = (car.pos + car.v * dt) % D_TOT

def update_mem(mem, speeds):
    mem.pop()
    mem.insert(0, speeds)
    return mem

def update(cars, memory):
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % N].v, dt)
    memory = update_mem(memory, new_mem)

def draw(cars, memory):
    fig = plt.figure()
    axis = plt.axes(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
    axis.set_aspect('equal')
    line, = axis.plot([], [], "rs")

    def init():
        thetas = [2*np.pi * car.pos/D_TOT for car in cars]
        line.set_data(np.cos(thetas), np.sin(thetas))
        circle_road = plt.Circle((0, 0), 1 , fill = False)
        axis.add_artist(circle_road)
        return line,

    def animate(frame):
        update(cars, memory)
        thetas = [2*np.pi * memcell.pos/D_TOT for memcell in memory[0]]
        line.set_data(np.cos(thetas), np.sin(thetas))
        return line,

    anim = FuncAnimation(fig, animate, init_func=init, interval=40, blit=True)
    plt.show()

def main():
    cars, memory = setup_cars()
    draw(cars, memory)

main()
