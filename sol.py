import pygame
from constants import *
class Sol(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h, *groups):
        super().__init__(*groups)
        self.x, self.y, self.w, self.h = x,y,w,h
        self.image = pygame.surface.Surface((w,h))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
    def draw(self, screen):
        pygame.draw.rect(screen,self.image,self.rect)