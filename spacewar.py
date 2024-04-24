#!/usr/bin/env python3

import pygame
import pygame.freetype
from operator import add, sub
import random
import math
import os
import time

WIDTH = 1240
HEIGHT = 640
ASPECT = float(WIDTH)/HEIGHT
RADIUS = 360
FPS = 60
CENTER = (WIDTH/2, HEIGHT/2)
G = 80.0
BULLET_G = G/1.0
SHIP_NUM = 20
SHIP_SIZE = 1
STAR_SIZE = 50
BG_STARS = 60
START_SPEED = 1.0
MAX_SPEED = 20.0
FADE = True
FADE_PARAM = 8
BULLET_COOLDOWN = 1
NUM_HYPERS = 3

FRAGMENTS = 50
FRAG_DECAY = 50

SCORE = [0,0]
SCORE1_POS = (WIDTH*1.5/9, HEIGHT/6)
SCORE2_POS = (WIDTH*7.5/9, HEIGHT/6)
SCORE_SIZE = 40
UI1_POS = (WIDTH*1.5/9, HEIGHT/6)
UI2_POS = (WIDTH*1.1/9, HEIGHT/2)
UI3_POS = (WIDTH*1.5/9, HEIGHT*5/6)
UI4_POS = (WIDTH*7.5/9, HEIGHT/6)
UI5_POS = (WIDTH*7.9/9, HEIGHT/2)
UI6_POS = (WIDTH*7.5/9, HEIGHT*5/6)
LAMP_SIZE = 120

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255,127,0)
MONO_COLOR = ORANGE
COLOR1 = CYAN
COLOR2 = GREEN

# initialize pygame and create window
random.seed()
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20,20)
pygame.init()
pygame.mixer.init()
#pygame.freetype.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
### NEED TO FIGURE OUT FULLSCREEN
#screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Spacewar!")
clock = pygame.time.Clock()
print(pygame.freetype.get_default_font())
font = pygame.freetype.Font("./fonts/OSCILLOS.TTF")
font.fgcolor = MONO_COLOR

#%% Generic Functions

def ran(number):
    return random.randrange(number)

def RandSign():
    return 1 if random.random() < 0.5 else -1

def SubCoords(a, b):
    return ((a[0]-b[0]),(a[1]-b[1]))

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

def ColorTint(source, tint):
  r = (tint[0]/255)*source[0]
  g = (tint[1]/255)*source[1]
  b = (tint[2]/255)*source[2]
  return (r,g,b,source[3])

def ColorSubtract(source, value):
  r = source[0] - value
  g = source[1] - value
  b = source[2] - value
  if r<0: r=0
  if g<0: g=0
  if b<0: b=0
  return (r,g,b,source[3])


#%%

class Player(pygame.sprite.Sprite):
    def __init__(self, playernum, shiptype):
        pygame.sprite.Sprite.__init__(self)
#        self.image = pygame.Surface((SHIP_SIZE, SHIP_SIZE))
#        self.image.fill(MONO_COLOR)
        self.image_orig = pygame.Surface((40, 40))
        self.playernum = playernum
        if playernum == 1: self.color = COLOR1
        elif playernum == 2: self.color = COLOR2
        self.DrawType(shiptype)
        self.image_orig.set_colorkey(BLACK)
        self.image_orig = pygame.transform.scale(self.image_orig, (30,30))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.locx = 0.0
        self.locy = 0.0
        self.rot = 0.0
        self.hyperspace = NUM_HYPERS
        self.NewSpeed()
        self.StartPos()

    def StartPos(self):
