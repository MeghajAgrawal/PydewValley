import pygame
from settings import * 
import os
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,group, collision_sprites,tree_sprites,interaction):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        self.z = LAYERS['main']

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.hitbox = self.rect.copy().inflate((-126,-70))
    
        #movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.collision_sprites = collision_sprites

        # Timers
        self.timers = {
            'tool use' : Timer(350,self.use_tool),
            'tool switch' : Timer(200),
            'plant seed' : Timer(350,self.use_seed),
            'plant switch' : Timer(200)
        }

        # tools
        self.tools = ['hoe','axe','water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        self.seeds = ['corn','tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        #inventory
        self.item_inventory = {
            'wood':  0,
            'apple': 0,
            'corn':  0,
            'tomato':0
        }

        #interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False

    def import_assets(self):
        self.animations = {}
        for entry in os.listdir('../graphics/character/'):
            if entry not in self.animations:
                self.animations[entry] = []
            else:
                continue
        #print(self.animations)
        for animation in self.animations.keys():
            full_path = '../graphics/character/'+ animation
            self.animations[animation] = import_folder(full_path)
        
        #print(self.animations)

    def animate(self,dt):
        self.frame_index += 4*dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active and not self.sleep:
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            
            if keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # Tools use
            if keys[pygame.K_SPACE]:
                # Timer for tool use
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = 0 if self.tool_index >= len(self.tools) else self.tool_index
                self.selected_tool = self.tools[self.tool_index]
            
            if keys[pygame.K_LSHIFT]:
                # Timer for tool use
                self.timers['plant seed'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            
            if keys[pygame.K_e] and not self.timers['plant switch'].active:
                self.timers['plant switch'].activate()
                self.seed_index += 1
                self.seed_index = 0 if self.seed_index >= len(self.seeds) else self.seed_index
                self.selected_seed = self.seeds[self.seed_index]
            
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        pass
                    else:
                        self.status = 'left_idle'
                        self.sleep = True

    def get_status(self):
        
        #idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        #tools
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def collision(self,direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite,'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                    
    def move(self,dt):
        
        #normalize the vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        #Horizontal Movement
        self.pos.x += self.direction.x * self.speed * dt  
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        #Vertical Movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def use_tool(self):
        if self.selected_tool == 'hoe':
            pass
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == 'water':
            pass
    
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
    
    def use_seed(self):
        pass
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self,dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        self.move(dt)
        self.animate(dt)
        