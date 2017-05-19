import pygame
from pygame.locals import *

from local_utils import *
from custome_sprite import *
from bullet import *
from supply import *

from math import *
from datetime import *

def pick( imgs, duration ):
	return imgs[ floor( ( timestamp( datetime.now() ) % duration ) * len( imgs ) / duration ) ]

class Plane( MovingSprite ):
	@staticmethod
	def hit( a, b ):
		cost = min( a.life, b.life )
		a.life -= cost
		b.life -= cost
	def __init__( self, self_bg, exp_bg, gas_bgs ):
		MovingSprite.__init__( self )
		
		self_bg = pygame.image.load( self_bg )
		exp_bg = pygame.image.load( exp_bg )
		gas_bgs = tuple( map( lambda x: pygame.image.load( x ), gas_bgs ) )
		
		self.self_bg = self_bg
		self.exp_bg = exp_bg
		self.gas_bgs = gas_bgs
		self.mask = pygame.mask.from_surface( self_bg )  # 获取飞机图像的掩膜用以更加精确的碰撞检测
		
		gas_bg = gas_bgs[ 0 ]
		
		self_size = self_bg.get_size()
		gas_size = gas_bg.get_size()
		
		self.size = ( self_size[ 0 ], self_size[ 1 ] + gas_size[ 1 ] )
		
		self.life = 1
		self.exploded = False
		self._exploded_dt = 0
	def get_gas_bg( self ):
		return pick( self.gas_bgs, 500 )
	def update( self, *args, **kwargs ):
		MovingSprite.update( self, *args, **kwargs )
		
		if self.life <= 0 and not self.exploded:
			self.exploded = True
			self._exploded_dt = datetime.now()
		
		if self.exploded:
			self.vex = [ 0, 0 ]
			
			if datetime.now() - self._exploded_dt > timedelta( milliseconds = 500 ):
				self.kill()
	def draw( self, screen ):
		if self.exploded:
			screen.blit( self.exp_bg, pygame.Rect(
				self.get_rect(), self.exp_bg.get_size()
			) )
		else:
			self.drawPlane( screen )
	def drawPlane( screen ):
		pass

class SelfPlane( Plane ):
	selfBullets = pygame.sprite.Group()
	MEX_LIFE = 15
	point = 0
	def __init__( self ):
		Plane.__init__(
			self,
			"./img/self.png",
			"./img/self-exp.png",
			(
				"./img/self-gas-f.png",
				"./img/self-gas-s.png"
			)
		)
		self.ivc_bgs = tuple(
			map(
				lambda x: pygame.image.load( x ),
				(
					"./img/ivc-bg-f.png",
					"./img/ivc-bg-s.png"
				)
			)
		)
		self.life = SelfPlane.MEX_LIFE
		self.ultimates = 3
		self.enchanced = False
		self._enchanced_dt = datetime.now()
		self.invincible = True
		self._invincible_dt = datetime.now()
	def get_ivg_bg( self ):
		return pick( self.ivc_bgs, 500 )
	def drawPlane( self, screen ):
		rect = self.get_rect()
		self_bg = self.self_bg
		gas_bg = self.get_gas_bg()
		ivc_bg = self.get_ivg_bg()
		
		self_size = self_bg.get_size()
		ivc_size = ivc_bg.get_size()
		
		screen.blit( self_bg, pygame.Rect(
			rect, self_size
		) )
		
		screen.blit( gas_bg, pygame.Rect(
			( rect[ 0 ], rect[ 1 ] + self_size[ 1 ] ),
			gas_bg.get_size()
		) )
		
		if self.invincible:
			screen.blit( ivc_bg, pygame.Rect(
				(
					rect[ 0 ] - ( ivc_size[ 0 ] - self_size[ 0 ] ) / 2,
					rect[ 1 ] - ( ivc_size[ 1 ] - self_size[ 1 ] ) / 2
				),
				ivc_size
			) )
	def update( self, *args, **kwargs ):
		Plane.update( self, *args, **kwargs )
		
		if ( datetime.now() - self._invincible_dt > timedelta( seconds = 3 ) ):
			self.invincible = False
		
		if not self.invincible:
			collisions = pygame.sprite.spritecollide(
				self,
				EnemyPlane.enemies,
				False,
				pygame.sprite.collide_mask
			)
			
			for enemy in collisions:
				Plane.hit( self, enemy )
			
			collisions = pygame.sprite.spritecollide(
				self,
				EnemyPlane.bullets,
				False,
				pygame.sprite.collide_mask
			)
			
			for bullet in collisions:
				Plane.hit( self, bullet )
		
		collisions = pygame.sprite.spritecollide(
			self,
			Supply.supplies,
			False,
			pygame.sprite.collide_mask
		)
		
		for supply in collisions:
			supply.affect( self )
			supply.kill
		
		if self.life > 0:
			if self.enchanced:
				if datetime.now() - self._enchanced_dt > timedelta( seconds = 15 ):
					self.enchanced = False
				
				self.supershoot()
			else:
				self.shoot()
	def enchance( self ):
		self.enchanced = True
		self._enchanced_dt = datetime.now()
	@every( milliseconds = 200 )
	def supershoot( self ):
		rect = self.get_rect()
		initLeft = rect[ 0 ] + self.size[ 0 ] / 2
		rect[ 1 ] -= 5
		rect[ 0 ] = initLeft - 50
		bullet = Bullet( 1, rect, [ 0, -10 ] )
		SelfPlane.selfBullets.add( bullet )
		rect[ 0 ] = initLeft + 50
		bullet = Bullet( 1, rect, [ -0, -10 ] )
		SelfPlane.selfBullets.add( bullet )
	@every( milliseconds = 200 )
	def shoot( self ):
		rect = self.get_rect()
		rect[ 0 ] += self.size[ 0 ] / 2
		rect[ 1 ] -= 5
		bullet = Bullet( 1, rect, [ 0, -10 ] )
		SelfPlane.selfBullets.add( bullet )
	def ultimate( self ):
		if self.life > 0 and self.ultimates > 0:
			self.ultimates = self.ultimates - 1
			
			for enemy in EnemyPlane.enemies:
				enemy.life = 0;

