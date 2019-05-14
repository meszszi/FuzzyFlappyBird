import pygame
from numpy.random import rand

class Ball():
    def __init__(self, x, y, radius):
        self.init_x = x
        self.init_y = y
        self.x = x
        self.y = y
        self.radius = radius
        self.v_speed = 0

    def draw(self, screen, color=(0, 255, 0), vector=True):
        pygame.draw.circle(screen, color, (int(round(self.x)), int(round(self.y))), self.radius)
        if vector:
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (self.x, round(self.y + self.v_speed * 10)), 2)

    def add_speed(self, dv):
        self.v_speed += dv

    def trim_speed(self, max_speed):
        self.v_speed = max(-max_speed, min(max_speed, self.v_speed))

    def move(self, gravity, boosters, max_speed=None):

        self.v_speed += gravity - boosters

        if max_speed:
            self.trim_speed(max_speed)

        self.y += self.v_speed

    def restart(self):
        self.x = self.init_x
        self.y = self.init_y
        self.v_speed = 0.


class Wall():
    def __init__(self, left_x, gap_top, gap_bottom, height, width):
        self.left_x = left_x
        self.gap_top = gap_top
        self.gap_bottom = gap_bottom
        self.height = height
        self.width = width

    def draw(self, screen, color=(0, 0, 255)):
        pygame.draw.rect(screen, color,
                         pygame.Rect(round(self.left_x), 0, self.width, self.gap_top))
        pygame.draw.rect(screen, color,
                         pygame.Rect(round(self.left_x), self.gap_bottom, self.width, self.height - self.gap_bottom))

    def move(self, dx):
        self.left_x += dx

    def collides(self, ball):

        dist = lambda p: (ball.x - p[0])**2 + (ball.y - p[1])**2
        corners = [(self.left_x, self.gap_top), (self.left_x, self.gap_bottom),
                   (self.left_x + self.width, self.gap_top),
                   (self.left_x + self.width, self.gap_bottom)]

        if any(map(lambda p: dist(p) < ball.radius**2, corners)):
            return True

        center_x = self.left_x + self.width / 2

        if (ball.y < self.gap_top or ball.y > self.gap_bottom) and (
                    abs(ball.x - center_x) < ball.radius + self.width / 2):
            return True

        if (self.left_x < ball.x < self.left_x + self.width) and (
            abs(ball.y - self.gap_bottom) < ball.radius or (
                    abs(ball.y - self.gap_top < ball.radius))):
            return True

        return False

    def gap_center(self):
        return (self.gap_top + self.gap_bottom) / 2


class Game():
    def __init__(self, width, height,
                 walls_width, walls_space, walls_speed,
                 min_gap, max_gap, margin,
                 gravity, max_boost, max_ball_speed,
                 ball_radius, ball_init_x):
        self.width = width
        self.height = height
        self.walls_width = walls_width
        self.walls_space = walls_space
        self.walls_speed = walls_speed
        self.min_gap = min_gap
        self.max_gap = max_gap
        self.margin = margin
        self.gravity = gravity
        self.max_boost = max_boost
        self.max_ball_speed = max_ball_speed

        self.walls = []
        self.ball = Ball(ball_init_x, height / 2, ball_radius)

    def clear_walls(self):
        self.walls = filter(lambda w: w.left_x + w.width > 0, self.walls)

    def generate_random_wall(self):

        if len(self.walls) > 0:
            left_x = self.walls[-1].left_x + self.walls_width + self.walls_space

        else: left_x = self.width

        gap_width = (self.max_gap - self.min_gap) * rand() + self.min_gap
        gap_top = (self.height - gap_width - 2*self.margin) * rand() + self.margin

        wall = Wall(left_x, gap_top, gap_top + gap_width, self.height, self.walls_width)

        self.walls += [wall]

    def make_step(self, boost_fraction):

        if (len(self.walls) == 0) or (self.walls[-1].left_x + self.walls_space < self.width):
            self.generate_random_wall()

        for w in self.walls:
            w.move(-self.walls_speed)

        self.ball.move(self.gravity, boost_fraction * self.max_boost, self.max_ball_speed)

    def game_over(self, check_margin=True):
        if any(map(lambda w: w.collides(self.ball), self.walls)):
            return True

        if check_margin and ((self.ball.y < 0) or (self.ball.y > self.height)):
            return True

        return False

    def draw_indicator(self, screen, x, y, width, height, fraction,
                       fg_color, bg_color=(255, 255, 0)):
        bar_height = round(fraction * (height - 4))
        bar_top = y - 2 + (height - bar_height)
        pygame.draw.rect(screen, bg_color, pygame.Rect(x, y, width, height))
        pygame.draw.rect(screen, fg_color, pygame.Rect(x+2, bar_top, width-4, bar_height))

    def draw(self, screen, wall_color=(0, 0, 255), ball_color=(0, 255, 0), booster=None):
        for w in self.walls:
            w.draw(screen, wall_color)

        self.ball.draw(screen, ball_color)

        ind_w = 15
        ind_h = 120
        ind_space = 5
        ind_y = self.height - (ind_h + ind_space)
        ind_x = [self.width - ((i+1)*(ind_space+ind_w)) for i in range(4)]
        colors = [(255, 0, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0)]
        inputs = list(self.get_fuzzy_inputs()) + [booster]
        for x, c, i in zip(ind_x, colors, inputs):
            self.draw_indicator(screen, x, ind_y, ind_w, ind_h, i, c)

    def restart(self):
        self.walls = []
        self.ball.restart()

    def get_fuzzy_inputs(self):

        if len(self.walls) == 0:
            gap_y = 0
            wall_dist = 1

        else:
            nearest = list(filter(lambda w: w.left_x + w.width > self.ball.x, self.walls))[0]
            gap_y = ((self.ball.y - nearest.gap_center()) + self.height) / (2*self.height)
            wall_dist = min((nearest.left_x - self.ball.x + self.ball.radius) / self.walls_space, 1)

        speed = (-self.ball.v_speed + self.max_ball_speed) / (2*self.max_ball_speed)

        return speed, gap_y, wall_dist