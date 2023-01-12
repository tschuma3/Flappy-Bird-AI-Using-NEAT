import pygame
import neat
import time
import os
import random

"""
NEAT
    -- Visualize the design for the game and network
"""

#Get the window width and height
WIN_WIDTH = 500
WIN_HEIGHT = 800

#Gets the images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bg.png")))

#The bird class
class Bird:
    IMGS = BIRD_IMGS #Gets the image
    MAX_ROTATION = 25 #How much the bird will tilt up or down
    ROT_VEL = 20 #How much the bird will rotate
    ANIMATION_TIME = 5 #How long to show the bird animation, how fast or slow the bird flaps it's wings

    def __init__(self, x, y):
        #The starting position of the bird
        self.x = x
        self.y = y
        
        self.tilt = 0
        self.tick_count = 0 #Helps with the physics of the bird going up and down
        self.vel = 0 #Velocity
        self.height = self.y
        self.img_count = 0 #Helps with animations 
        self.img = self.IMGS[0]

    #Works on the jump of the bird
    def jump(self):
        self.vel = 10.5
        self.tick_count = 0 #Keeps track of when the bird lasts jump
        self.height = self.y #Where the bird jumped from

    #Works on the movement of the bird
    def move(self):
        self.tick_count += 1 

        #How many pixels the bird moves
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        #Checks and sets a terminal velocity
        if d >= 16:
            d = 16
        
        #Helps fine tunes movenment
        if d < 0:
            d -= 2

        #Changes the y by the displacement
        self.y = self.y + d

        #Now tilts the bird
        #Keeps track of where the birds position is
        if d < 0 or self.y < self.height + 50:
            #Makes sure we keep the bird from not tilting too far
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            #Makes sure we keep the bird from not tilting too far
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    #Draws the bird
    def draw(self, win):
        self.img_count += 1 #How many ticks an image has been shown

        #Displays the image based on the image count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #Checks for the 90 degree tilt and wont flap wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        #Rotates the image around it's center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    #This gets the collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

#Draws the window
def draw_window(win, bird):
    #Draws bird on window and updates the display
    win.blit(BG_IMG, (0,0))
    bird.draw(win)
    pygame.display.update()

#Runs the main loop of the game 
def main():
    #Bird object, window, and clock
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    #Allows the game to be stopped if need be
    run = True

    #Main game loop
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #Moves and draws the bird 
        #bird.move()
        draw_window(win, bird)

    pygame.quit()
    quit()

main()