import pygame
import random
import player
from train import Train
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
JUMPFORCE = 30
GRAVITE = 1
WHITE, BLACK, RED, BLUE, GREEN= (255,255,255),(0,0,0),(255,0,0),(0,0,255),(0,255,0)


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

def constrain(var, minV, maxV): 
    """on regarde si la variable var est entre minV et maxV sinon on renvoie minV ou maxV"""
    if var > maxV:
        return maxV
    if var < minV:
        return minV
    else:
        return var
    

def dessiner(ecran, background, bg_image, joueur, metro):
    """Dessine les éléments du jeu sur l'écran."""
    for tile in background:
        ecran.blit(bg_image, tile)


    joueur.dessiner(ecran)
    metro.dessiner(ecran)
    pygame.display.update()

def deplacer_joueur(joueur):
    """Déplace le joueur en fonction des touches du clavier appuyées."""
    keys = pygame.key.get_pressed() # Récupère les touches du clavier appuyées

    joueur.x_vitesse = 0 # C'est important pour que le joueur s'arrête de bouger quand on relâche les touches
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: # Si la touche D ou la flèche droite est appuyée, le joueur se déplace vers la droite
        joueur.mouvement_droite(VITESSE_JOUEUR)
    if keys[pygame.K_q] or keys[pygame.K_LEFT]: # Si la touche Q ou la flèche gauche est appuyée, le joueur se déplace vers la gauche c'est le meme principe
        joueur.mouvement_gauche(VITESSE_JOUEUR)
    if keys[pygame.K_SPACE] and joueur.floored:
        joueur.jump()
        
    


def update(joueur):


    joueur.update(GRAVITE)

    joueur.rect.x = constrain(joueur.rect.x, 10, LARGEUR - 60)
    #joueur.rectangle.y = constrain(joueur.rectangle.y, 10, HAUTEUR - 60)


def deplacer_train(metro):
    """Déplace le train vers la gauche."""
    metro.mouvement_gauche(VITESSE_TRAIN)


def main(ecran): 
    """
    Fonction principale pour exécuter la boucle de jeu.
    
    Paramètres:
    ecran (pygame.Surface): La surface sur laquelle le jeu sera dessiné.
    """
    
    
    clock = pygame.time.Clock() # Initialisation de l'horloge du jeu pour contrôler le taux de rafraîchissement
    background, bg_image = get_background("MetroBackgroundBonnesDimensions.png")


    joueur = player.Joueur(200, 200, 25, 50, JUMPFORCE) # Crée un joueur
    metro = Train(1000, 500, 1000, 200)
    sol = pygame.Rect(0,HAUTEUR - 20, LARGEUR, 50)


    
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
        joueur.boucle()
        metro.boucle()
        deplacer_joueur(joueur)
        dessiner(ecran, background, bg_image, joueur, metro)
        pygame.draw.rect(ecran,WHITE, sol)
        pygame.display.flip()
        update(joueur) #on met a jour les variables

        if not joueur.floored:
            joueur.collideSol(sol)
            print(joueur.floored)



        
        
        if metro.train.x + metro.train.width < 0: # Si le train sort de l'écran, on le réinitialise
            metro = Train(1000, 500, 1000, 200)
        temps = random.randint(5, 10)
        t = Timer(temps, deplacer_train, [metro])
        t.start()
        


    pygame.quit()
    quit()
    # Quitte proprement Pygame puis quitte le programme Python
    pygame.quit()
    quit()

if __name__ == "__main__":
    
    main(ecran)




