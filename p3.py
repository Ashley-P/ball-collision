import sys
import copy
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
paused = False
clock = pygame.time.Clock()
myfont = pygame.font.SysFont('Arial', 30)


class Vector2d(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


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
        self.radius = ri(10, 100)
        self.mass   = int(self.radius / 10)
        #self.mass   = ri(1, 10)
        self._pos   = Vector2d(ri(0 + self.radius, SCREEN_WIDTH - self.radius), ri(0 + self.radius, SCREEN_HEIGHT - self.radius))
        self._vel   = Vector2d(ri(-10, 10),ri(-10, 10))


    @property
    def vel(self):
        return self._vel

    @vel.setter
    def vel(self, vel):
        if vel.x > 10:
            vel.x = 10
        elif vel.x < -10:
            vel.x = -10

        if vel.y > 10:
            vel.y = 10
        elif vel.y < -10:
            vel.y = -10

        self._vel = vel

    @property
    def pos(self):
        return self._pos

    # Setter is a bit pointless since balls can't leave the bounds of the screen
    @pos.setter
    def pos(self, pos):
        self._pos.x = pos.x % SCREEN_WIDTH
        self._pos.y = pos.y % SCREEN_HEIGHT

        
    def draw(self):
        pygame.draw.circle(screen, self.colour, (int(self.pos.x), int(self.pos.y)), self.radius)

    def update(self):
        #self.pos.x += self.vel.x
        #self.pos.y += self.vel.y
        self.pos = self.pos + self.vel



def ballball_collision(b1, b2):
    # Storing the old vectors
    b1old = copy.copy(b1.vel)
    b2old = copy.copy(b2.vel)

    # Getting the normal, unit normal and unit tangent
    v_n = b2.pos - b1.pos
    v_un = v_n.normal()
    v_ut = v_un.perpendicular()

    # dot products
    v1n = v_un.dot_product(b1.vel)
    v1t = v_ut.dot_product(b1.vel)
    v2n = v_un.dot_product(b2.vel)
    v2t = v_ut.dot_product(b2.vel)

    # New velocity normals and tangents
    v1tPrime = v1t
    v2tPrime = v2t

    v1nPrime = (v1n * (b1.mass - b2.mass) + (2 * b2.mass * v2n)) / (b1.mass + b2.mass)
    v2nPrime = (v2n * (b2.mass - b1.mass) + (2 * b1.mass * v1n)) / (b2.mass + b1.mass)

    v_v1nPrime = v1nPrime * v_un
    v_v1tPrime = v1tPrime * v_ut
    v_v2nPrime = v2nPrime * v_un
    v_v2tPrime = v2tPrime * v_ut

    ## Updating velocity
    #b1.vel.x = v_v1nPrime.x + v_v1tPrime.x
    #b1.vel.y = v_v1nPrime.y + v_v1tPrime.y
    #b2.vel.x = v_v2nPrime.x + v_v2tPrime.x
    #b2.vel.y = v_v2nPrime.y + v_v2tPrime.y

    b1.vel = v_v1nPrime + v_v1tPrime
    b2.vel = v_v2nPrime + v_v2tPrime

    # Stopping balls from getting stuck into each other
    # Super inefficient
    tmp = min([b1old.x, b1old.y, b2old.x, b2old.y])
    b1old = b1old / tmp
    b2old = b2old / tmp

    #while (check_intersection(b1, b2)):
    #    b1.vel = b1.vel + b1old
    #    b2.vel = b2.vel + b2old
    #
    #b1.draw()
    #b2.draw()

    # Stopping balls from getting stuck into each other


def check_intersection(b1, b2):
    delta = (b1.pos + b1.vel) - (b2.pos + b2.vel)

    distance = math.sqrt(delta.x * delta.x + delta.y * delta.y)

    if distance < b1.radius + b2.radius:
        return True
    else:
        return False


def query_collision_pairs(balls, isStatic):
    # Somewhat inefficient
    i = 0
    j = 0
    # checking ball to ball collisions
    while (i < len(balls) - 1):
        b1 = balls[i]
        j = i + 1
        while (j < len(balls)):
            b2 = balls[j]
            if (check_intersection(b1, b2)):
                if isStatic:
                    # Can exceed recusrion depth here if there are too many balls
                    balls[i] = Ball()
                    query_collision_pairs(balls, 1)
                    return
                elif not isStatic:
                    ballball_collision(b1, b2)
            else:
                pass
            j += 1

        i += 1

    # checking ball to wall collisions
    for a in balls:
        if (a.pos.x + a.vel.x) - a.radius < 0:             a.vel.x = abs(a.vel.x)
        if (a.pos.x + a.vel.x) + a.radius > SCREEN_WIDTH:  a.vel.x = -abs(a.vel.x)
        if (a.pos.y + a.vel.y) - a.radius < 0:             a.vel.y = abs(a.vel.y)
        if (a.pos.y + a.vel.y) + a.radius > SCREEN_HEIGHT: a.vel.y = -abs(a.vel.y)


def event_handling(ev):
    global paused

    # Key Events
    if ev.type == pygame.KEYDOWN:
        if ev.key == pygame.K_SPACE:
            paused = not paused
        elif ev.key == pygame.K_a:
            advance()

def advance():
    for each in all_balls:
        each.draw()
        each.update()
    query_collision_pairs(all_balls, isStatic=False)



# Some other initialisation
all_balls = [Ball() for _ in range(int(sys.argv[1]))]
query_collision_pairs(all_balls, isStatic=True)

while not done:

    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Checking if the player has pressed the X on the window
            done = True
        else:
            event_handling(event)

    screen.fill((0, 0, 0)) # Black background


    # Updating the logic
    if not paused:
        advance()
    else:
        for each in all_balls:
            each.draw()


    # Screen rendering stuff
    FPS = myfont.render("{:2.2f}".format(clock.get_fps()), False, (0, 0, 255))
    screen.blit(FPS, (0, 0))

    pygame.display.flip()

# Cleanup
pygame.quit()
