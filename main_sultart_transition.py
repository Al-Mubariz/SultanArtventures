#///////////////////////////////////#
import pygame, math, sys            #
from animation import Anima         #
from os import listdir              #
from os.path import isfile, join    #
from threading import Timer         #
from constants import *             #
#///////////////////////////////////#


# CONSTANTE
# --------------------------------- # {



# --------------------------------- # }


# INITIALISATION
# --------------------------------- # {

# Initialisation
pygame.init()

# Crée la fenêtre
ecran = pygame.display.set_mode((1920, 1080))

# Nom de la fenêtre
pygame.display.set_caption("Sultan's Artventures BOSSFIGHT")

# --------------------------------- # }


# CLASS
# --------------------------------- # {

class CollideZone(pygame.sprite.Sprite):
    """Classe CollideZone"""
    def __init__(self, x = 0, y = 0, w = 0, h = 0, *groups):
        """
        Constructeur de la classe CollideZone:
        - x : coordonné sur l'axe des abscisses du coint superieur gauche (=0)
        - y : coordonné sur l'axe des ordonnées du coint superieur gauche (=0)
        - w : la largeur du sol (=0)
        - h : la hauteur du sol (=0)
        """
        super().__init__(*groups) # Hérite du groupe
        self.image = pygame.surface.Surface((w, h), pygame.SRCALPHA) # Crée une image invisible à la bonne taille
        self.rect = self.image.get_rect() # Crée un rectangle de l'image
        self.rect.topleft = (x, y) # Déplace le rectangle au bonne coordonnées

    def set_pos(self, x, y):
        """Met à jour la position de l'Objet"""
        self.rect.topleft = (x, y) # Déplace le rectangle au bonne coordonnées
    
    def set_size(self, w, h):
        """Met à jour la taille de l'Objet"""
        self.image = pygame.surface.Surface((w, h), pygame.SRCALPHA) # Crée une image invisible à la bonne taille
        self.rect = self.image.get_rect() # Déplace le rectangle au bonne coordonnées

class Joueur(pygame.sprite.Sprite):
    """Classe Joueur"""
    def __init__(self, x, y, *groups): 
        """
        Constucteur de la classe Joueur, qui prend pour paramètres les coordonnées x et y du joueur, ainsi que sa largeur et sa hauteur. 
        (tsais les trucs que Mr Djahnit veut qu'on mette dans le constructeur)
        """
        super().__init__(*groups)
        self.x, self.y =x, y
        self.idleAnim = Anima('assets/PlayerAnim/IdlePlayerAnim/')
        self.walkAnim = Anima('assets/PlayerAnim/WalkPlayerAnim/')
        self.fallAnim = Anima('assets/PlayerAnim/FallPlayerAnim/')
        self.image = self.idleAnim.get_imgCourante().convert_alpha() # a remplacer par la vrai image a terme
        self.image = pygame.transform.scale(self.image, (150, 150)) 
        self.rect = self.image.get_rect() # Crée un rectangle pour le joueur
        self.rect = self.rect.scale_by(0.985)
        self.rect.topleft = (x,y) # on le positionne

        self.jumpforce = 23
        self.x_vel = 0  # Vitesse de déplacement du joueur
        self.y_vel = 0
        self.direction = "droite" # Direction du joueur
        self.action = 'idle'
        self.compteur_animation = 0 # Compteur pour l'animation du joueur
        self.floored = False

    def mouvement(self, dir):
        """dx est la vitesse et dir est la direction (1 pour la droite et _1 pour la gauche)"""
        self.rect.x += 4 * dir
        if self.floored:
            if dir == 1:
                self.direction = "droite"
                self.action = 'walk'
            elif dir == -1:
                self.direction = "gauche"
                self.action = 'walk'
            else: self.action = "idle"
        else:
            if dir == 1:
                self.direction = "droite"
                self.action = 'fall'
            elif dir == -1:
                self.direction = "gauche"
                self.action = 'fall'
            else: self.action = "fall"

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
        
        self.rect.x = constrain(self.rect.x, -20, 1920-130)
        
        if not self.floored:
            self.rect = self.rect.move(0,self.y_vel)
            self.y_vel += 0.7

    def collideDieZone(self, colliders):
        proj = Sprt(self.rect, (self.y_vel,0))
        collist = pygame.sprite.spritecollide(proj, colliders, False)
        if collist:
            return False
        else: return True
    
    def isFloored(self,other):
        d = abs(self.rect.bottom - other.rect.top)
        m = math.ceil(self.y_vel)
        if m != 0 and d%m == 0:
            m = m+1
        self.projF = self.rect.move(0,m)
        if self.projF.colliderect(other):
            if other.rect.top > self.rect.bottom:
                self.floored = True
                self.rect.bottom = other.rect.top
                self.lastFloor = other
        else: self.floored = False

