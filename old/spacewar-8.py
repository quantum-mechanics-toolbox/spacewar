#!/usr/bin/env python3

import pygame
import pygame.freetype
from operator import add, sub
import random
import math
import os
import time
import board
import digitalio
import busio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import colorsys

#%% Hardware Setup

# Try to create a Digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")


# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
chan2 = AnalogIn(mcp, MCP.P2)
chan3 = AnalogIn(mcp, MCP.P3)
chan4 = AnalogIn(mcp, MCP.P4)
chan5 = AnalogIn(mcp, MCP.P5)

KNOB_NOISE = 577 
#MAX_ABS = 0
#print(KNOB_NOISE)

#%% Settings

WIDTH = 1280
HEIGHT = 800
ASPECT = float(WIDTH)/HEIGHT
RADIUS = 420
FPS = 60
CENTER = (WIDTH/2, HEIGHT/2)
#SHIP_NUM = 20
SHIP_SIZE = 1

BG_STARS = 60
START_SPEED = 1.0
MAX_SPEED = 20.0
FADE = True
#FADE_PARAM = 8

FRAGMENTS = 50

SCORE = [0,0]

FULL_SCREEN = False
SHOW_LABELS = False

SCORE_SIZE = 60
LABEL_SIZE = 20
LAMP_SIZE = 150

UI1_POS = (WIDTH*1.08/9, HEIGHT*1.5/10)
UI2_POS = (WIDTH*0.52/9, HEIGHT/2)
UI3_POS = (WIDTH*1.08/9, HEIGHT*8.5/10)
UI4_POS = (WIDTH*7.92/9, HEIGHT*1.5/10)
UI5_POS = (WIDTH*8.48/9, HEIGHT/2)
UI6_POS = (WIDTH*7.92/9, HEIGHT*8.5/10)

UI7_POS = (WIDTH*0.75/9, HEIGHT*1.2/6)
UI8_POS = (WIDTH*0.75/9, HEIGHT*1.4/6)
UI9_POS = (WIDTH*0.75/9, HEIGHT*1.6/6)
UI10_POS = (WIDTH*0.75/9, HEIGHT*1.8/6)
UI11_POS = (WIDTH*0.75/9, HEIGHT*2.0/6)
UI12_POS = (WIDTH*0.75/9, HEIGHT*2.2/6)

UI13_POS = (WIDTH*8.2/9, HEIGHT*1.2/6)
UI14_POS = (WIDTH*8.2/9, HEIGHT*1.4/6)
UI15_POS = (WIDTH*8.2/9, HEIGHT*1.6/6)
UI16_POS = (WIDTH*8.2/9, HEIGHT*1.8/6)
UI17_POS = (WIDTH*8.2/9, HEIGHT*2.0/6)
UI18_POS = (WIDTH*8.2/9, HEIGHT*2.2/6)

UI19_POS = (WIDTH/2, HEIGHT*1/4)

control_label_pos = []
control_label_pos.append((UI19_POS[0]-200,UI19_POS[1]-(3*LABEL_SIZE)))
control_label_pos.append((UI19_POS[0],UI19_POS[1]-(3*LABEL_SIZE)))
control_label_pos.append((UI19_POS[0]+200,UI19_POS[1]-(3*LABEL_SIZE)))
control_label_pos.append((UI19_POS[0]-200,UI19_POS[1]+(4*LABEL_SIZE)))
control_label_pos.append((UI19_POS[0],UI19_POS[1]+(4*LABEL_SIZE)))
control_label_pos.append((UI19_POS[0]+200,UI19_POS[1]+(4*LABEL_SIZE)))



# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0) # HLS = 0.333, 0.5, 1.0
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255,127,0) # HLS = 0.0830, 0.5, 1.0
MONO_COLOR = ORANGE 
DIM_COLOR = (0, 128, 0)
OFF_COLOR = (0, 64, 0)
#COLOR1 = CYAN
COLOR1 = GREEN
COLOR2 = GREEN

settings = {"mode": "menu",
            "game": "1962",
            "gravity": 80, #80
            "sun_size": 50, #50
            "bullet_cool": 1.0, #1.0
            "hyper_cool": 0.1, #10.0
            "bullet_speed": 2.0,
            "frag_decay": 50, #50
            "fade_param": 8,
            "mono_hue": 0.333,
            "mono_lum": 0.5,
            "mono_sat": 1.0,
            "p1_hue": 0.333,
            "p1_lum": 0.5,
            "p1_sat": 1.0,
            "p2_hue": 0.333,
            "p2_lum": 0.5,
            "p2_sat": 1.0
            }



# initialize pygame and create window
random.seed()
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20,20)
pygame.init()
pygame.mixer.init()
#pygame.freetype.init()

if FULL_SCREEN:
    display_flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((WIDTH, HEIGHT), display_flags)
#      screen = pygame.display.set_mode((0,0), display_flags)
#    print (screen.get_size())
else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spacewar!")
clock = pygame.time.Clock()
#print(pygame.freetype.get_default_font())
#font = pygame.freetype.Font("./fonts/OSCILLOS.TTF")
font = pygame.freetype.Font("./fonts/Oscilloscope6.ttf")
font.fgcolor = MONO_COLOR
font.size = LABEL_SIZE

template = pygame.image.load("references/Lens_Template.png")
template = pygame.transform.scale(template, (WIDTH, HEIGHT))

#%% Control Setup

class control():
    def __init__(self, channel, scale, control, minval, maxval, settings):
        if channel == 0:
            self.channel = AnalogIn(mcp, MCP.P0)
        if channel == 1:
            self.channel = AnalogIn(mcp, MCP.P1)
        if channel == 2:
            self.channel = AnalogIn(mcp, MCP.P2)
        if channel == 3:
            self.channel = AnalogIn(mcp, MCP.P3)
        if channel == 4:
            self.channel = AnalogIn(mcp, MCP.P4)
        if channel == 5:
            self.channel = AnalogIn(mcp, MCP.P5)
        self.lastvalue = self.channel.value
