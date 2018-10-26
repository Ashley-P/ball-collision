import sys
import pygame
import math
from random import randint as ri



# Initialisiing modules
pygame.init()

### CONSTANTS ###
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
OFFSET = 25

### INITIALISATION ###
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
done = False
clock = pygame.time.Clock()
myfont = pygame.font.SysFont('Arial', 30)


class Vector2d(object):
    def __init__(self, x=0, y=0):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @x.setter
    def x(self, x):
        if x < 0 or x > SCREEN_WIDTH:
            self.__x = x % SCREEN_WIDTH
        else:
            self.__x = x

    @y.setter
    def y(self, y):
        if y < 0 or y > SCREEN_HEIGHT:
            self.__y = y % SCREEN_HEIGHT 
        else:
            self.__y = y

    def __add__(self, other):
        if type(other) == Vector2d:
            return Vector2d(self.x + other.x, self.y + other.y)
        else:
            return Vector2d(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) == Vector2d:
            return Vector2d(self.x - other.x, self.y - other.y)
        else:
            return Vector2d(self.x - other, self.y - other)
    
    def __mul__(self, other):
        if type(other) == Vector2d:
            return Vector2d(self.x * other.x, self.y * other.y)
        else:
            return Vector2d(self.x * other, self.y * other)

    def __rmul__(self, other):
            return self * other

    def __truediv__(self, other):
        if type(other) == Vector2d:
            return Vector2d(self.x / other.x, self.y / other.y)
        else:
            return Vector2d(self.x / other, self.y / other)

    def dot_product(self, other):
        return ((self.x * other.x) + (self.y * other.y))

    def cross_product(self, other):
        return ((self.x * other.x) - (self.y * other.y))

    def magnitude(self):
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def normal(self):
        magnitude = self.magnitude()
        if magnitude != 0:
            return Vector2d(self.x / magnitude, self.y / magnitude)
        else:
            return Vector2d()

    def perpendicular(self):
        return Vector2d(-self.y, self.x)



class Ball(object):
    def __init__(self):
        self.colour = (ri(0, 255), ri(0, 255), ri(0, 255))
        self.pos    = Vector2d(ri(0, SCREEN_WIDTH), ri(0, SCREEN_HEIGHT))
        self.vel    = Vector2d(ri(-10, 10),ri(-10, 10))
        self.radius = ri(0, 100)
        self.mass   = ri(1, 50)

    def draw(self):
        pygame.draw.circle(screen, self.colour, (int(self.pos.x), int(self.pos.y)), self.radius)

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y



def do_collision(b1, b2):
    #col_vecx = (((b1.vec2d.x * b2.radius) + (b2.vec2d.x * b1.radius)) / (b1.radius + b2.radius))
    #col_vecy = (((b1.vec2d.y * b2.radius) + (b2.vec2d.y * b1.radius)) / (b1.radius + b2.radius))

    #vel1x = (b1.vel.x * (b1.mass - b2.mass)) + (2 * b2.mass * b2.vel.x) / (b1.mass + b2.mass)
    #vel1y = (b1.vel.y * (b1.mass - b2.mass)) + (2 * b2.mass * b2.vel.y) / (b1.mass + b2.mass)
    #vel2x = (b2.vel.x * (b2.mass - b1.mass)) + (2 * b1.mass * b1.vel.x) / (b2.mass + b1.mass)
    #vel2y = (b2.vel.y * (b2.mass - b1.mass)) + (2 * b1.mass * b1.vel.y) / (b2.mass + b1.mass)

    # return if objects are moving away from each other
    #if (b2.vel - b1.vel).dot_product(b2.pos - b1.pos) <= 0:

    # Getting the normal
    v_n = b2.pos - b1.pos
    v_un = v_n.normal()
    v_ut = v_un.perpendicular()

    v1n = v_un.dot_product(b1.vel)
    v1t = v_ut.dot_product(b1.vel)
    v2n = v_un.dot_product(b2.vel)
    v2t = v_ut.dot_product(b2.vel)

    v1tPrime = v1t
    v2tPrime = v2t

    v1nPrime = (v1n * (b1.mass - b2.mass) + (2 * b2.mass * v2n)) / (b1.mass + b2.mass)
    v2nPrime = (v2n * (b2.mass - b1.mass) + (2 * b1.mass * v1n)) / (b2.mass + b1.mass)

    v_v1nPrime = v1nPrime * v_un
    v_v1tPrime = v1tPrime * v_ut
    v_v2nPrime = v2nPrime * v_un
    v_v2tPrime = v2tPrime * v_ut

    b1.vel.x = v_v1nPrime.x + v_v1tPrime.x
    b1.vel.y = v_v1nPrime.y + v_v1tPrime.y
    b2.vel.x = v_v2nPrime.x + v_v2tPrime.x
    b2.vel.y = v_v2nPrime.y + v_v2tPrime.y


def check_intersection(b1, b2):
    delta = b1.pos - b2.pos

    distance = math.sqrt(delta.x * delta.x + delta.y * delta.y)

    if distance < b1.radius + b2.radius:
        return True
    else:
        return False


def query_collision_pairs(balls):
    i = 0
    j = 0
    while (i < len(balls) - 1):
        b1 = balls[i]
        j = i + 1
        while (j < len(balls)):
            b2 = balls[j]
            if (check_intersection(b1, b2)):
                do_collision(b1, b2)
            else:
                pass
            j += 1

        i += 1



#all_balls = [Ball() for x in range(100)]
#all_balls = [Ball(), Ball()]

all_balls = [Ball() for _ in range(int(sys.argv[1]))]

while not done:

    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Checking if the player has pressed the X on the window
            done = True

    screen.fill((0, 0, 0)) # Black background


    for each in all_balls:
        each.draw()
        each.update()

    query_collision_pairs(all_balls)


    FPS = myfont.render("{:2.2f}".format(clock.get_fps()), False, (0, 0, 255))
    screen.blit(FPS, (0, 0))

    pygame.display.flip()