# Right Left Start Positions
#        if self.playernum ==1:
#            self.locx = (WIDTH/4) - (random.randrange(RADIUS) - (RADIUS/2))
#        if self.playernum ==2:
#            self.locx = (WIDTH*3/4)- (random.randrange(RADIUS) - (RADIUS/2))
#        self.locy = (HEIGHT/2) - (random.randrange(RADIUS) - (RADIUS/2))
        self.NewPos()

    def DrawType(self, ShipType):
        if ShipType==1:
            pygame.draw.polygon(self.image_orig, (self.color[0]/4, self.color[1]/4,self.color[2]/4), ((20,0),(10,40),(30,40)))
            pygame.draw.polygon(self.image_orig, self.color, ((20,0),(10,36),(30,36)), 4)
        if ShipType==2:
            pygame.draw.polygon(self.image_orig, (self.color[0]/4, self.color[1]/4,self.color[2]/4), ((20,10),(0,40),(40,40)))
            pygame.draw.polygon(self.image_orig, self.color, ((20,10),(0,36),(40,36)), 4)
            pygame.draw.polygon(self.image_orig, (self.color[0]/4, self.color[1]/4,self.color[2]/4), ((20,0),(15,40),(25,40)))
            pygame.draw.polygon(self.image_orig, self.color, ((20,0),(15,36),(25,36)), 4)
        if ShipType==3:
            pygame.draw.polygon(self.image_orig, (self.color[0]/4, self.color[1]/4,self.color[2]/4), ((20,10),(0,30),(0,40),(40,40),(40,30)))
            pygame.draw.polygon(self.image_orig, self.color, ((20,10),(0,30),(0,36),(36,36),(36,30)), 4)
            pygame.draw.polygon(self.image_orig, (self.color[0]/4, self.color[1]/4,self.color[2]/4), ((25,0),(15,0),(15,40),(25,40)))
            pygame.draw.polygon(self.image_orig, self.color, ((25,0),(15,0),(15,36),(25,36)), 4)

    def NewPos(self):
#        self.locx = (WIDTH/2) - (random.randrange(RADIUS) - (RADIUS/2))
#        self.locy = (HEIGHT/2) - (random.randrange(RADIUS) - (RADIUS/2))
        angle = random.random()*360
        distance = random.randrange(2*STAR_SIZE, 0.9*RADIUS)
        self.locx = CENTER[0] + AngleToCoords(angle, distance)[0]
        self.locy = CENTER[1] + AngleToCoords(angle, distance)[1]
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
        if self.GetBoundary() > RADIUS:
#            self.locx = WIDTH - self.locx + (4.0*self.speedx)
#            self.locy = HEIGHT - self.locy + (4.0*self.speedy)
            self.locx = WIDTH - self.locx
            self.locy = HEIGHT - self.locy
            self.rect.centerx = self.locx
            self.rect.centery = self.locy
        keystate = pygame.key.get_pressed()
        if self.playernum == 1:
            if keystate[pygame.K_LEFT]:
                self.rot += 2
            if keystate[pygame.K_RIGHT]:
                self.rot -= 2
            if keystate[pygame.K_UP]:
                thrust = AngleToCoords(self.rot, -0.05)
                self.speedx += thrust[1]
                self.speedy += thrust[0]
            if keystate[pygame.K_DOWN]:
                #self.Explode()
                #self.kill()
                if self.hyperspace>0:
                    self.hyperspace -=1
                    self.NewPos()
                    self.NewSpeed()
        if self.playernum == 2:
            if keystate[pygame.K_a]:
                self.rot += 2
            if keystate[pygame.K_d]:
                self.rot -= 2
            if keystate[pygame.K_w]:
                thrust = AngleToCoords(self.rot, -0.05)
                self.speedx += thrust[1]
                self.speedy += thrust[0]
            if keystate[pygame.K_s]:
                if self.hyperspace>0:
                    self.hyperspace -=1
                    self.NewPos()
                    self.NewSpeed()
#        if (self.GetDistance()==0):
#            self.NewPos()
#            self.NewSpeed()
#        if (self.GetDistance()<STAR_SIZE):
#            self.NewPos()
#            self.NewSpeed()
#            self.kill()
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
        distance = pow(Dx + Dy, 0.5)
        if distance == 0:
            distance = 1
        return distance

    def GetBoundary(self):
# Frame boundary
#        Dx = pow((self.rect.centerx - CENTER[0])/ASPECT, 2)
#        Dy = pow(self.rect.centery - CENTER[1], 2)
# Radius Boundary
        Dx = pow(self.rect.centerx - CENTER[0], 2)
        Dy = pow(self.rect.centery - CENTER[1], 2)
        return pow(Dx + Dy, 0.5)

    def shoot(self):
        thrust = AngleToCoords(self.rot, -2.0)
