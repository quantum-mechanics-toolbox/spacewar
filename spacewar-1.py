#!/usr/bin/python3

# KidsCanCode - Game Development with Pygame video series
# Shmup game - part 1
# Video link: https://www.youtube.com/watch?v=nGufy7weyGY
# Player sprite and movement

import pygame
import random
import math
import os
import time

WIDTH = 640
HEIGHT = 640
RADIUS = 300
FPS = 60
CENTER = (WIDTH/2, HEIGHT/2)
G = 80.0
BULLET_G = G/1.0
SHIP_NUM = 20
SHIP_SIZE = 1
START_SPEED = 1.0
MAX_SPEED = 20.0
FADE = True
FADE_PARAM = 32
BULLET_COOLDOWN = 1


# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255,127,0)
MONO_COLOR = ORANGE

# initialize pygame and create window
random.seed()
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20,20)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spacewar!")
clock = pygame.time.Clock()

def ran(number):
    return random.randrange(number)

def AngleToCoords(theta, mag):
    theta = 6.2832*theta/360.0
    MagX = mag*math.cos(theta)
    MagY = mag*math.sin(theta)
    return (MagX, MagY)

def SetColor():
    r_chan = ran(255)
#    r_chan = 255
    g_chan = ran(255)
    b_chan = ran(255)
#    r_chan = (r_chan/2) + 128
#    g_chan = (g_chan/2) + 128
#    b_chan = (b_chan/2) + 128
#    print (r_chan, g_chan, b_chan)
    return (r_chan, g_chan, b_chan)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
#        self.image = pygame.Surface((SHIP_SIZE, SHIP_SIZE))
#        self.image.fill(MONO_COLOR)
        self.image_orig = pygame.Surface((40, 40))
        pygame.draw.polygon(self.image_orig, (MONO_COLOR[0]/4, MONO_COLOR[1]/4,MONO_COLOR[2]/4), ((20,0),(10,40),(30,40)))
        pygame.draw.polygon(self.image_orig, MONO_COLOR, ((20,0),(10,36),(30,36)), 4)
        self.image_orig.set_colorkey(BLACK)
#        pygame.draw.polygon(self.image_orig, MONO_COLOR, ((20,0),(10,38),(30,38)), 4)
#        self.image.fill(GREEN)
#        self.image.fill(SetColor())
        self.image_orig = pygame.transform.scale(self.image_orig, (30,30))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.locx = 0.0
        self.locy = 0.0
        self.rot = 0.0
        self.NewPos()
        self.NewSpeed()

    def NewPos(self):
        self.locx = (WIDTH/2) - (random.randrange(RADIUS) - (RADIUS/2))
        self.locy = (HEIGHT/2) - (random.randrange(RADIUS) - (RADIUS/2))
#        print (self.locx, self.locy)
        self.rect.centerx = self.locx
        self.rect.centery = self.locy

    def NewSpeed(self):
        self.speedx = START_SPEED*(random.randrange(-100,100)/100.0)
        self.speedy = START_SPEED*(random.randrange(-100,100)/100.0)
#        self.speedx = 0.0
#        self.speedy = 0.0

    def CheckMaxSpeed(self):
#        if ((abs(self.speedx)>MAX_SPEED)or(abs(self.speedy)>MAX_SPEED)): self.NewSpeed()
        if (self.speedx>MAX_SPEED): self.speedx = MAX_SPEED
        if (self.speedy>MAX_SPEED): self.speedy = MAX_SPEED
        if (self.speedx<(-1.0*MAX_SPEED)): self.speedx = -1.0*MAX_SPEED
        if (self.speedy<(-1.0*MAX_SPEED)): self.speedy = -1.0*MAX_SPEED
                
    def update(self):
#        self.speedx = 0
#        self.speedy = 0
        if self.GetDistance() > RADIUS:
            self.locx = WIDTH - self.locx + self.speedx
            self.locy = HEIGHT - self.locy + self.speedy
            self.rect.centerx = self.locx
            self.rect.centery = self.locy
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.rot += 2
        if keystate[pygame.K_RIGHT]:
            self.rot -= 2
        if keystate[pygame.K_UP]:
            thrust = AngleToCoords(self.rot, -0.05)
            self.speedx += thrust[1]
            self.speedy += thrust[0]
#        if (self.GetDistance()==0):
#            self.NewPos()
#            self.NewSpeed()
        if (self.GetDistance()<5):
            self.NewPos()
            self.NewSpeed()
        self.speedx -= G*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
        self.speedy -= G*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
#        self.CheckMaxSpeed()
        self.locx += self.speedx
        self.locy += self.speedy
        self.rect.centerx = self.locx
        self.rect.centery = self.locy
        self.image = pygame.transform.rotate(self.image_orig, self.rot)

    def GetDistance(self):
        Dx = pow(self.rect.centerx - CENTER[0], 2)
        Dy = pow(self.rect.centery - CENTER[1], 2)
        return pow(Dx + Dy, 0.5)

    def shoot(self):
        thrust = AngleToCoords(self.rot, -2.0)
#        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[0], self.speedy+thrust[1])
        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0])
        all_sprites.add(bullet)
        bullets.add(bullet)
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speedx, speedy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(MONO_COLOR)
        self.rect = self.image.get_rect()
        self.locx = x
        self.locy = y
        self.speedx = speedx
        self.speedy = speedy
        self.rect.centerx = self.locx
        self.rect.centery = self.locy
#        print(self.rect.centerx, self.rect.centery)

    def update(self):
        if self.GetDistance() > RADIUS:
            self.kill()
        if (self.GetDistance()==0):
            self.kill()
        self.speedx -= BULLET_G*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
        self.speedy -= BULLET_G*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
        self.locx += self.speedx
        self.locy += self.speedy
        self.rect.centerx = self.locx
        self.rect.centery = self.locy

    def GetDistance(self):
        Dx = pow(self.rect.centerx - CENTER[0], 2)
        Dy = pow(self.rect.centery - CENTER[1], 2)
        return pow(Dx + Dy, 0.5)

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
fade_fill = pygame.Surface((WIDTH, HEIGHT))
fade_fill.set_alpha(FADE_PARAM)
pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())
LastBulletTime = time.time() - BULLET_COOLDOWN

star = pygame.Surface((10,10))
pygame.draw.circle(star, MONO_COLOR, (5,5), 5)

ships = []
#for i in range(0,SHIP_NUM):
#    ships.append(Player())
#all_sprites.add(ships)
player = Player()
all_sprites.add(player)
    
# Game loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if (time.time() > (LastBulletTime + BULLET_COOLDOWN)):
                    player.shoot()
                    LastBulletTime = time.time()
    # Update
    all_sprites.update()

    # Draw / render
    if (FADE): screen.blit(fade_fill, (0,0))
    else: screen.fill(BLACK)
    screen.blit(star, CENTER)
    all_sprites.draw(screen)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
