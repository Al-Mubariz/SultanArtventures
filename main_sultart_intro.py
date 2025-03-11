import pygame, math, sys
from animation import Anima
from os.path import isfile, join

def get_background(image):
    """ Récupère les tiles et l'image de fond. """
    _, _, largeur, hauteur = image.get_rect()
    tiles = []
    for i in range(1920 // largeur + 1):
        for j in range(1080 // hauteur + 1):
            pos = (i * largeur, j * hauteur)
            tiles.append(pos)
    return tiles, image

# Initialisation
pygame.init()

# Crée la fenêtre
ecran = pygame.display.set_mode((1920, 1080))

# Nom de la fenêtre
pygame.display.set_caption("Sultan's Artventures Intro")

def main(ecran):
    """
    Fonction principale pour exécuter la boucle de jeu.
    
    Paramètres:
    ecran (pygame.Surface): La surface sur laquelle le jeu sera dessiné.
    """
    image = pygame.image.load(join("assets\\chargementbg.jpg"))
    ecran.blit(image, (0, 0))
    pygame.display.flip() 

    bckg = Anima("assets\\intro")
    
    game(ecran, bckg)

def game(ecran, bckg):
    actime = pygame.time.get_ticks()
    lasttime = 0
    indice = 313
    run = True
    clock = pygame.time.Clock()
    bckg.restart()
    image = bckg.get_imgCourante()

    while run:
        clock.tick(60) # Limite le taux de rafraîchissement à la valeur de FPS (frames per second)

        actime = pygame.time.get_ticks()

        # Parcours de tous les événements dans la file d'attente des événements, si un événement de type QUIT est détecté (fermeture de la fenêtre) on met fin a la boucle de jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                break

        if actime - lasttime > 40:
            if indice >= 0:
                image = bckg.get_imgCourante()
                bckg.defilement()
                indice-=1
            lasttime = actime
        
        ecran.blit(image, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':
    main(ecran)