#        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[0], self.speedy+thrust[1])
#        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[1], self.speedy+thrust[0])
#        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0], self.color)
        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0], RED)
        all_sprites.add(bullet)
        if self.playernum==1: bullets1.add(bullet)
        elif self.playernum==2: bullets2.add(bullet)

    def Explode(self):
        for frag in range(1, FRAGMENTS):
            thrust = AngleToCoords(random.randrange(1,360), random.randrange(1,5))
    #        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[0], self.speedy+thrust[1])
    #        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[1], self.speedy+thrust[0])
    #        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0], self.color)
#"""static location"""
#            bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[0], thrust[1], self.color, random.randrange(FRAG_DECAY/2,FRAG_DECAY))
#"""ship velocity location"""
            bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[0]+self.speedx, thrust[1]+self.speedy, self.color, random.randrange(FRAG_DECAY/2,FRAG_DECAY))
            all_sprites.add(bullet)
            if self.playernum==1: bullets1.add(bullet)
            elif self.playernum==2: bullets2.add(bullet)
        self.NewPos()
        self.NewSpeed()
        self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speedx, speedy, color, lifespan=-1):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.locx = x
        self.locy = y
        self.speedx = speedx
        self.speedy = speedy
        self.lifespan = lifespan
        self.rect.centerx = self.locx
        self.rect.centery = self.locy
#        print(self.rect.centerx, self.rect.centery)

    def update(self):
        if self.GetBoundary() > RADIUS:
            self.kill()
        if self.lifespan > -1:
            self.lifespan -= 1
            if self.lifespan == 0:
                self.kill()
#                print(SCORE, len(all_sprites))
        if (self.GetDistance() < STAR_SIZE):
            self.kill()
#            print(SCORE, len(all_sprites))
        self.speedx -= BULLET_G*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
        self.speedy -= BULLET_G*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
        self.locx += self.speedx
        self.locy += self.speedy
        self.rect.centerx = self.locx
        self.rect.centery = self.locy

    def GetBoundary(self):
# Frame boundary
#        Dx = pow((self.rect.centerx - CENTER[0])/ASPECT, 2)
#        Dy = pow(self.rect.centery - CENTER[1], 2)
# Radius boundary
        Dx = pow(self.rect.centerx - CENTER[0], 2)
        Dy = pow(self.rect.centery - CENTER[1], 2)
        return pow(Dx + Dy, 0.5)

    def GetDistance(self):
        Dx = pow(self.rect.centerx - CENTER[0], 2)
        Dy = pow(self.rect.centery - CENTER[1], 2)
        distance = pow(Dx + Dy, 0.5)
        if distance == 0:
            distance = 1
        return distance

