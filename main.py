import sys
import traceback
from random import *
import math

import pygame
from pygame.locals import *

from plane import *

pygame.init()


caption		= "飞机大战"
bg			= pygame.image.load("./img/bg.png")		# 加载背景图片,并设置为不透明
monospace	= pygame.font.SysFont( "monospace", 24 )
canvas		= width, height = 414, 736 				# 设计背景尺寸
step = 5

pygame.time.Clock().tick( 60 )

pygame.mixer.init()								# 混音器初始化
pygame.display.set_mode( canvas )				# 设置背景对话框

pygame.display.set_caption( caption )

@every( seconds = 1 )
def arriveEnemy( r ):
	if r < 0.6:
		return SmallEnemyPlane()
	elif r < 0.95:
		return MidEnemyPlane()
	else:
		return BigEnemyPlane()

@every( seconds = 15 )
def arriveSupply( r ):
	if r < 0.3:
		return UltimateSupply( [ 0 , 0 ] )
	elif r < 0.6:
		return EnchanceSupply( [ 0 , 0 ] )
	else:
		return HealingSupply( [ 0 , 0 ] )

class GameOverException( RuntimeError ):
	pass

finalpoint = 0

def main():
	global finalpoint 
	
	items = [ arriveEnemy, arriveSupply ]
	 
	selfPlane = SelfPlane()
	selfPlane.set_rect( ( ( canvas[ 0 ] - selfPlane.rect[ 0 ] ) / 2, canvas[ 1 ] - selfPlane.rect[ 1 ] ) )
	
	selfWidth = selfPlane.size[ 0 ]
	casWidth, casHeight = pygame.display.get_surface().get_size()
	
	def arrive( item ):
		if item is not None:
			itemWidth = item.size[ 1 ]
			
			lower = int( max( ( selfWidth - itemWidth ) / 2, 0 ) )
			upper = casWidth - lower
			item.set_rect( [ randrange( lower, upper ), 0 ] )
	
	screen = pygame.display.get_surface()

	ulti_img = pygame.image.load( "./img/supply-ultimate.png" )
	ulti_img_width, ulti_img_height = ulti_img.get_size()

	def hum( screen ):
		life_pec = float( selfPlane.life ) / SelfPlane.MEX_LIFE
		pygame.draw.rect(
			screen,
			( 255 * ( 1 - life_pec ), 255 * life_pec, 0 ),
			[ 0, casHeight - 15, life_pec * casWidth, 15 ]
		)
		point = monospace.render( str( selfPlane.point ), 1, ( 0, 0, 0 ) )
		screen.blit( point, ( 0, 0 ) )
		
		for i in range( selfPlane.ultimates ):
			screen.blit( ulti_img, ( casWidth - ulti_img_width * ( i + 1 ), casHeight - 15 - ulti_img_height ) )
	
	running = True
	
	while True:
		selfPlane.vex = [ 0, 0 ]
		
		key_pressed = pygame.key.get_pressed()				# 获得用户所有的键盘输入序列
		
		if key_pressed[ K_w ] or key_pressed[ K_UP ]:		# 如果用户通过键盘发出“向上”的指令,其他类似
			selfPlane.vex[ 1 ] = -step
		if key_pressed[ K_s ] or key_pressed[ K_DOWN ]:
			selfPlane.vex[ 1 ] = step
		if key_pressed[ K_a ] or key_pressed[ K_LEFT ]:
			selfPlane.vex[ 0 ] = -step
		if key_pressed[ K_d ] or key_pressed[ K_RIGHT ]:
			selfPlane.vex[ 0 ] = step
		
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_SPACE:
					selfPlane.ultimate()

		if selfPlane.life <= 0:
			finalpoint = selfPlane.point
			raise GameOverException()

		screen.blit( bg, ( 0, 0 ) )
		
		list( map( lambda item: arrive( item( random() ) ), items ) )
		
		for entity in MovingSprite.movingSprites:
			entity.update()
			entity.draw( screen )
		
		hum( screen );

		pygame.display.flip()

def end():
	screen = pygame.display.get_surface()
	casWidth, casHeight = screen.get_size()
	lose = monospace.render( "You lose, Press Q to exit", 1, ( 0, 0, 0 ) )
	loseWidth, loseHeight = lose.get_size()
	point = monospace.render( str( finalpoint ), 1, ( 0, 0, 0 ) )
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_q:
					pygame.quit()
					sys.exit()
				
		screen.blit( bg, ( 0, 0 ) )
		screen.blit( lose, ( ( casWidth - loseWidth ) / 2, ( casHeight - loseHeight ) / 2 ) )
		screen.blit( point, ( 0, 0 ) )
					
		for entity in MovingSprite.movingSprites:
			entity.update()
			entity.draw( screen )

		pygame.display.flip()

if __name__ == '__main__':
	try:
		main()
	except SystemExit:
		pass
	except GameOverException:
		end()
	except:
		traceback.print_exc()
	finally:
		pygame.quit()
