import pygame
import neat
import time
import os
import random
pygame.font.init()

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

#Create fonts for the score
STAT_FONT = pygame.font.SysFont("comicsans", 50)

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

class Pipe:
    GAP = 200 #Space between pipes
    VEL = 5 #Moves the pipes backwards

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        #Gets image and keeps track of the pipes
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        #For collision
        self.passed = False
        self.set_height()

    def set_height(self):
        #Allows to see the tops of both facing pipes
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()

        self.bottom = self.height + self.GAP

    #Moves the pipes
    def move(self):
        self.x -= self.VEL

    #Draws pipe
    def draw(self, win):
        #Draws the top pipe
        win.blit(self.PIPE_TOP, (self.x, self.top))

        #Draws the bottom pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #Takes care of the collision for the bird and pipe
    def collide(self, bird):
        #Gets the masks of the bird and pipe
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        #Gets the offset
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #If no collision, then the function returns none
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        #Checks if b_point and t_point exist
        if t_point or b_point:
            return True

        return False

#Works with the base image
class Base:
    VEL = 5 #Same as pipe
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0 #x position 0
        self.x2 = self.WIDTH #x position after the first base image

    #Moves the base
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        #Cycles one image to the back like a circle of images
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    #Draws the base image
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

#Draws the window
def draw_window(win, bird, pipes, base, score):
    #Draws bird on window and updates the display
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    #Draws the score
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    bird.draw(win)
    pygame.display.update()

#Runs the main loop of the game 
def main():
    #Set up
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)] #Change to move the pipes closer
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    #Allows the game to be stopped if need be
    run = True

    #Main game loop
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #bird.move() <---- Uncomment to test the bird

        add_pipe = False
        rem = []
        for pipe in pipes:
            #Checks pipe bird collision
            if pipe.collide(bird):
                pass

            #Checks if the pipe is off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            #Checks if the bird has passed the pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            #Moves pipes
            pipe.move()

        #Adds a new pip
        if add_pipe:
            score += 1
            pipes.append(Pipe(600)) #Change to move the pipes closer

        #Removes pipes
        for r in rem:
            pipes.remove(r)
        
        #Checking if the bird has hit the ground
        if bird.y + bird.img.get_height() >= 730:
            pass

        #Moves base
        base.move()

        #Draws everything
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()

main()