class Star(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((STAR_SIZE*2,STAR_SIZE*2), pygame.SRCALPHA)
#        pygame.draw.circle(self.image, MONO_COLOR, (STAR_SIZE,STAR_SIZE), STAR_SIZE, 3)
#        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.locx = CENTER[0]
        self.locy = CENTER[1]
        self.rect.centerx = self.locx
        self.rect.centery = self.locy
#        print(self.rect.centerx, self.rect.centery)

    def update(self):
#        self.image.fill((0,0,0))
        pygame.draw.circle(self.image, (0,0,0,1), (STAR_SIZE,STAR_SIZE), STAR_SIZE)
        if pygame.time.get_ticks()%2 == 0:
          pygame.draw.circle(self.image, MONO_COLOR, (STAR_SIZE,STAR_SIZE), random.random()*STAR_SIZE, 1)


# class HUD():
#     def __init__(self):

#         self.barw = int(WIDTH*0.02)
#         self.barh = int(HEIGHT*0.16)
#         self.CBar_1 = pygame.sprite.Sprite()
#         self.CBar_1.image = pygame.Surface((self.barw, self.barh))
#         self.CBar_1.image.fill(COLOR1)
#         self.CBar_1.rect = self.CBar_1.image.get_rect()
#         self.CBar_1.rect.left = WIDTH*0.02
#         self.CBar_1.rect.bottom = HEIGHT*0.95

#         self.HUD_sprites = pygame.sprite.Group()
#         self.HUD_sprites.add(self.CBar_1)

#     def update(self):
#         Bar_1 = float(time.time() - LastBulletTime1)/BULLET_COOLDOWN
#         if Bar_1>1.0: Bar_1 = 1.0
#         elif Bar_1<0.01: Bar_1 = 0.01
#         self.CBar_1.image = pygame.transform.scale(self.CBar_1.image, (self.barw,int(self.barh*Bar_1)))
#         self.CBar_1.rect = self.CBar_1.image.get_rect()
#         self.CBar_1.rect.left = WIDTH*0.02
#         self.CBar_1.rect.bottom = HEIGHT*0.95

def Background():
    background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(background, (0,0,0,255), background.get_rect())
    pygame.draw.circle(background, (0,0,0,0), CENTER, RADIUS)
    pygame.draw.circle(background, MONO_COLOR, CENTER, RADIUS, 1)
    for star in range(BG_STARS):
        size = random.randrange(1,3)
        angle = random.random()*360
        distance = random.randrange(STAR_SIZE, 0.9*RADIUS)
        position = (CENTER[0] + AngleToCoords(angle, distance)[0], CENTER[1] + AngleToCoords(angle, distance)[1])
        pygame.draw.circle(background, MONO_COLOR, position, size)
    return background

def CreateElements():
    background = Background()

    lamp_surf = pygame.image.load("./gfx/lamp.png")
    lamp_surf = lamp_surf.convert_alpha()
    for x in range(0, lamp_surf.get_width()):
      for y in range(0, lamp_surf.get_height()):
    #    print(lamp_surf.get_at((x,y)))
        lamp_surf.set_at((x,y), ColorTint(lamp_surf.get_at((x,y)), MONO_COLOR))
    lamp_surf = pygame.transform.scale(lamp_surf, (LAMP_SIZE, LAMP_SIZE))

    return lamp_surf, background

def HUD():
    hud = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    hud.blit(background, (0,0))

    bullet_lamp_scale_1 = float(time.time() - LastBulletTime1)/BULLET_COOLDOWN
    if bullet_lamp_scale_1>1.0: bullet_lamp_scale_1 = 1.0
    elif bullet_lamp_scale_1<0.01: bullet_lamp_scale_1 = 0.01

#     scaled_lamp_surf = pygame.transform.scale_by(lamp_surf, bullet_lamp_scale_1)
# #    hud.blit(lamp_surf, (0,0))
#     hud.blit(scaled_lamp_surf, SubCoords(UI1_POS, scaled_lamp_surf.get_rect().center))

#    sub_lamp_surf = lamp_surf.copy()
#    for x in range(0, sub_lamp_surf.get_width()):
#      for y in range(0, sub_lamp_surf.get_height()):
#    #    print(lamp_surf.get_at((x,y)))
#        sub_lamp_surf.set_at((x,y), ColorSubtract(sub_lamp_surf.get_at((x,y)), int(255*(1.0-bullet_lamp_scale_1))))
#    hud.blit(sub_lamp_surf, SubCoords(UI2_POS, sub_lamp_surf.get_rect().center))

    # alpha_lamp_surf = lamp_surf.copy()
    # alpha_lamp_surf.set_alpha(int(255*bullet_lamp_scale_1))
    # hud.blit(alpha_lamp_surf, SubCoords(UI3_POS, alpha_lamp_surf.get_rect().center))


    font.size = SCORE_SIZE
    score_player1, score_player1_rect = font.render(str(SCORE[0]))
    score_player2, score_player2_rect = font.render(str(SCORE[1]))
    fps_disp, fps_disp_rect = font.render(str(fps))
    hud.blit(score_player1, SubCoords(UI1_POS, score_player1_rect.center))
    hud.blit(score_player2, SubCoords(UI4_POS, score_player2_rect.center))
    hud.blit(fps_disp, SubCoords(UI5_POS, fps_disp_rect.center))


    return hud


spawn_player1_event = pygame.USEREVENT + 1
spawn_player2_event = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_player1_event, 10, 1)
pygame.time.set_timer(spawn_player2_event, 10, 1)

all_sprites = pygame.sprite.Group()
bullets1 = pygame.sprite.Group()
bullets2 = pygame.sprite.Group()



#HUD = HUD()
#all_sprites.add(HUD.HUD_sprites)

lamp_surf, background = CreateElements()
star = Star()
all_sprites.add(star)
star_boundary = pygame.sprite.Group()
star_boundary.add(star)

