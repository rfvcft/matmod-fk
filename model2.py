import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Car:
    def __init__(self, id : int, v_max : int, reaction_time : int, acceleration : int, retardation : int, position : int) -> None:
        self.id = id
        self.v_max  = v_max
        self.r = reaction_time
        self.a = acceleration
        self.ret = retardation
        self.pos = position
        self.v = int(v_max * 0.9)
        self.pre_car = None

    def __repr__(self) -> str:
        return "Car(id=%i, v=%i, r=%i, a=%i, ret=%i, pos=%i, v_max=%i)" % (self.id, self.v, self.r, self.a, self.ret, self.pos, self.v_max)

    def d_max(self) -> int:
        return int(-self.v**2 / (2*self.ret) + self.r * self.v)

class MemCell:
    def __init__(self, v : int, pos : int) -> None:
        self.v = v
        self.pos = pos

    def __repr__(self) -> str:
        return "MemCell(v=%i, pos=%i)" % (self.v, self.pos)

Memory = list[list[MemCell]]

N = 40
V_MAX = 500
D_TOT = 500 * 2 * N
REACTION_TIME = 10
ACCELERATION = 100
RETARDATION = -300
DT = 1

def setup_cars() -> tuple[list[Car], Memory]:
    cars = [Car(i, V_MAX, REACTION_TIME, ACCELERATION, RETARDATION, int(i/N*D_TOT)) for i in range(N)]
    memory = []

    for i in range(REACTION_TIME):
        time_instance = []
        for car in cars:
            time_instance.append(MemCell(car.v, car.pos))
        memory.append(time_instance)

    cars[0].v = 0
    cars[1].v = 0
    cars[2].v = 0
    print(cars[1].pos - cars[0].pos)
    return cars, memory

def update_mem(mem : Memory, new_mem_row : list[MemCell]) -> Memory:
    mem.pop()
    mem.insert(0, new_mem_row)
    return mem

def move(car : Car, pre_mem : MemCell, pre_car : Car, dt : int) -> None:
    # print(car.v)
    if -10000 < (pre_car.pos - car.pos) < 0:
        print("CRASH!!!")
        print(car, pre_car)
    if car.v > car.v_max:
        car.v = car.v_max
    dist = (pre_car.pos - car.pos) % D_TOT
    if car.d_max() < dist and car.v < car.v_max: # if car in front is far enough away, and we aren't speeding -> accelerate
        if car.id == N-1:
            print("d_max:", car.d_max())
        car.v += car.a * dt
    elif car.v > pre_mem.v: # if we are close and we are faster than car in front, or we are moving over our max speed -> slow down
        delta_v = car.v - pre_mem.v
        ret = max(int(-1.1*(delta_v)**2/(2*(dist))), car.ret)
        if car.id == N-1:
            print("retardate!")
            print("car.v:", car.v, "pre_mem.v:", pre_mem.v, "dist:", dist, "delta_v:", delta_v, "car.r:", car.r)
            print("ret: ", ret)
            # print(car)
        car.v = max(car.v + ret * dt, 0)
    elif car.v < pre_mem.v: # if we are moving slower than the car in front -> accelerate
        if car.id == N-1:
            print("accelerate!")
        car.v += car.a * dt
    # else:
    #     if car.id == N-1:
    #         print("do nothing!")
    #         print("speed diff: ", car.v - pre_mem.v)
    # else:
    #     print(car.v - pre_mem.v)
    #     print("WOW WHAT A BIG DUM-DUM YOU ARE! (if it doesn't say 0 above)")
    car.pos = (car.pos + car.v * dt) % D_TOT

def update(cars : list[Car], memory : Memory) -> None:
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % N], cars[(i + 1) % N], DT)
    # print("NEW TIME STEP")
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
    print([car.v for car in cars])

def main() -> None:
    cars, memory = setup_cars()
    draw(cars, memory)

main()
