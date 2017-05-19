import pygame
from pygame.locals import *
from local_utils import *

class LocalableSprite( pygame.sprite.Sprite ):
	@staticmethod
	def _constrain_pos( rect, size, limits ):
		return list(
			map(
				lambda x:
					int( constrain( x[ 0 ], 0, x[ 2 ] - x[ 1 ] ) ),
				zip( rect, size, limits )
			)
		)
	def __init__( self ):
		pygame.sprite.Sprite.__init__( self )
		self.size = [ 0, 0 ]
		self.rect = [ 0, 0 ]
		self.rect_limits = pygame.display.get_surface().get_size()
	def set_rect( self, rect ):
		self.rect = MovingSprite._constrain_pos( rect, self.size, self.rect_limits )
	def get_rect( self ):
		self.set_rect( self.rect )
		
		return list( self.rect )

class MovingSprite( LocalableSprite ):
	moving = True
	movingSprites = pygame.sprite.Group()
	
	def __init__( self ):
		LocalableSprite.__init__( self )
		MovingSprite.movingSprites.add( self )
		self.vex = [ 0, 0 ]
	def update( self, *args, **kwargs ):
		LocalableSprite.update( self, *args, **kwargs )
		self.set_rect( map( lambda x: x[ 0 ] + x[ 1 ], zip( self.get_rect(), self.vex ) ) )

class FallingMixin:
	def __init__( self ):
		self.height_limits = ( 0, pygame.display.get_surface().get_height() - self.size[ 1 ] )
	def update( self, *args, **kwargs ):
		if not between( self.get_rect()[ 1 ], *self.height_limits ):
			self.kill()