fade_fill = pygame.Surface((WIDTH, HEIGHT))
fade_fill.set_alpha(FADE_PARAM)
pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())


#    background = pygame.sprite.Sprite()
#        self.background.image = pygame.Surface((WIDTH, HEIGHT))
#        self.background.image.fill((255,0,0,0))

#        pygame.draw.circle(self.background.image, MONO_COLOR, CENTER, RADIUS, 1)
#        self.background.rect = self.background.image.get_rect()


LastBulletTime1 = time.time() - BULLET_COOLDOWN
LastBulletTime2 = time.time() - BULLET_COOLDOWN

#star = pygame.Surface((STAR_SIZE*2,STAR_SIZE*2))
#pygame.draw.circle(star, MONO_COLOR, (STAR_SIZE,STAR_SIZE), STAR_SIZE)

ships = []
#for i in range(0,SHIP_NUM):
#    ships.append(Player())
#all_sprites.add(ships)
player1 = Player(1, 2)
player2 = Player(2, 3)
#all_sprites.add(player1)
#all_sprites.add(player2)



# Game loop
running = True
while running:
    # keep loop running at the right speed
    fps = int(1000/clock.tick(FPS))
#    print(fps)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == spawn_player1_event:
            all_sprites.add(player1)
#            pygame.event.clear(spawn_player1_event)
        elif event.type == spawn_player2_event:
            all_sprites.add(player2)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.key == pygame.K_RSHIFT:
                if (time.time() > (LastBulletTime1 + BULLET_COOLDOWN)):
                    player1.shoot()
                    LastBulletTime1 = time.time()
            if event.key == pygame.K_f:
                if (time.time() > (LastBulletTime2 + BULLET_COOLDOWN)):
                    player2.shoot()
                    LastBulletTime2 = time.time()
    if player1.alive():
        if (pygame.sprite.spritecollide(player1, bullets2, True)):
            player1.Explode()
            SCORE[1] += 1
            print(SCORE, len(all_sprites))
            pygame.time.set_timer(spawn_player1_event, 500, 1)
#            player1.kill()
    #        time.sleep(1)
    #        player1 = Player(1, 2)
    #        all_sprites.add(player1)
        if (pygame.sprite.spritecollide(player1, star_boundary, False)):
            player1.Explode()
            if SCORE[0] > 0:
                SCORE[0] -= 1
            print(SCORE, len(all_sprites))
            pygame.time.set_timer(spawn_player1_event, 500, 1)
#            player1.kill()
    #        time.sleep(1)
    #        player1 = Player(1, 2)
    #        all_sprites.add(player1)
    if player2.alive():
        if (pygame.sprite.spritecollide(player2, bullets1, True)):
            player2.Explode()
            SCORE[0] += 1
            print(SCORE, len(all_sprites))
            pygame.time.set_timer(spawn_player2_event, 500, 1)
    #        player2.kill()
    #        time.sleep(1)
    #        player2 = Player(2, 3)
    #        all_sprites.add(player2)
        if (pygame.sprite.spritecollide(player2, star_boundary, False)):
            player2.Explode()
            if SCORE[1] > 0:
                SCORE[1] -= 1
            print(SCORE, len(all_sprites))
            pygame.time.set_timer(spawn_player2_event, 500, 1)
    #        player2.kill()
    #        time.sleep(1)
    #        player2 = Player(2, 3)
    #        all_sprites.add(player2)

    # Update

    all_sprites.update()

    # Draw / render
    if (FADE): screen.blit(fade_fill, (0,0))
    else: screen.fill(BLACK)
#    screen.blit(star, (CENTER[0]-STAR_SIZE, CENTER[1]-STAR_SIZE))
    all_sprites.draw(screen)
    hud = HUD()
    screen.blit(hud, (0,0))

    # font.size = SCORE_SIZE
    # score_player1, score_player1_rect = font.render(str(SCORE[0]))
    # score_player2, score_player2_rect = font.render(str(SCORE[1]))
    # screen.blit(score_player1, SubCoords(SCORE1_POS, score_player1_rect.center))
    # screen.blit(score_player2, SubCoords(SCORE2_POS, score_player2_rect.center))
#    screen.blit(lamp_surf, (0,0))
#    screen.blit(score_player2, SCORE2_POS - score_player2_rect.center)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
