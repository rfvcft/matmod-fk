# The goal is to create plots for reaction time vs wave size, reaction time vs wave speed etc.
# During this we shouldn't do the regular plots, as to be able to simulate for multiple reaction times etc.

import matplotlib.pyplot as plt
import numpy as np

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

def setup_cars_set_parameters(v_max=V_MAX, reaction_time=REACTION_TIME, acceleration=ACCELERATION, retardation=RETARDATION, n=N) -> tuple[list[Car], Memory]:
    # cars = [Car(i, dev(v_max, "v"), dev(reaction_time, "r"), dev(acceleration, "a"), dev(retardation, "ret"), int(i/N*D_TOT), int(0.95 * v)) for i in range(n)]
    cars = [Car(i, v_max, reaction_time, acceleration, retardation, int(i/N*D_TOT), v_max) for i in range(n)]
    r_max = max(cars, key=lambda c: c.r).r
    memory = []

    for i in range(r_max):
        time_instance = []
        for car in cars:
            time_instance.append(MemCell(car.v, car.pos))
        memory.append(time_instance)

    cars[7].v /= 2
    return cars, memory

def update_mem(mem : Memory, new_mem_row : list[MemCell]) -> Memory:
    mem.pop()
    mem.insert(0, new_mem_row)

def move(car : Car, pre_mem : MemCell, dt : int) -> None:
    if car.v > pre_mem.v:
        car.v = max(car.v - car.a * dt, 0)
    elif car.v >= car.v_max:
        car.v = car.v_max
    elif car.v < pre_mem.v:
        car.v += car.a * dt
    car.pos = (car.pos + car.v * dt) % D_TOT

def update(cars : list[Car], memory : Memory, n=N) -> None:
    new_mem = []
    for i, car in enumerate(cars):
        new_mem.append(MemCell(car.v, car.pos))
        move(car, memory[car.r - 1][(i + 1) % n], DT)
    update_mem(memory, new_mem)

def simulate(cars : list[Car], memory : Memory, wave_size: list[int], wave_speed: list[int], start_k : int, stop_k : int, num_cars=N):
    # find wave size, wave speed and wave depth for each reaction time and iteration

    # wave size is seen to be the number of cars that are slowed down because of the queue
    # meaning that wave_size = number of cars that consequtively are under the avg speed.
    # Look at the number of cars under 95% of the max speed

    # wave speed is approximated by the "speed" of the lowest speed point. This is the average
    # distance moved by the lowest point.

    # wave depth is the depth of the speed dip, roughly approximated by the difference in speed
    # between the slowest and fastest car.
    min_wave_pos = []
    for k in range(stop_k):
        update(cars, memory, n=num_cars)
        min_car = min(cars, key=lambda c: c.v)
        if min_car.pos > D_TOT/2:
            min_wave_pos.append(min_car.pos - D_TOT)
        else:
            min_wave_pos.append(min_car.pos)
        # min_wave_pos.append(min_car.pos)
    # plt.plot(range(K), min_wave_pos)
    # plt.show()

    max_car = max(cars, key=lambda c: c.v)
    wave_size.append(sum(1 for car in cars if car.v < 0.95 * max_car.v))
    wave_speed.append((min_wave_pos[start_k] - min_wave_pos[stop_k - 1]) / ((stop_k-1 -start_k)))

def reaction_speed_graphs():
    wave_size = []
    wave_speed = []
    max_reaction_speed = 10
    for reaction_speed in range(2, max_reaction_speed):
        print("reaction_speed:", reaction_speed)
        cars, memory = setup_cars_set_parameters(reaction_time=reaction_speed)
        simulate(cars, memory, wave_size, wave_speed, 30, 100)
    plt.figure(1)
    plt.plot(range(2, max_reaction_speed), wave_size)
    plt.title("wave size")
    plt.xlabel("reaction time")
    plt.ylabel("number of cars in wave")

    plt.figure(2)
    plt.plot(range(2, max_reaction_speed), wave_speed)
    plt.title("wave speed")
    plt.xlabel("reaction time")
    plt.ylabel("wave speed of shock wave")

    plt.show()

def num_cars_graphs():
    wave_size = []
    wave_speed = []
    max_num_cars = 101
    for num_cars in range(10, max_num_cars, 10):
        print("num_cars:", num_cars)
        cars, memory = setup_cars_set_parameters(n=num_cars)
        simulate(cars, memory, wave_size, wave_speed, 20, 50, num_cars=num_cars)
    plt.figure(1)
    plt.plot(range(10, max_num_cars, 10), wave_size)
    plt.title("wave size")
    plt.xlabel("number of cars")
    plt.ylabel("number of cars in wave")

    plt.figure(2)
    plt.plot(range(10, max_num_cars, 10), wave_speed)
    plt.title("wave speed")
    plt.xlabel("number of cars")
    plt.ylabel("wave speed of shock wave")

    plt.show()

def acc_retard_graphs():
    wave_size = []
    wave_speed = []
    min_acc = 20
    max_acc = 81
    for acc in range(min_acc, max_acc, 10):
        print("acc:", acc)
        cars, memory = setup_cars_set_parameters(acceleration=acc, retardation=-acc)
        simulate(cars, memory, wave_size, wave_speed, 60, 100)
    plt.figure(1)
    plt.plot(range(min_acc, max_acc, 10), wave_size)
    plt.title("wave size")
    plt.xlabel("acceleration/retardation")
    plt.ylabel("number of cars in wave")

    plt.figure(2)
    plt.plot(range(min_acc, max_acc, 10), wave_speed)
    plt.title("wave speed")
    plt.xlabel("acceleration/retardation")
    plt.ylabel("wave speed of shock wave")

    plt.show()

def max_speed_graphs():
    wave_size = []
    wave_speed = []
    min_max_speed = 200
    max_max_speed = 1200
    for max_speed in range(min_max_speed, max_max_speed, 100):
        print("max_speed:", max_speed)
        cars, memory = setup_cars_set_parameters(v_max=max_speed)
        simulate(cars, memory, wave_size, wave_speed, 60, 140)
    plt.figure(1)
    plt.plot(range(min_max_speed, max_max_speed, 100), wave_size)
    plt.title("wave size")
    plt.xlabel("max speed")
    plt.ylabel("number of cars in wave")

    plt.figure(2)
    plt.plot(range(min_max_speed, max_max_speed, 100), wave_speed)
    plt.title("wave speed")
    plt.xlabel("max speed")
    plt.ylabel("wave speed of shock wave")

    plt.show()

reaction_speed_graphs()
num_cars_graphs()
acc_retard_graphs()
max_speed_graphs()
