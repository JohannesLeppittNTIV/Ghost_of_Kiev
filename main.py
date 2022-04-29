import pygame
from pygame import mixer
from pygame.locals import *
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()


#define fps
clock = pygame.time.Clock()
fps = 60


screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Ghost of Kiev')


#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)




#define game variables
rows = 5
cols = 5
russia_cooldown = 1000#bullet cooldown in milliseconds
last_russia_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0#0 is no game over, 1 means player has won, -1 means player has lost

#define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)



#load image
bg = pygame.image.load('assets/background.png')

print(bg)

def draw_bg():
	screen.blit(bg, (0, 0))


#define function for creating text
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))



#create ukraine class
class Ukraine(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/mig29.jpg")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.health_start = health
		self.health_remaining = health
		self.last_shot = pygame.time.get_ticks()


	def update(self):
		#set movement speed
		speed = 8
		#set a cooldown variable
		cooldown = 500 #milliseconds
		game_over = 0


		#get key press
		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT] and self.rect.left > 0:
			self.rect.x -= speed
		if key[pygame.K_RIGHT] and self.rect.right < screen_width:
			self.rect.x += speed

		#record current time
		time_now = pygame.time.get_ticks()
		#shoot
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			bullet = Bullets(self.rect.centerx, self.rect.top)
			bullet_group.add(bullet)
			self.last_shot = time_now


		#update mask
		self.mask = pygame.mask.from_surface(self.image)


		#draw health bar
		pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
		if self.health_remaining > 0:
			pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
		elif self.health_remaining <= 0:
			self.kill()
			game_over = -1
		return game_over



#create Bullets class
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/bullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y -= 5
		if self.rect.bottom < 0:
			self.kill()
		if pygame.sprite.spritecollide(self, russia_group, True):
			self.kill()




#create Russians class
class Russians(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/su34.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.move_counter = 0
		self.move_direction = 1

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75:
			self.move_direction *= -1
			self.move_counter *= self.move_direction



#create Russia Bullets class
class Russia_Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/russiabullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > screen_height:
			self.kill()
		if pygame.sprite.spritecollide(self, ukraine_group, False, pygame.sprite.collide_mask):
			self.kill()
			#reduce ukraine health
			ukraine.health_remaining -= 1









#create sprite groups
ukraine_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
russia_group = pygame.sprite.Group()
russia_bullet_group = pygame.sprite.Group()


def create_russians():
	#generate russians
	for row in range(rows):
		for item in range(cols):
			russia = Russians(100 + item * 100, 100 + row * 70)
			russia_group.add(russia)

create_russians()


#create player
ukraine = Ukraine(int(screen_width / 2), screen_height - 100, 3)
ukraine_group.add(ukraine)



run = True
while run:

	clock.tick(fps)

	#draw background
	draw_bg()


	if countdown == 0:
		#create random russia bullets
		#record current time
		time_now = pygame.time.get_ticks()
		#shoot
		if time_now - last_russia_shot > russia_cooldown and len(russia_bullet_group) < 5 and len(russia_group) > 0:
			attacking_russia = random.choice(russia_group.sprites())
			russia_bullet = Russia_Bullets(attacking_russia.rect.centerx, attacking_russia.rect.bottom)
			russia_bullet_group.add(russia_bullet)
			last_russia_shot = time_now

		#check if all the russians have been killed
		if len(russia_group) == 0:
			game_over = 1

		if game_over == 0:
			#update ukraine
			game_over = ukraine.update()

			#update sprite groups
			bullet_group.update()
			russia_group.update()
			russia_bullet_group.update()
		else:
			if game_over == -1:
				draw_text('UKRAINE DEFEATED!', font40, white, int(screen_width / 2 - 190), int(screen_height / 2 + 50))
			if game_over == 1:
				draw_text('RUSSIA DEFEATED!', font40, white, int(screen_width / 2 - 180), int(screen_height / 2 + 50))

	if countdown > 0:
		draw_text('DEFEND UKRAINE!', font40, white, int(screen_width / 2 - 180), int(screen_height / 2 + 50))
		draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
		count_timer = pygame.time.get_ticks()
		if count_timer - last_count > 1000:
			countdown -= 1
			last_count = count_timer




	#draw sprite groups
	ukraine_group.draw(screen)
	bullet_group.draw(screen)
	russia_group.draw(screen)
	russia_bullet_group.draw(screen)


	#event handlers
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False


	pygame.display.update()

pygame.quit()