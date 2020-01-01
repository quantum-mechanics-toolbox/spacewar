#!/usr/bin/python3

# KidsCanCode - Game Development with Pygame video series
# Shmup game - part 1
# Video link: https://www.youtube.com/watch?v=nGufy7weyGY
# Player sprite and movement

import pygame
import random
import math
import os

WIDTH = 640
HEIGHT = 640
RADIUS = 300
FPS = 60
CENTER = (WIDTH/2, HEIGHT/2)
G = 80.0
SHIP_NUM = 20
SHIP_SIZE = 1
START_SPEED = 1.0
MAX_SPEED = 20.0
FADE = False

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

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
        self.image = pygame.Surface((SHIP_SIZE, SHIP_SIZE))
#        self.image.fill(GREEN)
        self.image.fill(SetColor())
        self.rect = self.image.get_rect()
        self.locx = 0.0
        self.locy = 0.0
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
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedy += -0.2
        if keystate[pygame.K_RIGHT]:
            self.speedy += 0.2
        if (self.GetDistance()==0):
            self.NewPos()
            self.NewSpeed()
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
        if self.GetDistance() > RADIUS:
#            self.rect.centerx = WIDTH - self.rect.centerx
#            self.rect.centery = HEIGHT - self.rect.centery
            self.locx = WIDTH - self.locx
            self.locy = HEIGHT - self.locy
#            print(self.locx, self.locy)
            self.rect.centerx = self.locx
            self.rect.centery = self.locy

    def GetDistance(self):
        Dx = pow(self.rect.centerx - CENTER[0], 2)
        Dy = pow(self.rect.centery - CENTER[1], 2)
        return pow(Dx + Dy, 0.5)
    
all_sprites = pygame.sprite.Group()

fade_fill = pygame.Surface((WIDTH, HEIGHT))
fade_fill.set_alpha(1)
pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())

ships = []
for i in range(0,SHIP_NUM):
    ships.append(Player())
all_sprites.add(ships)
#player = Player()
#all_sprites.add(player)
    
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

    # Update
    all_sprites.update()

    # Draw / render
#    screen.fill(BLACK)
    if (FADE): screen.blit(fade_fill, (0,0))
    all_sprites.draw(screen)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
