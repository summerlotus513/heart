"""
"heart beat"
:author: zhouyq
:date: 2022-11-06
"""

# math func
from math import pi, log, sin, cos
# pytk
from tkinter import *
import random

CANVAS_WIDTH = 600  # view wigth
CANVAS_HEIGHT = 450  # view height
CANVAS_CENTER_X = CANVAS_WIDTH / 2  # center x
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2  # center y
IMAGE_ENLARGE = 10  # zoom ratio
HEART_COLOR = "#FF6EB4"  # heart clolor

def heartFunc(t, shrink_ratio: float = IMAGE_ENLARGE):
    """
    “heart create”
    :param shrink_ratio: ratio
    :param t: parameter
    :return: (x, y)
    """
    # calc function
    x = 17 * (sin(t) ** 3)
    y = -(15 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    # x = 2 * (cos(t) - cos(2*t))
    # y = 2 * (2*sin(t) - sin(2*t))

    # zoom+
    x *= shrink_ratio
    y *= shrink_ratio

    # move to cneter
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)

def randomInsideDiff(x, y, weights=0.15):
    """
    Random internal diffusion point
    :param x: Original x coordinate
    :param y: Original y coordinate
    :param weights: weighting
    :return: new coordinate  (x, y)
    """
    ratio_x = - weights * log(random.random())
    ratio_y = - weights * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy

def shake(x, y, scale):
    """
    Shake
    :param x: Original x coordinate
    :param y: Original y coordinate
    :param ratio: sacle
    :return: new coordinate (x, y)
    """
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = scale * force * (x - CANVAS_CENTER_X)
    dy = scale * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p, b):
    """
    curve func
    :param b: bezier parameter
    :param p: parameter
    :return: sin + bezier
    """

    # print('p:', p)
    t = sin(p)

    p0 = b[0]
    p1 = b[1]
    p2 = b[2]
    p3 = b[3]

    t1 = (1 - t)
    t2 = t1 * t1
    t3 = t2 * t1

    r = p0 * t3 + 3 * p1 * t * t2 + 3 * p2 * t * t * t1 + p3 * (t ** 3)  # bezier
    # r = 2 * (2 * sin(4 * p)) / (2 * pi)  # sin
    # print('r:', r)
    return r

def beatCurve(p):
    """
    Heart beat curve
    :param p: parameter
    :return: func
    """
    return curve(p, (.69, .75, .2, .95))

def haloCurve(p):
    return curve(p, (.75, .49, .46, .97))

class Heart:
    """
    Heart
    """

    def __init__(self, generate_frame=20):
        self._points = set()  # original points
        self._edge_diffusion_points = set()  # Edge diffusion effect point coordinate
        self._center_diffusion_points = set()  # Center diffusion effect point coordinate
        self.all_points = {}  # Coordinates of dynamic points per frame
        self.build(500)

        self.random_halo = 1000

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # heart
        for _ in range(number):
            t = random.uniform(0, 2.1 * pi)  # call gaps
            x, y = heartFunc(t)  # make heart
            self._points.add((x, y))

        # Inner diffusion
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = randomInsideDiff(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # diffusion
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = randomInsideDiff(x, y, 0.24)  # is center point nums
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calcCoordinates(x, y, ratio):
        # change scale
        scale = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.45)  # magic parameter

        dx = ratio * scale * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * scale * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        scale = 10 * beatCurve(generate_frame / 10 * pi)  # scale

        halo_radius = int(4 + 6 * (1 + beatCurve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(beatCurve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # halo
        heart_halo_point = set()  # halo points
        for _ in range(halo_number):
            t = random.uniform(0, 2.1 * pi)  # call gaps
            x, y = heartFunc(t, shrink_ratio=haloCurve(generate_frame / 10 * pi) + 11)  # magic
            x, y = shake(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # calc new point
                heart_halo_point.add((x, y))
                nRandomIntRange = int(27 + haloCurve(generate_frame / 10 * pi) + 4)
                x += random.randint(-nRandomIntRange, nRandomIntRange)
                y += random.randint(-nRandomIntRange, nRandomIntRange)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))

        # contour
        for x, y in self._points:
            x, y = self.calcCoordinates(x, y, scale)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # content
        for x, y in self._edge_diffusion_points:
            x, y = self.calcCoordinates(x, y, scale)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calcCoordinates(x, y, scale)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    # 30 is frame switch diff, low fps is high
    main.after(300, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()
    root.title('Heart~~')
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart(50)
    draw(root, canvas, heart)
    root.mainloop()
