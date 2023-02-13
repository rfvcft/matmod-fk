import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import sys

class Car:
    def __init__(self, v_max, reaction_time, acceleration, position) -> None:
        self.v_max = v_max
        self.r = reaction_time
        self.a = acceleration
        self.pos = position
        self.v = v_max

N = 50
V_MAX = 60
D_TOT = 314
REACTION_TIME = 1
ACCELERATION = 1

def setup_cars():
    cars = [Car(V_MAX, REACTION_TIME, ACCELERATION, i/N*D_TOT) for i in range(N)]
    return cars

def draw(cars):
    fig = plt.figure()
    axis = plt.axes(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
    dt = 0.1

    def animate(i):
        axis.clear()
        axis.set_aspect(1)
        drawing_uncolored_circle = plt.Circle((0, 0), 1 , fill = False)
        axis.add_artist(drawing_uncolored_circle)
        for car in cars:
            theta = (2*math.pi)/D_TOT * car.pos
            car.pos += dt*car.v
            plt.plot(math.cos(theta), math.sin(theta), "x")

    anim = FuncAnimation(fig, animate, interval=20, repeat=False)
    # anim.save('cars.mp4', writer='ffmpeg', fps=30)
    # plt.title('Circle')
    # plt.show()
    plt.show()
    print("AFTER SHOW")
    sys.exit()

def main():
    cars = setup_cars()
    draw(cars)

main()
