# Classe Train
import pygame

class Train(pygame.sprite.Sprite):
    COULEUR = (0, 50, 255)
    
    def __init__(self, x, y, largeur, hauteur):
        self.train = pygame.Rect(x, y, largeur, hauteur)
        self.x_vitesse = 0
        self.direction = "gauche"
        self.compteur_animation = 0
        self.Image = pygame.image.load('assets\\Metro.png')
    
    def mouvement(self, dx):
        self.train.x += dx # Ajoute la vitesse de déplacement à la vitesse actuelle

    def mouvement_gauche(self, vitesse):
        """Déplace le joueur vers la gauche de la meme manière mdr"""
        self.x_vitesse = -vitesse
        if self.direction != "gauche":
            self.direction = "gauche"
            self.compteur_animation = 0

    def boucle(self):
        """Met à jour la position du joueur en fonction de sa vitesse."""
        self.mouvement(self.x_vitesse)

    def dessiner(self, ecran):
        """"Dessine le joueur sur l'écran."""
        ecran.blit(self.Image, (self.train.x, 0))