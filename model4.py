# The goal is to create plots for reaction time vs wave size, reaction time vs wave speed etc.
# During this we shouldn't do the regular plots, as to be able to simulate for multiple reaction times etc.

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
V_MAX = 400
D_TOT = 30000
REACTION_TIME = 4
ACCELERATION = 50
RETARDATION = -50
DT = 0.1
WAVE_SPEED = []

def dev(avg : int, key : str) -> int:
    match key:
        case "v":
            return round(avg + np.random.gamma(10, 1) - 5)
        case "r":
            return np.random.randint(1, avg + 1)
        case "a":
            return np.random.randint(avg - 5, avg + 5)
        case "ret":
            return np.random.randint(avg - 5, avg + 5)


def setup_cars() -> tuple[list[Car], Memory]:
    # cars = [Car(i, dev(V_MAX, "v"), dev(REACTION_TIME, "r"), dev(ACCELERATION, "a"), dev(RETARDATION, "ret"), int(i/N*D_TOT), int(0.95 * V_MAX)) for i in range(N)]
    cars = [Car(i, V_MAX, REACTION_TIME, ACCELERATION, RETARDATION, int(i/N*D_TOT), int(1 * V_MAX)) for i in range(N)]
    r_max = max(cars, key=lambda c: c.r).r
    memory = []

    for i in range(r_max):
        time_instance = []
        for car in cars:
            time_instance.append(MemCell(car.v, car.pos))
        memory.append(time_instance)

    cars[17].v /= 2
    # cars[1].v = 0
    # cars[2].v = 0
    return cars, memory

def setup_cars_set_parameters(reaction_time) -> tuple[list[Car], Memory]:
    cars = [Car(i, dev(V_MAX, "v"), dev(reaction_time, "r"), dev(ACCELERATION, "a"), dev(RETARDATION, "ret"), int(i/N*D_TOT), int(0.95 * V_MAX)) for i in range(N)]
    # cars = [Car(i, V_MAX, reaction_time, ACCELERATION, RETARDATION, int(i/N*D_TOT), V_MAX) for i in range(N)]
    r_max = max(cars, key=lambda c: c.r).r
    memory = []

    for i in range(r_max):
        time_instance = []
        for car in cars:
            time_instance.append(MemCell(car.v, car.pos))
        memory.append(time_instance)

    cars[17].v /= 2
    # cars[1].v = 0
    # cars[2].v = 0
    return cars, memory

def update_mem(mem : Memory, new_mem_row : list[MemCell]) -> Memory:
    mem.pop()
    mem.insert(0, new_mem_row)

def move(car : Car, pre_mem : MemCell, dt : int) -> None:
    # if -10000 < (pre_car.pos - car.pos) < 0:
    #     print("CRASH!!!")
    #     print(car, pre_car)
    if car.v > pre_mem.v:
        car.v = max(car.v - car.a * dt, 0)
    elif car.v >= car.v_max:
        car.v = car.v_max
    elif car.v < pre_mem.v:
        car.v += car.a * dt
    car.pos = (car.pos + car.v * dt) % D_TOT

def update(cars : list[Car], memory : Memory) -> None:
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % N], DT)
    update_mem(memory, new_mem)

def simulate(cars : list[Car], memory : Memory, wave_depth: list[int], wave_size: list[int], wave_speed: list[int]):
    # find wave size, wave speed and wave depth for each reaction time and iteration

    # wave size is seen to be the number of cars that are slowed down because of the queue
    # meaning that wave_size = number of cars that consequtively are under the avg speed.
    # Look at the number of cars under 95% of the max speed

    # wave speed is approximated by the "speed" of the lowest speed point. This is the average
    # distance moved by the lowest point.

    # wave depth is the depth of the speed dip, roughly approximated by the difference in speed
    # between the slowest and fastest car.
    min_wave_pos = []
    K = 100
    for k in range(K):
        update(cars, memory)
        min_car = min(cars, key=lambda c: c.v)
        if min_car.pos > D_TOT/2:
            min_wave_pos.append(min_car.pos - D_TOT)
        else:
            min_wave_pos.append(min_car.pos)

    # plt.plot(range(K), min_wave_pos)
    # plt.show()

    max_car = max(cars, key=lambda c: c.v)
    min_car = min(cars, key=lambda c: c.v)
    # wave_depth.append(max_car.v - min_car.v)
    wave_size.append(sum(1 for car in cars if car.v < 0.95 * max_car.v))
    wave_speed.append((min_wave_pos[30] - min_wave_pos[-1]) / ((K-30) * DT))

