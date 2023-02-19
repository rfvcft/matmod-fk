import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Car:
    def __init__(self, v_max : int, reaction_time : int, acceleration : int , position : int) -> None:
        self.v_max  = v_max
        self.r = reaction_time
        self.a = acceleration
        self.pos = position
        self.v = v_max
        self.pre_car = None

    def __repr__(self) -> str:
        return "Car(v=%i, r=%i, a=%i, pos=%i, v_max=%i)" % (self.v, self.r, self.a, self.pos, self.v_max)

    def d_max(self) -> int:
        return int(self.v**2 / (2*self.a) + self.r * self.v)

class MemCell:
    def __init__(self, v : int, pos : int) -> None:
        self.v = v
        self.pos = pos

    def __repr__(self) -> str:
        return "MemCell(v=%i, pos=%i)" % (self.v, self.pos)

Memory = list[list[MemCell]]

N = 50
V_MAX = 400
D_TOT = 31415
REACTION_TIME = 1
ACCELERATION = 30
dt = 1

def setup_cars() -> tuple[list[Car], Memory]:
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

def update_mem(mem : Memory, new_mem_row : list[MemCell]) -> Memory:
    mem.pop()
    mem.insert(0, new_mem_row)
    return mem

def move(car : Car, pre_mem : MemCell, dt : int) -> None:
    if -1000 < (pre_mem.pos - car.pos) < 0:
        print("CRASH!!!")
        print(car.d_max())
    if car.d_max() > ((pre_mem.pos - car.pos) % D_TOT) and car.v < car.v_max: # if car in front is far enough away, and we aren't speeding -> accelerate
        car.v += car.a * dt
    elif car.v > pre_mem.v or car.v >= car.v_max: # if we are close and we are faster than car in front, or we are moving over our max speed -> slow down
        car.v -= car.a * dt
    else: # if we are moving slower than the car in front -> accelerate
        car.v += car.a * dt
    car.pos = (car.pos + car.v * dt) % D_TOT

def update(cars : list[Car], memory : Memory) -> None:
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % N], dt)
    memory = update_mem(memory, new_mem)

def draw(cars : list[Car], memory : Memory) -> None:
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

def main() -> None:
    cars, memory = setup_cars()
    draw(cars, memory)

main()