#        print (self.lastvalue)
        self.scale = scale
        self.control = control
        self.minval = minval
        self.maxval = maxval
        self.settings = settings
    
    def ReadControl(self):
        value = self.channel.value
#        global MAX_ABS
        if abs(value - self.lastvalue)>KNOB_NOISE:
#            new_abs = abs(value - self.lastvalue)
#            if new_abs > MAX_ABS:
#                MAX_ABS = new_abs
#                print(MAX_ABS)
            if self.scale == 'LIN':
                setting_value = self.minval + ((self.maxval-self.minval)*value/65535)
            if self.scale == 'LOG':
                setting_value = self.minval + ((self.maxval-self.minval)*pow(10, (4*value/65535))/10000)
            self.settings[self.control] = setting_value
            self.lastvalue = value
            return True
        self.lastvalue = value
        return False

control_gravity = control(0, 'LIN', 'gravity', 0.1, 800.0, settings)
control_sun_size = control(1, 'LIN', 'sun_size', 0.1, 0.7*RADIUS, settings)
control_frag_decay = control(2, 'LOG', 'frag_decay', 2, 1000.0, settings)
control_bullet_speed = control(3, 'LIN', 'bullet_speed', 1.0, 5.0, settings)
control_bullet_cool = control(4, 'LIN', 'bullet_cool', 0.1, 3.0, settings)
control_hyper_cool = control(5, 'LIN', 'hyper_cool', 0.1, 30.0, settings)

control_mono_hue = control(0, 'LIN', 'mono_hue', 0.0, 1.0, settings)
control_mono_sat = control(1, 'LIN', 'mono_sat', 0.0, 1.0, settings)
control_mono_lum = control(2, 'LIN', 'mono_lum', 0.0, 1.0, settings)
control_fade = control(3, 'LIN', 'fade_param', 1.0, 32.0, settings)

control_p_one_hue = control(0, 'LIN', 'p1_hue', 0.0, 1.0, settings)
control_p_one_sat = control(1, 'LIN', 'p1_sat', 0.0, 1.0, settings)
control_p_one_lum = control(2, 'LIN', 'p1_lum', 0.0, 1.0, settings)

control_p_two_hue = control(3, 'LIN', 'p2_hue', 0.0, 1.0, settings)
control_p_two_sat = control(4, 'LIN', 'p2_sat', 0.0, 1.0, settings)
control_p_two_lum = control(5, 'LIN', 'p2_lum', 0.0, 1.0, settings)

controls = []        
controls.append(control_gravity)
controls.append(control_sun_size)
controls.append(control_frag_decay)
controls.append(control_bullet_speed)
controls.append(control_bullet_cool)
controls.append(control_hyper_cool)
#controls.append(control_mono_hue)
#controls.append(control_mono_lum)
#controls.append(control_mono_sat)

#%% Menu Setup

class menu():
    def __init__(self, name, parent, settings, help_gfx):
        self.name = name
        self.parent = parent
        self.menu_items = []
        self.control_items = []
        self.select = 0
        self.settings = settings
        self.settings_hold = settings.copy()
        self.help_gfx=help_gfx
        
    def enter(self):
        self.settings_hold = self.settings.copy()
        
    def reset(self):
        for i in range(len(self.control_items)):
            key = self.control_items[i].control
            self.settings[key] = self.settings_hold[key] 
        
class menu_item():
    def __init__(self, name, itemtype, parent, key="", contents = []):
        self.name = name
        self.itemtype = itemtype
        self.contents = contents
        self.select = 0
        self.key = key
       
    def selected(self):
        global active_menu, settings
        if self.itemtype == "menu":
            active_menu = self.name
        if self.itemtype == "options":
            self.select += 1
            if self.select >= len(self.contents):
                self.select = 0
            settings[self.key] = self.contents[self.select]

active_menu = ""        
menus = {}

main_menu = menu("main_menu", "", settings, 0)
game_menu_item = menu_item("game_version", "options", "main_menu", "game", ['1962','2024'])
#game_menu_item.contents = ['1962', '2024']
main_menu.menu_items.append(game_menu_item)
system_menu_item = menu_item("system", "menu", "main_menu")
main_menu.menu_items.append(system_menu_item)
display_menu_item = menu_item("display", "menu", "main_menu")
main_menu.menu_items.append(display_menu_item)


ph_menu_item = menu_item("placeholder", "menu", "main_menu")

system_menu = menu("system", "main_menu", settings, 2)
system_menu.control_items = [control_gravity,
                             control_sun_size,
                             control_frag_decay,
                             control_bullet_speed,
                             control_bullet_cool,
                             control_hyper_cool]
#system_menu.menu_items.append(ph_menu_item)

display_menu = menu("display", "main_menu", settings, 1)
system_color_menu_item = menu_item("system_display", "menu", "display")
display_menu.menu_items.append(system_color_menu_item)
player_color_menu_item = menu_item("player_display", "menu", "display")
display_menu.menu_items.append(player_color_menu_item)

system_color_menu = menu("system_display", "display", settings, 2)
system_color_menu.control_items = [control_mono_hue,
                                 control_mono_sat,
                                 control_mono_lum,
                                 control_fade]

player_color_menu = menu("player_display", "display", settings, 2)
player_color_menu.control_items = [control_p_one_hue,
                                 control_p_one_sat,
                                 control_p_one_lum,
                                 control_p_two_hue,
                                 control_p_two_sat,
                                 control_p_two_lum]


    
