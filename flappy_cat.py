import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 900
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Cat')

font = pygame.font.SysFont('Bauhaus 93', 60)

#define colors
white = (255, 255, 255)

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 300
pipe_frequency = 1500 #ms
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

#load images
bg = pygame.image.load('img/bg1.gif')
bg = pygame.transform.scale(bg, (screen_width, screen_height))
button_image = pygame.image.load('img/restart.png')
button_image = pygame.transform.scale(button_image, (button_image.get_width()*2,button_image.get_height()*2))


ground_img = pygame.image.load('img/ground.png')
ground_height = 100
ground_img = pygame.transform.scale(ground_img, (screen_width+35, ground_height))

def draw_text(text, size, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img,(x,y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y=int(screen_height/2)
    flappy.index = 0
    flappy.counter = 0
    flappy.vel = 0
    flappy.image = flappy.images[0]
    score = 0
    flappy.image = flappy.images[0]
    return score

#Class for cat, which acts as the flying bird 
class Bird(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range (1,4):
            img = pygame.transform.scale(pygame.image.load(f'img/bird{num}.png'), (100, 100))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0

    def update(self):

        #gravity
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < screen_height - ground_height:
                self.rect.y += int(self.vel)
            else:
                self.rect.bottom = screen_height - ground_height
                self.vel = 0

        if game_over == False:
 
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel =-9
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #handle bird animation
            self.counter +=1
            flap_cooldown = 15

            if self.counter >=flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            #rotate the bird
        if flying == True:
            self.image = pygame.transform.rotate(self.images[self.index], self.vel*-3)
        else:
            self.image = self.images[self.index]

class Pipe(pygame.sprite.Sprite):
    def __init__(self,x,y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is top pipe, -1 is bottom pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x,y + int(pipe_gap/2)]
    
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    
    def draw(self):

        action = False

        #check if mouse is over the button
        pos = pygame.mouse.get_pos()

        #check if mouse hovers button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image,(self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height/2))

#restart button
#restart button
button_x = screen_width // 2 - button_image.get_width() // 2
button_y = screen_height // 2 - 100
button = Button(button_x, button_y, button_image)

bird_group.add(flappy)


run = True
while run:

    clock.tick(fps)

    #draw background
    screen.blit(bg,(0,0))

    #draw bird
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    
    #draw ground
    screen.blit(ground_img, (ground_scroll, screen_height - ground_height))
    
    #check score
    for pipe in pipe_group:
        if pipe.rect.bottom >= screen_height / 2:  # only consider bottom pipes
            if flappy.rect.left > pipe.rect.right and pass_pipe == False:
                score += 1
                pass_pipe = True
            if flappy.rect.left < pipe.rect.right:
                pass_pipe = False
            break  # Only check one pipe per frame

    
    draw_text(str(score),font, white, int(screen_width/2), 20)

    #collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    #check if bird has hit the ground
    if flappy.rect.bottom >= screen_height - ground_height:
        flying = False
        game_over = True
        flappy.vel = 0
  


    
    if game_over == False and flying == True:

        #generate pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)
                btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
                pipe_group.add(top_pipe)
                pipe_group.add(btm_pipe)
                last_pipe = time_now

        #draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll)>35:
            ground_scroll = 0

        pipe_group.update()

    
    #check for game over --> reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    

    pygame.display.update()

pygame.quit()