def reaction_speed_graphs():
    wave_depth = []
    wave_size = []
    wave_speed = []
    max_reaction_speed = 10
    for reaction_speed in range(1, max_reaction_speed):
        print("reaction_speed:", reaction_speed)
        cars, memory = setup_cars_set_parameters(reaction_speed)
        simulate(cars, memory, wave_depth, wave_size, wave_speed)
    plt.figure(1)
    plt.plot(range(1, max_reaction_speed), wave_size)
    plt.title("wave size")
    plt.xlabel("reaction time")
    plt.ylabel("number of cars in wave")

    # plt.figure(2)
    # plt.plot(range(1, max_reaction_speed), wave_depth)
    # plt.title("wave depth")
    # plt.xlabel("reaction time")
    # plt.ylabel("difference in speed in shock wave")

    plt.figure(3)
    plt.plot(range(1, max_reaction_speed), wave_speed)
    plt.title("wave speed")
    plt.xlabel("reaction time")
    plt.ylabel("wave speed of shock wave")

    plt.show()


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
        min_v_car = min(cars, key=lambda c: c.v)
        prev_min_v_mem = min(memory[0], key=lambda m: m.v)
        wave_v_approx = ((min_v_car.pos - prev_min_v_mem.pos) % D_TOT) / DT
        WAVE_SPEED.append(wave_v_approx)
        # print(sum(WAVE_SPEED)/len(WAVE_SPEED))
        line.set_data(np.cos(thetas), np.sin(thetas))
        return line,

    def make_figure(title, y_max):
        fig = plt.figure()
        axis = plt.axes(xlim=(0, N), ylim=(0, y_max))
        axis.set_title(title)
        line, = axis.plot([], [])
        return fig, axis, line

    def make_wave_figure(title, y_max):
        fig = plt.figure()
        axis = plt.axes(ylim=(0, y_max))
        axis.set_title(title)
        line, = axis.plot([], [])
        return fig, axis, line

    def animate_pos(frame, line):
        diffs = np.append(np.diff([car.pos for car in cars]), cars[0].pos - cars[N-1].pos)
        mod_diffs = [max(d, 0) % D_TOT for d in diffs]
        print(mod_diffs)
        line.set_data(range(len(cars)), mod_diffs)
        return line,

    def animate_speeds(frame, line):
        line.set_data(range(len(cars)), [(car.v + memcell.v)/2 for car, memcell in list(zip(cars, memory[0]))])
        return line,

    def moving_average(a, n=5):
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def animate_wave_speed(frame, line):
        if len(WAVE_SPEED) > N:
            avg_speed = moving_average(WAVE_SPEED[-N:], n=5)
            line.set_data(range(N-4), avg_speed)
        elif len(WAVE_SPEED) > 9:
            avg_speed = moving_average(WAVE_SPEED[-len(WAVE_SPEED):], n=min(len(WAVE_SPEED), 5))
            line.set_data(range((min(N, len(WAVE_SPEED) - 4))), avg_speed)
        else:
            avg_speed = WAVE_SPEED[-min(N, len(WAVE_SPEED)):]
            line.set_data(range((min(N, len(WAVE_SPEED)))), avg_speed)
        return line,

    car_fig, car_ax, car_line = make_car_figure()
    # pos_fig, pos_ax, pos_line = make_figure("Difference in positions", D_TOT)
    v_fig, v_ax, v_line = make_figure("Speeds", V_MAX + 20)
    # wave_fig, wave_ax, wave_line = make_figure("Wave speed", V_MAX + 200)
    car_anim = FuncAnimation(car_fig, partial(animate_cars, line=car_line), init_func=partial(init_cars, axis=car_ax, line=car_line), interval=40, blit=True)
    # pos_anim = FuncAnimation(pos_fig, partial(animate_pos, line=pos_line), interval=40, blit=True)
    v_anim = FuncAnimation(v_fig, partial(animate_speeds, line=v_line), interval=20, blit=True)
    # wave_v_anim = FuncAnimation(wave_fig, partial(animate_wave_speed, line=wave_line), interval=20, blit=True)
    plt.show()
    print([car.v for car in cars])

def main() -> None:
    cars, memory = setup_cars()
    draw(cars, memory)

# main()
reaction_speed_graphs()