active_menu = "main_menu"
menus[main_menu.name] = main_menu
menus[system_menu.name] = system_menu
menus[display_menu.name] = display_menu
menus[system_color_menu.name] = system_color_menu
menus[player_color_menu.name] = player_color_menu


#%% Generic Functions

def ran(number):
    return random.randrange(number)

def RandSign():
    return 1 if random.random() < 0.5 else -1

def SubCoords(a, b):
    return ((a[0]-b[0]),(a[1]-b[1]))

def AngleToCoords(theta, mag):
    theta = (6.2832/360)*theta
    MagX = mag*math.cos(theta)
    MagY = mag*math.sin(theta)
    return (MagX, MagY)

def CoordsToAngle(MagX, MagY):
    theta = (360.0/6.2832)*math.atan(MagY/MagX)
    if MagX<0:
        theta += 180.0
    if MagX>0 and MagY<0:
        theta += 360.0
    mag = VectMag((MagX, MagY))
    print("{:1f}\t{:1f}\t{:1f}\t{:1f}".format(MagX, MagY, theta, mag))
    return theta, mag

def SetColor():
    r_chan = ran(255)
    g_chan = ran(255)
    b_chan = ran(255)
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

def ColorMult(source, value):
  r = int(source[0] * value)
  g = int(source[1] * value)
  b = int(source[2] * value)
  if (len(source) == 3):
    return (r,g,b)
  if (len(source) == 4):
    return (r,g,b,source[3])

def VectSubtract(a, b):
  x = a[0] - b[0]
  y = a[1] - b[1]
  return (x,y)

def VectMag(a):
  mag = math.sqrt(a[0]**2 + a[1]**2)
  return mag 

#%% Player & Bullet

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
#        self.hyperspace = NUM_HYPERS
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
#        distance = random.randrange(int(2*STAR_SIZE), int(0.9*RADIUS))
#        distance = random.randrange(int(2*settings['sun_size']), int(0.9*RADIUS))
        distance = random.randrange(int(settings['sun_size'] + ((RADIUS-settings['sun_size'])/2)), int(0.99*RADIUS))
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
        global LastHyperTime1
        global LastHyperTime2
#        self.speedx = 0
#        self.speedy = 0
        if self.GetBoundary() > RADIUS:
            angle, pos = CoordsToAngle(self.locx-CENTER[0], self.locy-CENTER[1]) 
            angle -=180
            pos = 0.99*pos
            x,y = AngleToCoords(angle, pos)
            self.locx = CENTER[0] + x
            self.locy = CENTER[1] + y
            
            # self.locx = WIDTH - self.locx
            # self.locy = HEIGHT - self.locy
            # if (self.speedx < 1.0) and (self.speedx > -1.0) and (self.speedy < 1.0) and (self.speedy > -1.0):
            #     self.locx = self.locx + (10.0*self.speedx)
            #     self.locy = self.locy + (10.0*self.speedy)

#            self.locx = WIDTH - self.locx + (4.0*self.speedx)
#            self.locy = HEIGHT - self.locy + (4.0*self.speedy)
#            self.locx = WIDTH - self.locx
#            self.locy = HEIGHT - self.locy
#            self.locx += self.speedx
#            self.locy += self.speedy
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
                if (time.time() > (LastHyperTime1 + settings['hyper_cool'])):
                    self.NewPos()
                    self.NewSpeed()
                    LastHyperTime1 = time.time()
#                if self.hyperspace>0:
#                    self.hyperspace -=1
#                    self.NewPos()
#                    self.NewSpeed()
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
                if (time.time() > (LastHyperTime2 + settings['hyper_cool'])):
                    self.NewPos()
                    self.NewSpeed()
                    LastHyperTime2 = time.time()
#                if self.hyperspace>0:
#                    self.hyperspace -=1
#                    self.NewPos()
#                    self.NewSpeed()
#        if (self.GetDistance()==0):
#            self.NewPos()
#            self.NewSpeed()
#        if (self.GetDistance()<STAR_SIZE):
#            self.NewPos()
#            self.NewSpeed()
#            self.kill()
#        self.speedx -= G*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
#        self.speedy -= G*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
        self.speedx -= settings['gravity']*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
        self.speedy -= settings['gravity']*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
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
#        thrust = AngleToCoords(self.rot, -2.0)
        thrust = AngleToCoords(self.rot, -1.0*settings['bullet_speed'])
#        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[0], self.speedy+thrust[1])
#        bullet = Bullet(self.rect.centerx, self.rect.centery, self.speedx+thrust[1], self.speedy+thrust[0])
#        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0], self.color)
#        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0], YELLOW)
        bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[1], thrust[0], MONO_COLOR)
        all_sprites.add(bullet)
        if self.playernum==1: bullets1.add(bullet)
        elif self.playernum==2: bullets2.add(bullet)

    def Explode(self):
        for frag in range(1, FRAGMENTS):
            thrust = AngleToCoords(random.randrange(1,360), random.randrange(1,5))
#"""static location"""
#            bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[0], thrust[1], self.color, random.randrange(settings['frag_decay']/2,settings['frag_decay']))
#"""ship velocity location"""
            bullet = Bullet(self.rect.centerx, self.rect.centery, thrust[0]+self.speedx, thrust[1]+self.speedy, self.color, random.randrange(int(settings['frag_decay']/2),int(settings['frag_decay'])))
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
#        if (self.GetDistance() < STAR_SIZE):
        if (self.GetDistance() < settings['sun_size']):
            self.kill()
#            print(SCORE, len(all_sprites))
#        self.speedx -= BULLET_G*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
#        self.speedy -= BULLET_G*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
        self.speedx -= settings['gravity']*(self.rect.centerx - CENTER[0])/pow(self.GetDistance(), 3)
        self.speedy -= settings['gravity']*(self.rect.centery - CENTER[1])/pow(self.GetDistance(), 3)
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

