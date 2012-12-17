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

header = Image.open('assets/receiptheader.jpg')
def print_header():
	"print receipt header"
	# printer.print_bitmap(list(header.getdata()), 384, 324, True)
	
class zoltar :
	screen = None
	current_game = None
	current_question = None
	current_image = None
	logo = None
	wait_screen = None
	header_thread = None

	def __init__(self):
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
			self.header_thread = Process(target=print_header)
			self.header_thread.start()

    def next_question(self):
		self.current_question = self.current_game.next_question()
		if ( self.current_question == None ):
			self.screen.blit(self.wait_screen, (0, 0))
			pygame.display.update()
			self.header_thread.join()
			print self.current_game.answers
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
				printer.print_bitmap(data, w, h, True)
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
        if (GPIO.input(JOY_UP) == False):
        	self.start_game()
        	print "UP"
        if (GPIO.input(JOY_LEFT) == False):
        	self.start_game()
        	print "LEFT"
        	self.answer_question("left")
        if (GPIO.input(BUTTON) == False):
        	self.start_game()
        	print "BUTTON"
        	meow_sound.play()
        if (GPIO.input(JOY_RIGHT) == False):
        	self.start_game()
        	print "RIGHT"
        	self.answer_question("right")
        if (GPIO.input(JOY_DOWN) == False):
        	self.start_game()
        	print "DOWN"
        if (GPIO.input(JOY_UP) == False and GPIO.input(BUTTON) == False):
        	sys.exit()

    def run(self):
		"Test method to make sure the display is configured correctly"
		clock = pygame.time.Clock()
		while True:
			#if (pygame.time.get_ticks() >= 30000):
				#sys.exit()			
			self.poll_input()
			self.draw_screen()

# Create an instance of the zoltar class
zoltar().run()