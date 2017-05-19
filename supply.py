import pygame
from pygame.locals import *

from local_utils import *
from bullet import *
from custome_sprite import *

from math import *
from datetime import *

def pick( imgs, duration ):
	return imgs[ floor( ( timestamp( datetime.now() ) % duration ) * len( imgs ) / duration ) ]

class Supply( MovingSprite, FallingMixin ):
	supplies = pygame.sprite.Group()
	
	def __init__( self, rect, self_bg ):
		MovingSprite.__init__( self )
		Supply.supplies.add( self )
		
		self_bg = pygame.image.load( self_bg )
		gas_bgs = tuple( map(
			lambda x: pygame.image.load( x ),
			(
				"./img/parachute-f.png",
				"./img/parachute-s.png"
			)
		) )
		
		self.self_bg = self_bg
		self.gas_bgs = gas_bgs
		
		gas_bg = gas_bgs[ 0 ]
		
		self_size = self_bg.get_size()
		gas_size = gas_bg.get_size()
		
		self.size = ( self_size[ 0 ], self_size[ 1 ] + gas_size[ 1 ] )
		self.mask = pygame.mask.from_surface( self_bg )  # 获取飞机图像的掩膜用以更加精确的碰撞检测
		
		self.set_rect( rect )
		self.vex = [ 0, 2 ]
		
		FallingMixin.__init__( self )
	def get_gas_bg( self ):
		return pick( self.gas_bgs, 500 )
	def update( self, *args, **kwargs ):
		MovingSprite.update( self, *args, **kwargs )
		FallingMixin.update( self, *args, **kwargs )
	def draw( self, screen ):
		rect = self.get_rect()
		self_bg = self.self_bg
		gas_bg = self.get_gas_bg()
		
		gas_size = gas_bg.get_size()
		
		screen.blit( gas_bg, pygame.Rect(
			rect, gas_size
		) )
		
		screen.blit( self_bg, pygame.Rect(
			( rect[ 0 ], rect[ 1 ] + gas_size[ 1 ] ), self_bg.get_size()
		) )
	def affect( self, selfPlane ):
		self.kill()

class HealingSupply( Supply ):
	def __init__( self, rect ):
		Supply.__init__( self, rect, "./img/supply-healing.png" )
	def affect( self, selfPlane ):
		Supply.affect( self, selfPlane )
		selfPlane.life = 15

class UltimateSupply( Supply ):
	def __init__( self, rect ):
		Supply.__init__( self, rect, "./img/supply-ultimate.png" )
	def affect( self, selfPlane ):
		Supply.affect( self, selfPlane )
		selfPlane.ultimates += 1

class EnchanceSupply( Supply ):
	def __init__( self, rect ):
		Supply.__init__( self, rect, "./img/supply-enchance.png" )
	def affect( self, selfPlane ):
		Supply.affect( self, selfPlane )
		selfPlane.enchance()