#%% Graphics

def SetColor(settings):
    global MONO_COLOR, DIM_COLOR, OFF_COLOR, COLOR1, COLOR2
    RGB = colorsys.hls_to_rgb(settings['mono_hue'], settings['mono_lum'], settings['mono_sat'])    
    MONO_COLOR = (RGB[0]*255, RGB[1]*255, RGB[2]*255) 
    DIM_COLOR = ColorMult(MONO_COLOR, 0.5)
    OFF_COLOR = ColorMult(MONO_COLOR, 0.25)
    RGB = colorsys.hls_to_rgb(settings['p1_hue'], settings['p1_lum'], settings['p1_sat'])    
    COLOR1 = (RGB[0]*255, RGB[1]*255, RGB[2]*255) 
    RGB = colorsys.hls_to_rgb(settings['p2_hue'], settings['p2_lum'], settings['p2_sat'])    
    COLOR2 = (RGB[0]*255, RGB[1]*255, RGB[2]*255) 

def Background():
    background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
#    pygame.draw.rect(background, (0,0,0,255), background.get_rect())
    pygame.draw.circle(background, (0,0,0,0), CENTER, RADIUS)
    pygame.draw.circle(background, MONO_COLOR, CENTER, RADIUS, 1)
### STARFIELD
    for star in range(BG_STARS):
        size = random.randrange(1,3)
        angle = random.random()*360
#        distance = random.randrange(STAR_SIZE, int(0.9*RADIUS))
        distance = random.randrange(int(settings['sun_size']), int(0.9*RADIUS))
        position = (CENTER[0] + AngleToCoords(angle, distance)[0], CENTER[1] + AngleToCoords(angle, distance)[1])
        pygame.draw.circle(background, MONO_COLOR, position, size)
### Milky Way
    milky_color = ColorMult(MONO_COLOR, 0.5)
#    print(milky_color)
#    milky_color = MONO_COLOR
#    print(milky_color)
    for star in range(40*BG_STARS):
        slope = 0.5
        spread = 0.3
        x = random.randrange(int(CENTER[0] - RADIUS), int(CENTER[0] + RADIUS)) 
#        y = (x*slope) + random.randrange(-1*RADIUS*spread, RADIUS*spread)
        y = int((x-CENTER[0])*slope) + CENTER[1]
        y += int(RADIUS*spread*(pow(2*random.random(),1.6)*RandSign()))
#        print(x,y)
        pygame.draw.circle(background, milky_color, (x,y), 1)
        
    return background.convert_alpha()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
#        self.image = pygame.Surface((STAR_SIZE*2,STAR_SIZE*2), pygame.SRCALPHA)
        self.image = pygame.Surface((settings['sun_size']*2,settings['sun_size']*2), pygame.SRCALPHA)
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
#        pygame.draw.circle(self.image, (0,0,0,1), (STAR_SIZE,STAR_SIZE), STAR_SIZE)
        pygame.draw.circle(self.image, (0,0,0,1), (settings['sun_size'],settings['sun_size']), settings['sun_size'])
        if pygame.time.get_ticks()%2 == 0:
#          pygame.draw.circle(self.image, MONO_COLOR, (STAR_SIZE,STAR_SIZE), random.random()*STAR_SIZE, 1)
#          pygame.draw.circle(self.image, MONO_COLOR, (settings['sun_size'],settings['sun_size']), random.random()*settings['sun_size'], 1)
          pygame.draw.circle(self.image, MONO_COLOR, (settings['sun_size'],settings['sun_size']), random.random()*settings['sun_size'], int(settings['sun_size']/50))
#          pygame.draw.circle(self.image, MONO_COLOR, (settings['sun_size'],settings['sun_size']), random.random()*settings['sun_size'], int(settings['sun_size']*settings['sun_size']/50/50))

def HelpFrames():
#    help_frame = pygame.Surface((WIDTH/2, HEIGHT/6), pygame.SRCALPHA)
    help_frames = []
    spacing = 100
    margin = 20
    HELP_COLOR = MONO_COLOR
    font.size = LABEL_SIZE
    font.fgcolor = HELP_COLOR
#    help_frame_rect = help_frame.get_rect()
#    pygame.draw.rect(help_frame, MONO_COLOR, help_frame_rect, 1) 

    labels = ['UP', 'DOWN', 'SELECT', 'BACK', 'RESET']

    help_frame = pygame.Surface((spacing*5, (font.size*1.25)+72), pygame.SRCALPHA)
    for i in range(5):
        if i<3:
            COLOR = MONO_COLOR
        else:
            COLOR = DIM_COLOR
        font.fgcolor = COLOR
        pygame.draw.rect(help_frame, (0,0,0), (margin+(i*spacing),(font.size*1.25),52,72))
        pygame.draw.rect(help_frame, COLOR, (margin+(i*spacing),(font.size*1.25),52,72), 3)
        pygame.draw.rect(help_frame, COLOR, (6 + margin+(i*spacing),6+(font.size*1.25),40,60), 3)
        label_text = "{}".format(labels[i])
        label,label_rect = font.render(label_text)
        label.set_alpha()
        help_frame.blit(label, SubCoords((margin + 27 + (i*spacing), LABEL_SIZE), label_rect.center))
    help_frames.append(help_frame)

    help_frame = pygame.Surface((spacing*5, (font.size*1.25)+72), pygame.SRCALPHA)
    for i in range(5):
        if i<4:
            COLOR = MONO_COLOR
        else:
            COLOR = DIM_COLOR
        font.fgcolor = COLOR
        pygame.draw.rect(help_frame, (0,0,0), (margin+(i*spacing),(font.size*1.25),52,72))
        pygame.draw.rect(help_frame, COLOR, (margin+(i*spacing),(font.size*1.25),52,72), 3)
        pygame.draw.rect(help_frame, COLOR, (6 + margin+(i*spacing),6+(font.size*1.25),40,60), 3)
        label_text = "{}".format(labels[i])
        label,label_rect = font.render(label_text)
        label.set_alpha()
        help_frame.blit(label, SubCoords((margin + 27 + (i*spacing), LABEL_SIZE), label_rect.center))
    help_frames.append(help_frame)

    help_frame = pygame.Surface((spacing*5, (font.size*1.25)+72), pygame.SRCALPHA)
    font.fgcolor = HELP_COLOR
    for i in range(5):
        pygame.draw.rect(help_frame, (0,0,0), (margin+(i*spacing),(font.size*1.25),52,72))
        pygame.draw.rect(help_frame, HELP_COLOR, (margin+(i*spacing),(font.size*1.25),52,72), 3)
        pygame.draw.rect(help_frame, HELP_COLOR, (6 + margin+(i*spacing),6+(font.size*1.25),40,60), 3)
        label_text = "{}".format(labels[i])
        label,label_rect = font.render(label_text)
        label.set_alpha()
        help_frame.blit(label, SubCoords((margin + 27 + (i*spacing), LABEL_SIZE), label_rect.center))
    help_frames.append(help_frame)

    return help_frames

