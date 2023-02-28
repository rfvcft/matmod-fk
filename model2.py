import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from functools import partial

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

N = 50
V_MAX = 400
D_TOT = 30000
REACTION_TIME = 4
ACCELERATION = 50
RETARDATION = -70
DT = 0.1

def setup_cars() -> tuple[list[Car], Memory]:
    cars = [Car(i, V_MAX, REACTION_TIME, ACCELERATION, RETARDATION, int(i/N*D_TOT)) for i in range(N)]
    memory = []

    for i in range(REACTION_TIME):
        time_instance = []
        for car in cars:
            time_instance.append(MemCell(car.v, car.pos))
        memory.append(time_instance)

    cars[17].v /= 2
    # print(cars[1].pos - cars[0].pos)
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
    # if (car.d_max() < dist and car.v < car.v_max) or car.v < pre_mem.v: # if car in front is far enough away, and we aren't speeding -> accelerate
    if car.v < pre_mem.v:
        # if car.id == N-1:
        #     print("d_max:", car.d_max())
        car.v += car.a * dt
    elif car.v > pre_mem.v: # if we are close and we are faster than car in front, or we are moving over our max speed -> slow down
        delta_v = car.v - pre_mem.v
        ret = min(int(delta_v**2/(2*(dist - delta_v * car.r))), car.ret)
        # ret = car.ret
        # if car.id == N-1:
        #     print("retardate!")
        #     print("car.v:", car.v, "pre_mem.v:", pre_mem.v, "dist:", dist, "delta_v:", delta_v, "car.r:", car.r)
        #     print("ret: ", ret)
        #     # print(car)
        car.v = max(car.v + ret * dt, 0)
    # elif car.v < pre_mem.v: # if we are moving slower than the car in front -> accelerate
    #     if car.id == N-1:
    #         print("accelerate!")
    #     car.v += car.a * dt
    # else:
    #     if car.id == N-1:
    #         print("do nothing!")
    #         print("speed diff: ", car.v - pre_mem.v)
    # else:
    #     print(car.v - pre_mem.v)
    car.pos = (car.pos + car.v * dt) % D_TOT

def update(cars : list[Car], memory : Memory) -> None:
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % N], cars[(i + 1) % N], DT)
    # print("NEW TIME STEP")
    memory = update_mem(memory, new_mem)

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
        line.set_data(np.cos(thetas), np.sin(thetas))
        return line,

    def make_figure(title, y_max):
        fig = plt.figure()
        axis = plt.axes(xlim=(0, N), ylim=(0, y_max))
        axis.set_title(title)
        line, = axis.plot([], [])
        return fig, axis, line

    def animate_speeds(frame, line):
        line.set_data(range(len(cars)), [(car.v + memcell.v)/2 for car, memcell in list(zip(cars, memory[0]))])
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

main()
