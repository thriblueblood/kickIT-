import sys
import smbus
import math
import time
import pygame
import os
from os import path
from pygame import mixer
import RPi.GPIO as GPIO
import tm1637
diry = path.join(path.dirname(__file__))

#TM1637
tm = tm1637.TM1637(23,24,tm1637.BRIGHT_TYPICAL)
tm.Clear()
tm.SetBrightnes(5)

highscore = 0
WIDTH = 600
HEIGHT = 600
FPS = 30

#Initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Kick IT!")
clock = pygame.time.Clock()
HS_FILE = "highscore.txt"

#Define Colors
white = (255,255,255)
yellow = (255, 255, 0)
black = (0,0,0)

#MPU6050
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command
        # Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

#Game
def load_data():
    with open(path.join(diry,HS_FILE), 'r') as f:
        try:
            data = f.read()
            
            #highscore = int(f.read())
        except:
            highscore = 0
    return data

            
def input_name():
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    font = pygame.font.Font("8-BIT WONDER.TTF", 35)
    clock = pygame.time.Clock()
    
    input_box = pygame.Rect(180, 100, 140, 50)
    color_inactive = pygame.Color("green")
    color_active = pygame.Color('yellow')
    color = color_inactive
    active = False
    global name
    name = ''
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        gameplay()
                        print(name)
                        name = ''
                    elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                    else:
                        if len(name)<=4:
                            name += event.unicode

        screen.blit(name_menu,(0,0))
##        screen.fill((30,30,30))                    
        # Render the current text.
        txt_surface = font.render(name, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+10, input_box.y+10))
        # Blit the input_box rect.
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(FPS)

def gameplay():
    active = True
    global highscore
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        text_name = text_format(name,font,40,yellow)
        for i in range(3, 0, -1):
            number = text_format(str(i),font,100,yellow)
            if (i ==1):
                os.system("sudo ./RED_LED_OFF")
                os.system("sudo ./YELLOW_LED_ON")
            screen.blit(gameplay_dark,(0,0))
            screen.blit(number,(WIDTH/4+120,200))
            pygame.display.flip()
            time.sleep(1)
        os.system("sudo ./YELLOW_LED_OFF")
        os.system("sudo ./GREEN_LED_ON")

        screen.blit(gameplay_menu,(0,0))
        screen.blit(text_name,(210,10))
        
        pygame.display.flip()
        
        
        #Score             
        t_future = time.time()+5
        acc_list = []
        while time.time() < t_future:
            screen.blit(shoot_logo,(WIDTH/4+30,HEIGHT/2+80))
            pygame.display.flip()
            accel_xout = read_word_2c(0x3b)
            accel_yout = read_word_2c(0x3d)
            accel_zout = read_word_2c(0x3f)
            acc = (((accel_xout)**2+(accel_yout)**2+(accel_zout)**2)**0.5)
            acc_list.append(int(acc//75))
        os.system("sudo ./GREEN_LED_OFF")
        max_acc = max(acc_list)
        show_max = [int(max_acc//1000),int(max_acc//100),int(max_acc//10%10),int(max_acc%10)]
        if(max_acc < 250):
            error_text = text_format("ERROR",font,100,white)
            screen.blit(gameplay_dark,(0,0))
            screen.blit(error_text,(60,200))
            pygame.display.flip()
            time.sleep(5)
            os.system("sudo ./RED_LED_ON")
            gameplay()
            
        for i in range(int(max_acc)+1):
            screen.blit(gameplay_menu,(0,0))
            screen.blit(text_name,(210,10))
            score_name = text_format(str(i),font,100,yellow)
            screen.blit(score_name,(WIDTH/4+15,230))
            show_max = [int(i//1000),int(i//100),int(i//10%10),int(i%10)]
            tm.Show(show_max)
            pygame.display.update()
            pygame.display.flip()
            time.sleep(0.005)
        time.sleep(0.5)
        
        for i in range(4):
            screen.blit(gameplay_menu,(0,0))
            screen.blit(text_name,(210,10))
            score_name = text_format(str(int(max_acc)),font,100,yellow)
            tm.Clear()
            pygame.display.update()
            pygame.display.flip()
            time.sleep(0.5)
            screen.blit(gameplay_menu,(0,0))
            screen.blit(text_name,(210,10))
            screen.blit(score_name,(WIDTH/4+15,230))
            tm.Show(show_max)
            pygame.display.flip()
            time.sleep(0.5)

        print(max_acc, highscore)
        score1= text_format(str(int(max_acc)),font,50,white)
        return_text = text_format(("Press any key to continue"),font,20,white)
        if (max_acc > int(highscore)):
            highscore = max_acc
            with open(HS_FILE, 'w') as f:
                print(max_acc)
                f.write(str(max_acc) + " " + str(name))
                f.close()
            not_pressed = True
            while not_pressed:
                screen.blit(gameplay_dark,(0,0))
                screen.blit(text_name,(210,10))
                screen.blit(highscore_screen,(0,0))
                screen.blit(score1,(340,350))
                screen.blit(return_text,(70,450))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        main_menu()

        not_pressed = True
        while not_pressed:
            screen.blit(gameplay_dark,(0,0))
            screen.blit(text_name,(210,10))
            screen.blit(result_screen,(0,0))
            screen.blit(score1,(340,350))
            screen.blit(return_text,(70,450))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    not_pressed = False
            
        
        
        main_menu()
    
def text_format(message, textFont, textSize, textColor):
    newFont = pygame.font.Font(textFont, textSize)
    newText = newFont.render(message,0,textColor)
    return newText
font = "8-BIT WONDER.TTF"


#Load game sprites
main_menuBG = pygame.image.load(path.join(diry, "kickIT.png")).convert()
name_menu = pygame.image.load(path.join(diry, "select_name.png")).convert()
gameplay_menu = pygame.image.load(path.join(diry, "gameplay.png")).convert()
gameplay_dark = pygame.image.load(path.join(diry,"gameplay_dark.png")).convert()
shoot_logo = pygame.image.load(path.join(diry,"shoot.png"))
result_screen = pygame.image.load(path.join(diry,"nt.png"))
highscore_screen = pygame.image.load(path.join(diry,"result.png"))


#Load sounds
move_menu = pygame.mixer.Sound("move.wav")
pygame.mixer.music.load("theme.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

#Game loop
def main_menu():
    tm.Clear()
    running = True
    selected = "start"
    data = load_data()
    global highscore
    global name
    highscore, name = data.split(' ')
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_UP:
                        move_menu.play()
                        selected="start"
                    elif event.key==pygame.K_DOWN:
                        move_menu.play()
                        selected="quit"
                    if event.key==pygame.K_RETURN:
                        if selected=="start":
                            print("Start")
                            input_name()
                        if selected=="quit":
                            pygame.quit()
                            quit()

        screen.blit(main_menuBG,(0,0))
        if selected == "start":
            text_start= text_format("START", font, 75, yellow)
        else:
            text_start= text_format("START", font, 75, white)

        if selected == "quit":
            text_quit= text_format("QUIT", font, 75, yellow)
        else:
            text_quit= text_format("QUIT", font, 75, white)
        os.system("sudo ./GREEN_LED_OFF")
        os.system("sudo ./RED_LED_ON")
        text_highscore = text_format("HighScore is "+str(highscore) +" BY " + str(name),font,10,white)
        screen.blit(text_highscore,(10,10))
        screen.blit(text_start, (120, 300))
        screen.blit(text_quit, (180, 380))
        pygame.display.update()
        clock.tick(FPS)

main_menu()
pygame.quit()