import pygame
import neat
import time
import os
import random
import pickle
pygame.font.init()

"""
Neuroevolution of Augmented Topologies (NEAT) 
    -- Visualize the design for the game and network
    -- Starts off with random movements and input values
    -- Uses Neural Networks
        -- Works in layers 
        -- Has an input layer and an output layer
    -- Make sure to load in the configuration file
    -- Flappy Bird with Neat
        -- Organized List
            -- Inputs --> Bird Y, Top Pipe, Bottom Pipe
            -- Outputs --> Jump? Do or Do not
            -- Activation Function --> TanH == Hyperbolic Tangent Funciton
                -- Could pick sigmoid etc...
            -- Population Size --> 100 Birds
                -- Could pick 10 or 1000, what suites the NEAT model
            -- Fitness Function --> Distance
                -- Think about how we can figure out which birds are the best
                -- Can tweek and influence birds to move further
            -- Max Generations --> 30 Generations
                -- Helps with making sure there is a perfect bird
        -- Input Layer (Eyes of the AI)
            -- Pieces of Information that are valuable
                -- 1. Position of the Bird
                -- 2. Position / Distance between the Bird and the Top / Bottom Pipe
        -- Determin whether the bird will jump or not jump
        -- Feeds values into each layer using weights and biases
        -- The math
            -- E = (By * W1) + (TP * W2) + (BP * W3) + B
                -- E == Weighted Sum
                -- By == Bird y position
                -- TP == Top pipe position
                -- BP == Bottom pipe position
                -- W1, W2, W3 == Weights of the 3 inputs
                -- B == bias
            -- Next is F(E)
                -- F == Activation function "TanH"
                    -- TanH == Squishes the value of the weighted sum to be inbetween -1 to 1
        -- NEAT wiil take care of weights and biases
        -- Steps
            -- 1. Create a population of birds that are completely random
                -- Each bird gets a neural network
                -- Each bird starts with random weights and biases
            -- 2. Test the birds and evaluate their fitness
                -- Fitness is different on every game
                -- For Flappy Bird, it is how far the bird progresses in the game
            -- 3. Once every bird has died
                -- Bread and mutate the for the next generation of bird
            -- 4. Rinse and Repeat until the desired result is acquired
    -- Will remove and add connections when going through the generations
    -- NEAT seperates the populations into species
        -- Species
            -- One can be birds have 2 hidden layers as well as 3 nodes and 1 output
            -- Another bird can have 3 nodes and 1 output
    --Fitness function
        -- Make sure to add "genomes" and "config" as parameters
"""

#Get the window width and height
WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

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
        self.vel = -10.5
        self.tick_count = 0 #Keeps track of when the bird lasts jump
        self.height = self.y #Where the bird jumped from

    #Works on the movement of the bird
    def move(self):
        self.tick_count += 1 

        #How many pixels the bird moves also known as displacement
        d = self.vel * (self.tick_count) + 0.5 * (3) * (self.tick_count) ** 2

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
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #Checks for the 90 degree tilt and wont flap wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        #Rotates the image around it's center
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

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

#Rotate a surface and blit it to the window
def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

#Draws the window
def draw_window(win, birds, pipes, base, score, gen):
    if gen == 0:
        gen = 1

    #Draws bird on window and updates the display
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    #Draws the score
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))
   
    pygame.display.update()

#Runs the main loop of the game 
def main(genomes, config):
    #Keeps track and increment by 1
    global GEN
    GEN += 1

    #Set up
    nets = [] #Keep track of the neural networks for each bird
    ge = [] #Keeps track of the genome
    birds = []

    #Keeps the bird, genome, and neural network together
    for g_id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)] #Change to move the pipes closer
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    #Allows the game to be stopped if need be
    run = True

    #Main game loop
    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        #If the bird exists
        if len(birds) > 0:
            #If the birds have passed the pipe , then change the index (the pipe the birds are looking at)
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        #Moves the birds
        for x, bird in enumerate(birds):
            bird.move() #Calls move
            ge[x].fitness += 0.1 #Increases the fitness of the bird every frame

            #Activating the neural networks based on the input
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            #When the output is greater than 0.5, the bird jumps
            if output[0] > 0.5:
                bird.jump()

        #Moves base
        base.move()

        add_pipe = False
        rem = []
        for pipe in pipes:
            #Moves pipes
            pipe.move()

            for x, bird in enumerate(birds):
                #Checks pipe bird collision for every bird and pip
                if pipe.collide(bird):
                    #Gets rid of less intelligent birds
                    ge[birds.index(bird)].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x) 

            #Checks if the pipe is off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            #Checks if the bird has passed the pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        #Adds a new pip
        if add_pipe:
            score += 1

            #Increases fitness
            for g in ge:
                g.fitness += 5

            pipes.append(Pipe(700)) #Change to move the pipes closer

        #Removes pipes
        for r in rem:
            pipes.remove(r)
        
        for x, bird in enumerate(birds):
            #Checking if the bird has hit the ground or the bird is at the top of the screen
            if bird.y + bird.img.get_height() - 10 >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        #Draws everything
        draw_window(win, birds, pipes, base, score, GEN)

        #Uncomment this section for the first time running the program
        """
        if score > 20:
            pickle.dump(nets[0], open("best.pickle", "wb"))
            break
        """

#Helps load the configuration file
def run(config_file):
    #Defining the subheadings from config-feedforward.txt
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    #Sets the population size
    p = neat.Population(config)

    #Showing the detailed report
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #Sets the fitness function
    #Uses main as the fitness function
    winner = p.run(main, 50)

    print("\nBest Genome: \n{!s}".format(winner))

#Helps load the configuration file
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) #Gets a file in the current folder
    config_path = os.path.join(local_dir, "config-feedforward.txt") #Gets the exact path
    run(config_path)