def Knob():
    knob = pygame.Surface((40,40), pygame.SRCALPHA)
    pygame.draw.circle(knob, (0,0,0), (20,20), 20)
    pygame.draw.circle(knob, MONO_COLOR, (20,20), 20, 3)
    pygame.draw.rect(knob, MONO_COLOR, (19,0,3,15), 3)
    return knob

def LampSurfs(color):    
    lamp_surf = pygame.image.load("./gfx/lamp.png")
    lamp_surf = lamp_surf.convert_alpha()
    lamp_surf = pygame.transform.scale(lamp_surf, (LAMP_SIZE, LAMP_SIZE))

### Player Lamp
    lamp_surf_player = lamp_surf.copy()
    for x in range(0, lamp_surf.get_width()):
      for y in range(0, lamp_surf.get_height()):
        lamp_surf_player.set_at((x,y), ColorTint(lamp_surf.get_at((x,y)), color))

    levels = []
    for i in range(20):
      levels.append(int(20*i/19))
    levels[18] = levels[17]
    lamp_surfs_player = []
    for surfs in range(20):
      sub_lamp_surf_player = lamp_surf_player.copy()
      for x in range(0, sub_lamp_surf_player.get_width()):
        for y in range(0, sub_lamp_surf_player.get_height()):
          sub_lamp_surf_player.set_at((x,y), ColorSubtract(sub_lamp_surf_player.get_at((x,y)), int(255*((20.0-levels[surfs])/20.0))))
      lamp_surfs_player.append(sub_lamp_surf_player.convert())
    return lamp_surfs_player

# def LampSurfsPlayer2():    
#     lamp_surf = pygame.image.load("./gfx/lamp.png")
#     lamp_surf = lamp_surf.convert_alpha()
#     lamp_surf = pygame.transform.scale(lamp_surf, (LAMP_SIZE, LAMP_SIZE))

# ### Player 2 Lamp
#     lamp_surf_player2 = lamp_surf.copy()
#     for x in range(0, lamp_surf.get_width()):
#       for y in range(0, lamp_surf.get_height()):
#         lamp_surf_player2.set_at((x,y), ColorTint(lamp_surf.get_at((x,y)), COLOR2))

#     levels = []
#     for i in range(20):
#       levels.append(int(20*i/19))
#     levels[18] = levels[17]
# #    print(levels)
# #    for surfs in range(20):
# #      print(((20.0-levels[surfs])/20.0))
#     lamp_surfs_player1 = []
#     lamp_surfs_player2 = []
#     for surfs in range(20):
#       sub_lamp_surf_player1 = lamp_surf_player1.copy()
#       sub_lamp_surf_player2 = lamp_surf_player2.copy()
#       for x in range(0, sub_lamp_surf_player1.get_width()):
#         for y in range(0, sub_lamp_surf_player1.get_height()):
#           sub_lamp_surf_player1.set_at((x,y), ColorSubtract(sub_lamp_surf_player1.get_at((x,y)), int(255*((20.0-levels[surfs])/20.0))))
#           sub_lamp_surf_player2.set_at((x,y), ColorSubtract(sub_lamp_surf_player2.get_at((x,y)), int(255*((20.0-levels[surfs])/20.0))))
#       lamp_surfs_player1.append(sub_lamp_surf_player1.convert())
#       lamp_surfs_player2.append(sub_lamp_surf_player2.convert())
#     return lamp_surfs_player1, lamp_surfs_player2


def CreateElements():
    background = Background()
    help_frames = HelpFrames()
    # help_frame_0 = HelpFrame0()
    # help_frame_1 = HelpFrame1()
    # help_frame_2 = HelpFrame2()
    knob = Knob()
    lamp_surfs_player1 = LampSurfs(COLOR1)
    lamp_surfs_player2 = LampSurfs(COLOR2)    
    return lamp_surfs_player1, lamp_surfs_player2, background, help_frames, knob

def HUD(screen):

    global last_fps, last_tick

    font.size = SCORE_SIZE
    font.fgcolor = MONO_COLOR

#    score_player1, score_player1_rect = font.render(str(SCORE[0]))
    score_player1, score_player1_rect = font.render("{:02d}".format(SCORE[0]))
    score_player2, score_player2_rect = font.render("{:02d}".format(SCORE[1]))
    screen.blit(score_player1, SubCoords(UI1_POS, score_player1_rect.center))