class EnemyPlane( Plane, FallingMixin ):
	enemies = pygame.sprite.Group()
	bullets = pygame.sprite.Group()
	
	def __init__( self, *args, **kwargs ):
		Plane.__init__( self, *args, **kwargs )
		EnemyPlane.enemies.add( self )
		FallingMixin.__init__( self )
		self._point_added = False
	def drawPlane( self, screen ):
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
	def drawLife( self, screen ):
		life_pec = float( self.life ) / self.MAX_LIFE
		rect = self.get_rect()
		
		pygame.draw.rect(
			screen,
			( 0, 0, 0 ),
			[ rect[ 0 ], rect[ 1 ] - 5,  self.size[ 1 ] * life_pec, 3 ]
		)
	def update( self, *args, **kwargs ):
		Plane.update( self, *args, **kwargs )
		FallingMixin.update( self, *args, **kwargs )
		
		collisions = pygame.sprite.spritecollide(
			self,
			SelfPlane.selfBullets,
			False,
			pygame.sprite.collide_mask
		)
		
		for bullet in collisions:
			Plane.hit( self, bullet )
			
			if not self._point_added and self.life <= 0:
				self._point_added = True
				SelfPlane.point += self.point
	def _shoot( self, life, vex ):
		rect = self.get_rect()
		rect[ 0 ] += self.size[ 0 ] / 2
		rect[ 1 ] += self.size[ 1 ] + 5
		bullet = Bullet( life, rect, vex )
		EnemyPlane.bullets.add( bullet )	

class SmallEnemyPlane( EnemyPlane ):
	MAX_LIFE = 1
	point = 100
	def __init__( self ):
		EnemyPlane.__init__(
			self,
			"./img/emeny-small.png",
			"./img/emeny-small-exp.png",
			(
				"./img/emeny-small-gas-f.png",
				"./img/emeny-small-gas-s.png"
			)
		)
		self.vex = [ 0, 3 ]
		self.life = SmallEnemyPlane.MAX_LIFE

class MidEnemyPlane( EnemyPlane ):
	MAX_LIFE = 3
	point = 500
	def __init__( self ):
		@every( self, milliseconds = 750 )
		def shoot():
			EnemyPlane._shoot( self, 1, [ 0, 5 ] )
		EnemyPlane.__init__(
			self,
			"./img/emeny-mid.png",
			"./img/emeny-mid-exp.png",
			(
				"./img/emeny-mid-gas-f.png",
				"./img/emeny-mid-gas-s.png"
			)
		)
		self.vex = [ 0, 2 ]
		self.life = MidEnemyPlane.MAX_LIFE
		self.shoot = shoot
	def update( self, *args, **kwargs ):
		EnemyPlane.update( self, *args, **kwargs )
		if self.life > 0:
			self.shoot()
	def drawPlane( self, screen ):
		EnemyPlane.drawPlane( self, screen )
		if self.life < self.MAX_LIFE:
			self.drawLife( screen )

class BigEnemyPlane( EnemyPlane ):
	MAX_LIFE = 10
	point = 1000
	def __init__( self ):
		@every( self, milliseconds = 750 )
		def shoot():
			EnemyPlane._shoot( self, 5, [ 0, 5 ] )
		EnemyPlane.__init__(
			self,
			"./img/emeny-big.png",
			"./img/emeny-big-exp.png",
			(
				"./img/emeny-big-gas-f.png",
				"./img/emeny-big-gas-s.png"
			)
		)
		self.vex = [ 0, 1 ]
		self.life = BigEnemyPlane.MAX_LIFE
		self.shoot = shoot
	def update( self, *args, **kwargs ):
		EnemyPlane.update( self, *args, **kwargs )
		if self.life > 0:
			self.shoot()
	def drawPlane( self, screen ):
		EnemyPlane.drawPlane( self, screen )
		if self.life < self.MAX_LIFE:
			self.drawLife( screen )
