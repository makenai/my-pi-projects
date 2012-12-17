import os
import pygame
import time
import random
import sys
import Image, ImageDraw
import RPi.GPIO as GPIO
import pygame.mixer
from multiprocessing import Process
from printer import *
from game_session import *
from recommendation_grabber import *

CORE_VALUES = [
	"Deliver WOW Through Service",
	"Embrace and Drive Change",
	"Create Fun and A Little Weirdness",
	"Be Adventurous, Creative, and Open-Minded",
	"Pursue Growth and Learning",
	"Build Open and Honest Relationships With Communication",
	"Build a Positive Team and Family Spirit",
	"Do More With Less",
	"Be Passionate and Determined",
	"Be Humble"
]

pygame.mixer.init(48000, -16, 1, 15000)
meow_sound = pygame.mixer.Sound("assets/cutemeow.wav")
blip_sound = pygame.mixer.Sound("assets/blip.wav")
welcome_sound = pygame.mixer.Sound("assets/welcome.wav")
printing_sound = pygame.mixer.Sound("assets/printing.wav")
printer = ThermalPrinter()

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

JOY_UP = 4
JOY_DOWN = 25
JOY_LEFT = 22
JOY_RIGHT = 24
BUTTON = 23

class zoltar :
    screen = None
    current_game = None
    current_question = None
    current_image = None
    logo = None
    wait_screen = None
    header_thread = None
    header = Image.open('assets/receiptheader.jpg')
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        
        # Hide the mouse
        pygame.mouse.set_visible(False)
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print "Framebuffer size: %d x %d" % (size[0], size[1])
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        

		# Render the screen
        pygame.display.update()
        
        self.wait_screen = pygame.image.load('assets/gypsycat.png').convert()
        self.logo = pygame.image.load('assets/logo.png').convert()
        self.grabber = recommendation_grabber()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def draw_screen(self):
    	self.screen.fill((0,0,0))
    	if (self.current_game == None):
    		self.screen.blit(self.logo, (0, 0))
    	else:
    		self.screen.blit(self.current_image, (0, 0))
    	pygame.display.update()
   
    def start_game(self):
		"Try to start the game if not already running"
		if ( self.current_game == None ):
			self.current_game = game_session()
			self.next_question()
#			self.header_thread = Process(target=print_header)
#			self.header_thread.start()
			welcome_sound.play()
			return True
		return False

    def next_question(self):
		self.current_question = self.current_game.next_question()
		if ( self.current_question == None ):
			self.screen.blit(self.wait_screen, (0, 0))
			printing_sound.play()
			pygame.display.update()
			self.header_thread.join()
			print self.current_game.answers
			printer.print_bitmap(list(self.header.getdata()), 384, 324)
			outfit = self.grabber.get_recommendations(self.current_game.answers)
			printer.linefeed()
			for item in outfit:
				# print sku
				printer.print_text('SKU# ' + item['sku'])
				printer.linefeed()
				printer.print_text(item['name'])
				printer.linefeed()				
				print item['sku']
				# print item picture
				image_filename = self.grabber.get_image(item['image'], item['sku'])
				i = Image.open(image_filename)
				data = list(i.getdata())
				w, h = i.size
				printer.print_bitmap(data, w, h)
				printer.linefeed()
			printer.print_text("Your core value of the day is:")
			printer.linefeed()
			printer.print_text( random.choice( CORE_VALUES ) )
			printer.linefeed()
			printer.linefeed()
			printer.linefeed()
			self.current_game = None
		else:
			self.current_image = pygame.image.load( self.current_question["image"] ).convert()
		time.sleep(0.5)

    def answer_question(self,direction):
    	if ( self.current_game != None ):
	        self.current_game.store_answer( self.current_question[ direction ] )
	        blip_sound.play()
	        self.next_question()

    def poll_input(self):
        "we're gonna make the buttons worky"
        if (GPIO.input(JOY_UP) == False and GPIO.input(BUTTON) == False):
        	sys.exit()        
        if (GPIO.input(JOY_UP) == False):
        	self.start_game()
        	print "UP"
        if (GPIO.input(JOY_LEFT) == False):
        	self.start_game()
        	print "LEFT"
        	self.answer_question("left")
        if (GPIO.input(BUTTON) == False):
        	if ( self.start_game() == False ):
        		meow_sound.play()
        	print "BUTTON"
        if (GPIO.input(JOY_RIGHT) == False):
        	self.start_game()
        	print "RIGHT"
        	self.answer_question("right")
        if (GPIO.input(JOY_DOWN) == False):
        	self.start_game()
        	print "DOWN"

    def run(self):
		"Test method to make sure the display is configured correctly"
		#logo = pygame.image.load('richcat.png').convert()
		clock = pygame.time.Clock()
		while True:
			#if (pygame.time.get_ticks() >= 30000):
				#sys.exit()
			
			self.poll_input()
			self.draw_screen()
			
#			self.screen.fill((0,0,0))
#			self.screen.blit(logo, (0, 0))
#			pygame.display.update()
       
# Create an instance of the zoltar class
zoltar().run()