#    screen.blit(score_player2, SubCoords(UI4_POS, score_player2_rect.center))
#    screen.blit(score_player1, UI1_POS)
    screen.blit(score_player2, SubCoords(UI4_POS, score_player2_rect.center))

    hyper_lamp_scale_1 = float(time.time() - LastHyperTime1)/settings['hyper_cool']
    if hyper_lamp_scale_1>1.0: hyper_lamp_scale_1 = 1.0
    index = int(19*hyper_lamp_scale_1)
    screen.blit(lamp_surfs_player1[index], SubCoords(UI2_POS, lamp_surfs_player1[index].get_rect().center))

    bullet_lamp_scale_1 = float(time.time() - LastBulletTime1)/settings['bullet_cool']
    if bullet_lamp_scale_1>1.0: bullet_lamp_scale_1 = 1.0
    index = int(19*bullet_lamp_scale_1)
    screen.blit(lamp_surfs_player1[index], SubCoords(UI3_POS, lamp_surfs_player1[index].get_rect().center))

    hyper_lamp_scale_2 = float(time.time() - LastHyperTime2)/settings['hyper_cool']
    if hyper_lamp_scale_2>1.0: hyper_lamp_scale_2 = 1.0
    index = int(19*hyper_lamp_scale_2)
    screen.blit(lamp_surfs_player2[index], SubCoords(UI5_POS, lamp_surfs_player2[index].get_rect().center))

    bullet_lamp_scale_2 = float(time.time() - LastBulletTime2)/settings['bullet_cool']
    if bullet_lamp_scale_2>1.0: bullet_lamp_scale_2 = 1.0
    index = int(19*bullet_lamp_scale_2)
    screen.blit(lamp_surfs_player2[index], SubCoords(UI6_POS, lamp_surfs_player2[index].get_rect().center))

    font.size = LABEL_SIZE

#    fps = int(1000.0/clock.tick())
    fps = int(1000.0/last_tick)
    fps = int(((29*last_fps) + fps)/30)
    last_fps = fps
    fps_text = "FPS: {:d}".format(fps)
    fps_label, fps_label_rect = font.render(fps_text)
    screen.blit(fps_label, SubCoords(UI7_POS, fps_label_rect.center))

    if SHOW_LABELS:
    #    screen.blit(score_player1, (-score_player1_rect[0]/2,-score_player1_rect[1]/2))
    
        sprites_text = "Sprites = {:d}".format(len(all_sprites))
        sprites_label, sprites_label_rect = font.render(sprites_text)
    
        speed_text = "{:.2f}, {:.2f}".format(player1.speedx, player1.speedy)
        speed_label, speed_label_rect = font.render(speed_text)
        
        p1x = player1.locx-CENTER[0]
        p1y = player1.locy-CENTER[1]
        p1a, p1m = CoordsToAngle(p1x, p1y)
        pos_text1 = "{:.1f},{:.1f}".format(p1x, p1y)
        pos_label1, pos_label_rect1 = font.render(pos_text1)
        pos_text2 = "{:.1f},{:.1f}".format(p1a, p1m)
        pos_label2, pos_label_rect2 = font.render(pos_text2)
    
        font.size = int(LABEL_SIZE*0.8)
        gravity_text = "gravity = {:.1f}".format(settings['gravity'])
        gravity_label, gravity_label_rect = font.render(gravity_text)
    
        sun_size_text = "sun size = {:.1f}".format(settings['sun_size'])
        sun_size_label, sun_size_label_rect = font.render(sun_size_text)
    
        frag_decay_text = "frag decay = {:.1f}".format(settings['frag_decay'])
        frag_decay_label, frag_decay_label_rect = font.render(frag_decay_text)

        bullet_speed_text = "bullet speed = {:.1f}".format(settings['bullet_speed'])
        bullet_speed_label, bullet_speed_label_rect = font.render(bullet_speed_text)        
    
        bullet_cool_text = "bullet cooldown = {:.1f}".format(settings['bullet_cool'])
        bullet_cool_label, bullet_cool_label_rect = font.render(bullet_cool_text)
    
        hyper_cool_text = "hyper cooldown = {:.1f}".format(settings['hyper_cool'])
        hyper_cool_label, hyper_cool_label_rect = font.render(hyper_cool_text)
    
    #            "gravity": 80, #80
    #            "sun_size": 50, #50
    #            "bullet_cool": 1.0, #1.0
    #            "hyper_cool": 0.1, #10.0
    #            "bullet_speed": 1.0,
    #            "frag_decay": 50000, #50
    
    #    speed_label, speed_label_rect = font.render(str(int(player1.speedx)) + ", " + str(int(player1.speedy)))
        screen.blit(sprites_label, SubCoords(UI8_POS, sprites_label_rect.center))
        screen.blit(speed_label, SubCoords(UI9_POS, speed_label_rect.center))
        screen.blit(pos_label1, SubCoords(UI10_POS, pos_label_rect1.center))
        screen.blit(pos_label2, SubCoords(UI11_POS, pos_label_rect2.center))
    
        screen.blit(gravity_label, SubCoords(UI13_POS, gravity_label_rect.center))
        screen.blit(sun_size_label, SubCoords(UI14_POS, sun_size_label_rect.center))
        screen.blit(frag_decay_label, SubCoords(UI15_POS, frag_decay_label_rect.center))
        screen.blit(bullet_speed_label, SubCoords(UI16_POS, bullet_speed_label_rect.center))
        screen.blit(bullet_cool_label, SubCoords(UI17_POS, bullet_cool_label_rect.center))
        screen.blit(hyper_cool_label, SubCoords(UI18_POS, hyper_cool_label_rect.center))

### Show lens overlay
#    screen.blit(template, (0,0))

#%% Game Setup

SetColor(settings)

