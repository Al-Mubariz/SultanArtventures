# Classe Joueur
import pygame
import train
from constants import *
from animation import Anima

class Joueur(pygame.sprite.Sprite):
    COULEUR = RED # Couleur du joueur

    def __init__(self, x, y, w, h, *groups): 
        super().__init__(*groups)
        """
        Constucteur de la classe Joueur, qui prend pour paramètres les coordonnées x et y du joueur, ainsi que sa largeur et sa hauteur. 
        (tsais les trucs que Mr Djahnit veut qu'on mette dans le constructeur)
        """
        self.x, self.y =x, y
        self.idleAnim = Anima('assets/PlayerAnim/IdlePlayerAnim/')
        self.image = self.idleAnim.get_imgCourante().convert_alpha() # a remplacer par la vrai image a terme
        self.image = pygame.transform.scale(self.image, (150, 150)) 
        self.rect = self.image.get_rect() # Crée un rectangle pour le joueur
        self.rect = self.rect.scale_by(0.985)
        self.rect.topleft = (x,y) # on le positionne

        self.jumpforce = JUMPFORCE
        self.x_vel = 0  # Vitesse de déplacement du joueur
        self.y_vel = 0
        self.direction = "gauche" # Direction du joueur
        self.compteur_animation = 0 # Compteur pour l'animation du joueur
        self.floored = False

    def draw(self, ecran):
        self.image = self.idleAnim.get_imgCourante()
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect() # Crée un rectangle pour le joueur
        self.rect = self.rect.scale_by(0.985)
        self.rect.topleft = (self.x,self.y)
        pygame.draw.rect(ecran,self.image,self.rect)

    def mouvement(self, dir):
        """dx est la vitesse et dir est la direction (1 pour la droite et _1 pour la gauche)"""
        self.rect.x += VITESSE_JOUEUR * dir # Ajoute la vitesse de déplacement à la vitesse actuelle
        if dir == 1: self.direction = "droite"
        elif dir == -1: self.direction = "gauche"
        else: self.direction = "idle"

    def jump(self):
        """
        Fait sauter le joueur en définissant la vitesse verticale à une valeur négative
        définie par la force de saut et en marquant le joueur comme n'étant pas au sol.

        Attributs:
        self.y_vel (float): La vitesse verticale du joueur.
        self.jumpforce (float): La force appliquée au joueur pour le faire sauter.
        self.floored (bool): Un indicateur indiquant si le joueur est au sol.
        """
        
        self.y_vel = -self.jumpforce
        self.floored = False
    
    def update(self):
        """
        Met à jour la position verticale du joueur en fonction de la gravité.
        Args:
            grav (float): La valeur de la gravité à appliquer à la vitesse verticale du joueur.
        Attributs modifiés:
            self.lastY (int): La dernière position verticale du joueur.
            self.y_vel (float): La vitesse verticale du joueur, augmentée par la gravité.
            self.rect.y (int): La nouvelle position verticale du joueur, ajustée en fonction de la vitesse verticale.
        """
        
        self.rect.x = constrain(self.rect.x, 10, LARGEUR - 60)
        self.lastY = self.rect.y
        self.y_vel += GRAVITE
        
        if self.floored:
            self.rect.y = self.lastY
        else:
            self.rect.y += self.y_vel

        
        
    def collideSol(self, colliders):
        """
        Vérifie si le joueur entre en collision avec le sol.
        Cette méthode déplace le rectangle de collision du joueur de 5 pixels vers la droite
        et vérifie s'il entre en collision avec le rectangle du sol. Si une collision est détectée,
        l'attribut 'floored' du joueur est défini sur True, sinon il est défini sur False.
        Args:
            sol (pygame.Rect): Le rectangle représentant le sol avec lequel vérifier la collision.
        """
        proj = Sprt(self.rect, (self.y_vel,0))
        collist = pygame.sprite.spritecollide(proj, colliders, False)
        if collist:
            for s in collist:
                if type(s) == train.Train:
                    pass # faudra appeler collideTrain la ou on fera des trucs 
            self.floored = True
            self.y_vel = 0
        else: self.floored = False
        
    def collideTrain(self, trains): # faudra ajouter des spécificités
        pass
        



   