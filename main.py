import pygame
import time
import random
import os
import math
from os import listdir
from os.path import isfile, join
from threading import Timer
# Initialisation
pygame.init()

# Constantes
LARGEUR, HAUTEUR = 1000, 700
FPS = 60
VITESSE_JOUEUR = 5
VITESSE_TRAIN = 20

# Crée la fenêtre
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))

# Nom de la fenêtre
pygame.display.set_caption("Sultan's Artventures")

# Classe Joueur
class Joueur(pygame.sprite.Sprite):
    COULEUR = (255, 0, 0) # Couleur du joueur

    def __init__(self, x, y, largeur, hauteur, jumpforce): 
        """
        Constucteur de la classe Joueur, qui prend pour paramètres les coordonnées x et y du joueur, ainsi que sa largeur et sa hauteur. 
        (tsais les trucs que Mr Djahnit veut qu'on mette dans le constructeur)
        """
        self.jumpforce = jumpforce
        self.rectangle = pygame.Rect(x, y, largeur, hauteur) # Crée un rectangle pour le joueur
        self.x_vitesse = 0  # Vitesse de déplacement du joueur
        self.y_vel = 0
        self.direction = "gauche" # Direction du joueur
        self.compteur_animation = 0 # Compteur pour l'animation du joueur


    def mouvement(self, dx):
        self.rectangle.x += dx # Ajoute la vitesse de déplacement à la vitesse actuelle


    def mouvement_droite(self, vitesse): 
        """Déplace le joueur vers la droite tout en renitialisant le compteur d'animation."""
        self.x_vitesse = vitesse
        if self.direction != "droite": 
            self.direction = "droite"
            self.compteur_animation = 0 


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
        pygame.draw.rect(ecran, self.COULEUR, self.rectangle)

    def jump(self):
        self.y_vel = -self.jumpforce
    
    def update(self, grav):

        self.y_vel+= grav
        
        self.rectangle.y += self.y_vel


class Train(pygame.sprite.Sprite):
    COULEUR = (0, 50, 255)
    
    def __init__(self, x, y, largeur = 700, hauteur = 100):
        self.train = pygame.Rect(x, y, largeur, hauteur)
        self.x_vitesse = 0
        self.direction = "gauche"
        self.compteur_animation = 0
    
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
        pygame.draw.rect(ecran, self.COULEUR, self.train)
    
def get_background(name):
    image = pygame.image.load(join("assets", name))
    _, _, largeur, hauteur = image.get_rect()
    tiles = []

    for i in range(LARGEUR // largeur + 1):
        for j in range(HAUTEUR // hauteur + 1):
            pos = (i * largeur, j * hauteur)
            tiles.append(pos)
    
    return tiles, image


def dessiner(ecran, background, bg_image, joueur, train):
    """Dessine les éléments du jeu sur l'écran."""
    for tile in background:
        ecran.blit(bg_image, tile)


    joueur.dessiner(ecran)
    train.dessiner(ecran)
    pygame.display.update()


def deplacer_joueur(joueur):
    """Déplace le joueur en fonction des touches du clavier appuyées."""

    keys = pygame.key.get_pressed() # Récupère les touches du clavier appuyées

    joueur.x_vitesse = 0 # C'est important pour que le joueur s'arrête de bouger quand on relâche les touches
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: # Si la touche D ou la flèche droite est appuyée, le joueur se déplace vers la droite
        joueur.mouvement_droite(VITESSE_JOUEUR)
    if keys[pygame.K_q] or keys[pygame.K_LEFT]: # Si la touche Q ou la flèche gauche est appuyée, le joueur se déplace vers la gauche c'est le meme principe
        joueur.mouvement_gauche(VITESSE_JOUEUR)
    if keys[pygame.K_SPACE]:
        joueur.jump()

def deplacer_train(train):
    """Déplace le train vers la gauche."""
    train.mouvement_gauche(VITESSE_TRAIN)
        
        

    


def main(ecran): 
    """
    Fonction principale pour exécuter la boucle de jeu.
    
    Paramètres:
    ecran (pygame.Surface): La surface sur laquelle le jeu sera dessiné.
    """
    
    clock = pygame.time.Clock() # Initialisation de l'horloge du jeu pour contrôler le taux de rafraîchissement

    background, bg_image = get_background("paris.jpg")

    joueur = Joueur(700, 650, 50, 50, 10) # Crée un joueur
    train = Train(1000, 600, 500, 100)
    
    run = True  # Variable de contrôle pour maintenir la boucle de jeu active

    # Boucle principale du jeu
    while run:
        clock.tick(FPS) # Limite le taux de rafraîchissement à la valeur de FPS (frames per second)
 
        # Parcours de tous les événements dans la file d'attente des événements, si un événement de type QUIT est détecté (fermeture de la fenêtre) on met fin a la boucle de jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        # Mise à jour de l'écran
        # à modifier après avec un fonction pour dessiner le background
        joueur.boucle()
        train.boucle()
        deplacer_joueur(joueur)
        dessiner(ecran, background, bg_image, joueur, train)
        pygame.display.flip()
        
        
        
        if train.train.x + train.train.width < 0: # Si le train sort de l'écran, on le réinitialise
            train = Train(1000, 600, 500, 100)
        temps = random.randint(5, 10)
        t = Timer(temps, deplacer_train, [train])
        t.start()



    pygame.quit()
    quit()

if __name__ == "__main__":
    main(ecran)



