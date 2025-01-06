import pygame
import random
import player
import train
import sol
from os import listdir
from os.path import isfile, join
from threading import Timer


# Initialisation
pygame.init()

# Constantes
from constants import *


# Crée la fenêtre
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))

# Nom de la fenêtre
pygame.display.set_caption("Sultan's Artventures")

def get_background(name):
    """ Récupère les tiles et l'image de fond. """
    image = pygame.image.load(join("assets", name))
    _, _, largeur, hauteur = image.get_rect()
    tiles = []

    for i in range(LARGEUR // largeur + 1):
        for j in range(HAUTEUR // hauteur + 1):
            pos = (i * largeur, j * hauteur)
            tiles.append(pos)
    
    return tiles, image



def dessiner(ecran, background, bg_image):
    """Dessine les éléments du jeu sur l'écran."""
    for tile in background:
        ecran.blit(bg_image, tile)

    pygame.display.update()

def plyr_inputs(joueur):
    """Déplace le joueur en fonction des touches du clavier appuyées."""
    keys = pygame.key.get_pressed() # Récupère les touches du clavier appuyées
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: # Si la touche D ou la flèche droite est appuyée, le joueur se déplace vers la droite
        joueur.mouvement(1)
    elif keys[pygame.K_q] or keys[pygame.K_LEFT]: # Si la touche Q ou la flèche gauche est appuyée, le joueur se déplace vers la gauche c'est le meme principe
        joueur.mouvement(-1)
    else: joueur.mouvement(0) # immobilité
    if keys[pygame.K_SPACE] and joueur.floored:
        joueur.jump()

def main(ecran): 
    """
    Fonction principale pour exécuter la boucle de jeu.
    
    Paramètres:
    ecran (pygame.Surface): La surface sur laquelle le jeu sera dessiné.
    """
    
    
    clock = pygame.time.Clock() # Initialisation de l'horloge du jeu pour contrôler le taux de rafraîchissement
    background, bg_image = get_background("MetroBackgroundBonnesDimensions.png") # Récupère les tiles et l'image de fond

    """ Crée un joueur, un train et un sol """
    joueur = player.Joueur(200, 200, 25, 50) # Crée un joueur
    metros = pygame.sprite.Group()
    sols = pygame.sprite.Group()
    metro = train.Train(1000, 500, 1000, 200) # Crée un train
    sol1 = sol.Sol(0,HAUTEUR - 20, LARGEUR, 50) # Crée un sol
    sol2 = sol.Sol(0,HAUTEUR - 100, LARGEUR/3, 10)
    metros.add(metro)
    sols.add(sol1, sol2)
    
    allsprites = pygame.sprite.Group(sols,joueur,metros)
    
    run = True  # Variable de contrôle pour maintenir la boucle de jeu active

    # Boucle principale du jeu
    while run:
        clock.tick(FPS) # Limite le taux de rafraîchissement à la valeur de FPS (frames per second)
 
        # Parcours de tous les événements dans la file d'attente des événements, si un événement de type QUIT est détecté (fermeture de la fenêtre) on met fin a la boucle de jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        # inputs
        plyr_inputs(joueur) # Déplace le joueur en fonction des touches du clavier appuyées
        # Mise à jour de l'écran
        
        dessiner(ecran, background, bg_image) # Dessine les éléments du jeu sur l'écran
        allsprites.update()
        allsprites.draw(ecran)
        pygame.display.flip() # Met à jour l'écran


        # collisions
        
        joueur.collideSol(sols)
            
            


        """ Si le train sort de l'écran, on le réinitialise et on le fait réapparaître après un temps aléatoire"""
        if metro.rect.x + metro.rect.width < 0: 
            metro = train.Train(1000, 500, 1000, 200)
            metro.lance = False
        """if metro.lance:
            metro.mouvement(-1)
        temps = random.randint(5, 10)
        t = Timer(temps, metro.lancer())
        t.start()"""

    # Quitte proprement Pygame puis quitte le programme Python
    pygame.quit()
    quit()

if __name__ == "__main__":
    
    main(ecran)




