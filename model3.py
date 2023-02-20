import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from functools import partial

class Car:
    def __init__(self, id : int, v_max : int, reaction_time : int, acceleration : int, retardation : int, position : int, v : int) -> None:
        self.id = id
        self.v_max  = v_max
        self.r = reaction_time
        self.a = acceleration
        self.ret = retardation
        self.pos = position
        self.v = v
        self.pre_car = None

    def __repr__(self) -> str:
        return "Car(id=%i, v=%i, r=%i, a=%i, ret=%i, pos=%i, v_max=%i)" % (self.id, self.v, self.r, self.a, self.ret, self.pos, self.v_max)

class MemCell:
    def __init__(self, v : int, pos : int) -> None:
        self.v = v
        self.pos = pos

    def __repr__(self) -> str:
        return "MemCell(v=%i, pos=%i)" % (self.v, self.pos)

Memory = list[list[MemCell]]

N = 50
K = 1
V_MAX = 400 * K
D_TOT = 31415 * K
REACTION_TIME = 5 * K
ACCELERATION = 30 * K
RETARDATION = -30 * K
DT = 1

def dev(avg : int, key : str) -> int:
    match key:
        case "v":
            return round(avg + np.random.gamma(10, 0.4) - 5)
        case "r":
            return np.random.randint(avg, avg + 2)
        case "a":
            return np.random.randint(avg - 3, avg + 3)
        case "ret":
            return np.random.randint(avg - 3, avg + 3)


def setup_cars() -> tuple[list[Car], Memory]:
    cars = [Car(i, dev(V_MAX, "v"), dev(REACTION_TIME, "r"), dev(ACCELERATION, "a"), dev(RETARDATION, "ret"), int(i/N*D_TOT), int(0.8 * V_MAX)) for i in range(N)]
    # cars = [Car(i, V_MAX, REACTION_TIME, ACCELERATION, RETARDATION, int(i/N*D_TOT), int(0.8 * V_MAX)) for i in range(N)]
    r_max = max(cars, key=lambda c: c.r).r
    memory = []

    for i in range(r_max):
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

def move(car : Car, pre_mem : MemCell, pre_car : Car, dt : int) -> None:
    # if -10000 < (pre_car.pos - car.pos) < 0:
    #     print("CRASH!!!")
    #     print(car, pre_car)
    if car.v > pre_mem.v:
        car.v -= car.a * dt
    elif car.v >= car.v_max:
        car.v = car.v_max
    else:
        car.v += car.a * dt
    car.pos = (car.pos + car.v * dt) % D_TOT

def update(cars : list[Car], memory : Memory) -> None:
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % N], cars[(i + 1) % N], DT)
    update_mem(memory, new_mem)

def draw(cars : list[Car], memory : Memory) -> None:

    def make_car_figure():
        fig = plt.figure()
        axis = plt.axes(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
        axis.set_aspect('equal')
        line, = axis.plot([], [], "rs")
        return fig, axis, line

    def init_cars(axis, line):
        thetas = [2*np.pi * car.pos/D_TOT for car in cars]
        line.set_data(np.cos(thetas), np.sin(thetas))
        circle_road = plt.Circle((0, 0), 1 , fill = False)
        axis.add_artist(circle_road)
        return line,

    def animate_cars(frame, line):
        update(cars, memory)
        # thetas = [2*np.pi * memcell.pos/D_TOT for memcell in memory[0]]
        thetas = [2*np.pi * car.pos/D_TOT for car in cars]
        line.set_data(np.cos(thetas), np.sin(thetas))
        return line,

    def make_figure(title, y_max):
        fig = plt.figure()
        axis = plt.axes(xlim=(0, N), ylim=(0, y_max))
        axis.set_title(title)
        line, = axis.plot([], [])
        return fig, axis, line

    def animate_pos(frame, line):
        diffs = np.diff([car.pos for car in cars])
        line.set_data(range(len(cars) - 1), diffs)
        return line,

    def animate_speeds(frame, line):
        # print(list(zip(cars, memory[0])))
        line.set_data(range(len(cars)), [(car.v + memcell.v)/2 for car, memcell in list(zip(cars, memory[0]))])
        # line.set_data(range(len(cars)), [car.v for car in cars])
        return line,

    car_fig, car_ax, car_line = make_car_figure()
    # pos_fig, pos_ax, pos_line = make_figure("Difference in positions", 2000)
    v_fig, v_ax, v_line = make_figure("Speeds", V_MAX + 20)
    car_anim = FuncAnimation(car_fig, partial(animate_cars, line=car_line), init_func=partial(init_cars, axis=car_ax, line=car_line), interval=40, blit=True)
    # pos_anim = FuncAnimation(pos_fig, partial(animate_pos, line=pos_line), interval=40, blit=True)
    v_anim = FuncAnimation(v_fig, partial(animate_speeds, line=v_line), interval=40, blit=True)
    plt.show()
    print([car.v for car in cars])

def main() -> None:
    cars, memory = setup_cars()
    draw(cars, memory)

main()