spawn_player1_event = pygame.USEREVENT + 1
spawn_player2_event = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_player1_event, 10, 1)
pygame.time.set_timer(spawn_player2_event, 10, 1)

all_sprites = pygame.sprite.Group()
bullets1 = pygame.sprite.Group()
bullets2 = pygame.sprite.Group()

star = Star()
all_sprites.add(star)
star_boundary = pygame.sprite.Group()
star_boundary.add(star)

lamp_surfs_player1, lamp_surfs_player2, background, help_frames, knob = CreateElements()

fade_fill = pygame.Surface((WIDTH, HEIGHT)).convert()
fade_fill.set_alpha(settings['fade_param'])
pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())
fade_fill.blit(background, (0,0))

LastBulletTime1 = time.time() - settings['bullet_cool']
LastBulletTime2 = time.time() - settings['bullet_cool']
LastHyperTime1 = time.time() - settings['hyper_cool']
LastHyperTime2 = time.time() - settings['hyper_cool']

last_fps = 0

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

#%% Menu Loop


while settings['mode'] == 'menu':
    last_tick = clock.tick()
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
### Up
            if (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
                menus[active_menu].select -= 1
                if menus[active_menu].select < 0:
                    menus[active_menu].select = len(menus[active_menu].menu_items)-1
### Down
            if (event.key == pygame.K_RIGHT) or (event.key == pygame.K_d):
                menus[active_menu].select += 1
                if menus[active_menu].select >= len(menus[active_menu].menu_items):
                    menus[active_menu].select = 0
### Back
            if (event.key == pygame.K_RSHIFT) or (event.key == pygame.K_c) or (event.key == pygame.K_f):
#                print("{} Parent: {}".format(active_menu, menus[active_menu].parent))
                if menus[active_menu].parent != "":
                    active_menu = menus[active_menu].parent
### Select
            if (event.key == pygame.K_UP) or (event.key == pygame.K_w):
                if len(menus[active_menu].menu_items) > 0:
                    menus[active_menu].menu_items[menus[active_menu].select].selected()
                    menus[active_menu].enter()
### Revert
            if (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
                menus[active_menu].reset()
                control_items = len(menus[active_menu].control_items)
                for i in range(control_items):
                    item = menus[active_menu].control_items[i]
                    if item.control == 'sun_size':
                        star.image = pygame.Surface((settings['sun_size']*2,settings['sun_size']*2), pygame.SRCALPHA)
                        star.rect = star.image.get_rect()
                        star.rect.centerx = star.locx
                        star.rect.centery = star.locy
                    if (item.control == 'mono_hue') or (item.control == 'mono_sat') or (item.control == 'mono_lum'):   
                        SetColor(settings)
                        font.fgcolor = MONO_COLOR
                        knob = Knob()
                        help_frames = HelpFrames()
                        background = Background()
                        pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())
                        fade_fill.blit(background, (0,0))
                    if item.control == 'fade_param':
                        fade_fill.set_alpha(settings['fade_param'])



        elif event.type == spawn_player1_event:
            all_sprites.add(player1)
        elif event.type == spawn_player2_event:
            all_sprites.add(player2)

    if player1.alive():
        if (pygame.sprite.spritecollide(player1, bullets2, True)):
            player1.Explode()
            SCORE[1] += 1
            pygame.time.set_timer(spawn_player1_event, 500, 1)
        if (pygame.sprite.spritecollide(player1, star_boundary, False)):
            player1.Explode()
            #if SCORE[0] > 0:
            #    SCORE[0] -= 1
            pygame.time.set_timer(spawn_player1_event, 500, 1)
    if player2.alive():
        if (pygame.sprite.spritecollide(player2, bullets1, True)):
            player2.Explode()
            SCORE[0] += 1
            pygame.time.set_timer(spawn_player2_event, 500, 1)
        if (pygame.sprite.spritecollide(player2, star_boundary, False)):
            player2.Explode()
            #if SCORE[1] > 0:
            #    SCORE[1] -= 1
            pygame.time.set_timer(spawn_player2_event, 500, 1)


    # Update
    all_sprites.update()

    # Draw / render
    if (FADE): screen.blit(fade_fill, (0,0))
    else: screen.fill(BLACK)

    all_sprites.draw(screen)

    HUD(screen)

### Display Menu Items
    font.size = LABEL_SIZE*2
    menu_items = len(menus[active_menu].menu_items)
    for i in range(menu_items):
        item = menus[active_menu].menu_items[i]
        if menus[active_menu].select == i:
            font.fgcolor = MONO_COLOR
        else:
            font.fgcolor = DIM_COLOR
        if item.itemtype == 'menu':
            label_text = "{}".format(item.name)
        elif item.itemtype == 'options':
            label_text = "{}: {}".format(item.name, item.contents[item.select])
        label,label_rect = font.render(label_text)
        label.set_alpha()
        screen.blit(label, SubCoords((UI19_POS[0],UI19_POS[1]+(i*2.5*LABEL_SIZE)) , label_rect.center))

### Display Control Items
    font.fgcolor = MONO_COLOR
    control_items = len(menus[active_menu].control_items)
    for i in range(control_items):
        item = menus[active_menu].control_items[i]
        if(item.ReadControl()):
            if item.control == 'sun_size':
                star.image = pygame.Surface((settings['sun_size']*2,settings['sun_size']*2), pygame.SRCALPHA)
                star.rect = star.image.get_rect()
                star.rect.centerx = star.locx
                star.rect.centery = star.locy
            if (item.control == 'mono_hue') or (item.control == 'mono_sat') or (item.control == 'mono_lum'):   
                SetColor(settings)
                #                RGB = colorsys.hls_to_rgb(settings['mono_hue'], settings['mono_lum'], settings['mono_sat'])    
#                MONO_COLOR = (RGB[0]*255, RGB[1]*255, RGB[2]*255) 
                font.fgcolor = MONO_COLOR
                knob = Knob()
                help_frames = HelpFrames()
                background = Background()
                pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())
                fade_fill.blit(background, (0,0))
            if (item.control == 'p1_hue') or (item.control == 'p1_sat') or (item.control == 'p1_lum'):   
                SetColor(settings)
                lamp_surfs_player1 = LampSurfs(COLOR1)
            if item.control == 'fade_param':
                fade_fill.set_alpha(settings['fade_param'])

        label_text = "{}".format(item.control.upper())
        font.size = LABEL_SIZE*1.1
        label,label_rect = font.render(label_text)
        label.set_alpha()
        screen.blit(label, SubCoords(control_label_pos[i] , label_rect.center))
        control_rot = 140 - (280*item.channel.value/65535)
        control_knob = pygame.transform.rotate(knob,control_rot)
        screen.blit(control_knob, SubCoords((control_label_pos[i][0], control_label_pos[i][1]-60), control_knob.get_rect().center))
        value_text = "{:.1f}".format(settings[item.control])
        font.size = LABEL_SIZE*2
        label,label_rect = font.render(value_text)
        label.set_alpha()
        screen.blit(label, SubCoords((control_label_pos[i][0], control_label_pos[i][1]+50), label_rect.center))