# --------------------------------- # }


# FONCTION
# --------------------------------- # {

def get_background(image):
    """ Récupère les tiles et l'image de fond. """
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
    image = pygame.image.load(join("assets\\louvre.jpg"))
    background, bg_image = get_background(image)
    dessiner(ecran, background, bg_image)
    pygame.display.flip() 

    """ Crée un joueur, un train et un sol """
    sol = CollideZone(0,1000, 1920, 10) # Crée un sol
    collidezone = CollideZone(890,390, 200, 180)
    collidezones = pygame.sprite.Group(collidezone)
    # Boucle principale du jeu

    joueur = Joueur(150, 800) # Crée un joueur
    
    allsprites = pygame.sprite.Group(sol,joueur, collidezone)
    actime = pygame.time.get_ticks()
    lasttime = 0
    run = True  # Variable de contrôle pour maintenir la boucle de jeu active
    clock = pygame.time.Clock() # Initialisation de l'horloge du jeu pour contrôler le taux de rafraîchissement

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

        # inputs
        plyr_inputs(joueur)
        if actime - lasttime > 30:
            if joueur.direction == 'droite':
                if joueur.action == 'idle' and joueur.floored and joueur.idleAnim.stop:
                    joueur.idleAnim.restart()
                    joueur.image = pygame.transform.scale(joueur.idleAnim.get_imgCourante(), (125, 125))
                elif joueur.action == 'idle' and joueur.floored:
                    joueur.idleAnim.defilement()
                    joueur.image = pygame.transform.scale(joueur.idleAnim.get_imgCourante(), (125, 125))
                elif joueur.action == 'walk' and joueur.floored and joueur.walkAnim.stop:
                    joueur.walkAnim.restart()
                    joueur.image = pygame.transform.scale(joueur.walkAnim.get_imgCourante(), (125, 125))
                elif joueur.action == 'walk' and joueur.floored:
                    joueur.walkAnim.defilement()
                    joueur.image = pygame.transform.scale(joueur.walkAnim.get_imgCourante(), (125, 125))
                elif joueur.fallAnim.stop and joueur.action == 'fall':
                    joueur.fallAnim.restart()
                    joueur.image = pygame.transform.scale(joueur.fallAnim.get_imgCourante(), (125, 125))
                elif joueur.action == 'fall':
                    joueur.fallAnim.defilement()
                    joueur.image = pygame.transform.scale(joueur.fallAnim.get_imgCourante(), (125, 125))
            elif joueur.direction == 'gauche':
                if joueur.action == 'idle' and joueur.floored and joueur.idleAnim.stop:
                    joueur.idleAnim.restart()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.idleAnim.get_imgCourante(), True, False), (125, 125))
                elif joueur.action == 'idle' and joueur.floored:
                    joueur.idleAnim.defilement()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.idleAnim.get_imgCourante(), True, False), (125, 125))
                elif joueur.action == 'walk' and joueur.floored and joueur.walkAnim.stop:
                    joueur.walkAnim.restart()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.walkAnim.get_imgCourante(), True, False), (125, 125))
                elif joueur.action == 'walk' and joueur.floored:
                    joueur.walkAnim.defilement()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.walkAnim.get_imgCourante(), True, False), (125, 125))
                elif joueur.fallAnim.stop and joueur.action == 'fall':
                    joueur.fallAnim.restart()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.fallAnim.get_imgCourante(), True, False), (125, 125))
                elif joueur.action == 'fall':
                    joueur.fallAnim.defilement()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.fallAnim.get_imgCourante(), True, False), (125, 125))
            lasttime = actime


        # Mise à jour de l'écran
        #print(type(background))
        dessiner(ecran, background, bg_image) # Dessine les éléments du jeu sur l'écran
        allsprites.update()
        allsprites.draw(ecran)
        pygame.display.flip() # Met à jour l'écran

        # collisions
        joueur.isFloored(sol)
        if joueur.collideDieZone(collidezones) != True:
            pygame.quit()
            sys.exit()
# --------------------------------- # }


if __name__ == "__main__":
    main(ecran)