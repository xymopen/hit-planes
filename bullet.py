import pygame
from pygame.locals import *
from custome_sprite import *

class Bullet( MovingSprite, FallingMixin ):
	def __init__( self, life, rect, vex ):
		MovingSprite.__init__( self )
		self.self_bg = pygame.image.load( "./img/bullet.png" )
		self.size = self.self_bg.get_size()
		self.mask = pygame.mask.from_surface( self.self_bg )  # 获取飞机图像的掩膜用以更加精确的碰撞检测
		
		self.set_rect( rect )
		self.vex = vex
		
		self.life = life
		
		FallingMixin.__init__( self )
	def draw( self, screen ):
		screen.blit( self.self_bg, pygame.Rect(
			self.get_rect(), self.size
		) )
	def update( self, *args, **kwargs ):
		MovingSprite.update( self )
		FallingMixin.update( self, *args, **kwargs )
		
		if self.life <= 0:
			self.kill()