#            label_text = "{} = {:.1f}".format(c.control, settings[c.control]).upper()
    

### Help GFX
    screen.blit(help_frames[menus[active_menu].help_gfx], SubCoords((UI19_POS[0],UI19_POS[1]+(WIDTH/3)) , help_frames[menus[active_menu].help_gfx].get_rect().center))
    # if menus[active_menu].help_gfx == 0:
    #     screen.blit(help_frame_0, SubCoords((UI19_POS[0],UI19_POS[1]+(WIDTH/3)) , help_frame_0.get_rect().center))
    # elif menus[active_menu].help_gfx == 1:
    #     screen.blit(help_frame_1, SubCoords((UI19_POS[0],UI19_POS[1]+(WIDTH/3)) , help_frame_1.get_rect().center))
    # elif menus[active_menu].help_gfx == 2:
    #     screen.blit(help_frame_2, SubCoords((UI19_POS[0],UI19_POS[1]+(WIDTH/3)) , help_frame_2.get_rect().center))


# *after* drawing everything, flip the display
    pygame.display.flip()
    
#%% Game Loop

# Game loop
running = True
while running:
    # keep loop running at the right speed
#    last_tick = clock.tick(FPS)
    last_tick = clock.tick()
        # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == spawn_player1_event:
            all_sprites.add(player1)
        elif event.type == spawn_player2_event:
            all_sprites.add(player2)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            if (event.key == pygame.K_RSHIFT) or (event.key == pygame.K_c):
                if (time.time() > (LastBulletTime1 + settings['bullet_cool'])):
                    player1.shoot()
                    LastBulletTime1 = time.time()
            if event.key == pygame.K_f:
                if (time.time() > (LastBulletTime2 + settings['bullet_cool'])):
                    player2.shoot()
                    LastBulletTime2 = time.time()
    if player1.alive():
        if (pygame.sprite.spritecollide(player1, bullets2, True)):
            player1.Explode()
            SCORE[1] += 1
            pygame.time.set_timer(spawn_player1_event, 500, 1)
        if (pygame.sprite.spritecollide(player1, star_boundary, False)):
            player1.Explode()
            #if SCORE[0] > 0:
            #    SCORE[0] -= 1
            pygame.time.set_timer(spawn_player1_event, 500, 1)
    if player2.alive():
        if (pygame.sprite.spritecollide(player2, bullets1, True)):
            player2.Explode()
            SCORE[0] += 1
            pygame.time.set_timer(spawn_player2_event, 500, 1)
        if (pygame.sprite.spritecollide(player2, star_boundary, False)):
            player2.Explode()
            #if SCORE[1] > 0:
            #    SCORE[1] -= 1
            pygame.time.set_timer(spawn_player2_event, 500, 1)

    # Update
    all_sprites.update()

    # Draw / render
    if (FADE): screen.blit(fade_fill, (0,0))
    else: screen.fill(BLACK)
#    screen.blit(star, (CENTER[0]-STAR_SIZE, CENTER[1]-STAR_SIZE))
#    screen.blit(background, (0,0))
    all_sprites.draw(screen)

    HUD(screen)

    # Read Control Knobs
    font.size = LABEL_SIZE
    font.fgcolor = MONO_COLOR
    for c in controls:
        if (c.ReadControl()):
#            label_text = "{} = {:.1f}".format(c.control, settings[c.control]).upper()
            label_text = "{} = {:.1f}".format(c.control, settings[c.control])
            label,label_rect = font.render(label_text)
            label.set_alpha()
            screen.blit(label, SubCoords(UI19_POS, label_rect.center))
            if c.control == 'sun_size':
                star.image = pygame.Surface((settings['sun_size']*2,settings['sun_size']*2), pygame.SRCALPHA)
                star.rect = star.image.get_rect()
                star.rect.centerx = star.locx
                star.rect.centery = star.locy
            if (c.control == 'mono_hue') or (c.control == 'mono_sat') or (c.control == 'mono_lum'):   
                RGB = colorsys.hls_to_rgb(settings['mono_hue'], settings['mono_lum'], settings['mono_sat'])    
                MONO_COLOR = (RGB[0]*255, RGB[1]*255, RGB[2]*255) 
                font.fgcolor = MONO_COLOR
                background = Background()
                pygame.draw.rect(fade_fill, BLACK, fade_fill.get_rect())
                fade_fill.blit(background, (0,0))
#                lamp_surfs_player1, lamp_surfs_player2, background = CreateElements()

    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
