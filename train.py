# Classe Train
import pygame
from constants import *

class Train(pygame.sprite.Sprite):
    COULEUR = GREEN
    
    def __init__(self, x, y, w, h, *groups):
        super().__init__(*groups)
        self.image = pygame.surface.Surface((w,h))
        self.image.fill(self.COULEUR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.compteur_animation = 0
        self.lance = False
    
    def mouvement(self, dir):
        """dx est la vitesse et dir est la direction (1 pour la droite et -1 pour la gauche)"""
        self.rect.x += VITESSE_TRAIN * dir # Ajoute la vitesse de déplacement à la vitesse actuelle
        if dir == 1: self.direction = "droite"
        elif dir == -1: self.direction = "gauche"
        else: self.direction = "idle"

    def lancer(self):
        self.lance = True


    def draw(self, ecran):
        """"Dessine le joueur sur l'écran."""
        pygame.draw.rect(ecran, self.image, self.rect)