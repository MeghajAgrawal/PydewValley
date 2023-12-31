import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition

class Level:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprite = pygame.sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

    def setup(self):
        tmx_map = load_pygame('../data/map.tmx')

        #house
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y,surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,LAYERS['house bottom'])

        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x,y,surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites)

        #Fence
        for x,y,surf in tmx_map.get_layer_by_name('Fence').tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,[self.all_sprites,self.collision_sprites])
        
        #Water
        water_frames = import_folder('../graphics/water')
        print(water_frames)
        for x,y,surf in tmx_map.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE,y*TILE_SIZE),water_frames,self.all_sprites)

        # Trees and Wildflowers
        for obj in tmx_map.get_layer_by_name('Trees'):
            Tree(
                pos = (obj.x,obj.y),
                surf = obj.image,
                groups = [self.all_sprites,self.collision_sprites,self.tree_sprites],
                name = obj.name,
                player_add = self.player_add)

        for obj in tmx_map.get_layer_by_name('Decoration'):
            WildFlower((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites])

        #Collision
        for x,y,surf in tmx_map.get_layer_by_name('Collision').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),pygame.Surface((TILE_SIZE,TILE_SIZE)),self.collision_sprites)

        Generic(
            pos = (0,0),
            surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
        )

        for obj in tmx_map.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    (obj.x,obj.y),
                    self.all_sprites,
                    self.collision_sprites,
                    self.tree_sprites,
                    self.interaction_sprite)
            if obj.name == 'Bed':
                Interaction(
                    (obj.x,obj.y),
                    (obj.width,obj.height),
                    self.interaction_sprite,
                    obj.name
                    )
                
    def player_add(self,item):
        self.player.item_inventory[item] +=1

    def reset(self):
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def run(self,dt):
        self.display_surface.fill('black')
        #self.all_sprites.draw(self.display_surface)
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()
        if self.player.sleep:
            self.transition.play()
        #print(self.player.item_inventory)

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH/2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT/2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image,offset_rect)

