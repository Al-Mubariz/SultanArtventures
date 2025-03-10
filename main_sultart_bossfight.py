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
        self.image = pygame.surface.Surface((w, h), pygame.SRCALPHA) #Crée une image invisible à la bonne taille
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
        self.idleAnim = Anima('assets/PlayerAnim/IdlePlayerAnim1/')
        self.walkAnim = Anima('assets/PlayerAnim/WalkPlayerAnim1/')
        self.image = self.idleAnim.get_imgCourante().convert_alpha() # a remplacer par la vrai image a terme
        self.image = pygame.transform.scale(self.image, (200, 200)) 
        self.rect = self.image.get_rect() # Crée un rectangle pour le joueur
        self.rect = self.rect.scale_by(0.985)
        self.rect.topleft = (x,y) # on le positionne

        self.jumpforce = 36.5
        self.x_vel = 0  # Vitesse de déplacement du joueur
        self.y_vel = 0
        self.direction = "droite" # Direction du joueur
        self.action = 'idle'
        self.compteur_animation = 0 # Compteur pour l'animation du joueur
        self.floored = False

    def mouvement(self, dir):
        """dx est la vitesse et dir est la direction (1 pour la droite et _1 pour la gauche)"""
        self.rect.x += 10 * dir # Ajoute la vitesse de déplacement à la vitesse actuelle
        if dir == 1:
            self.direction = "droite"
            self.action = 'walk'
        elif dir == -1:
            self.direction = "gauche"
            self.action = 'walk'
        else: self.action = "idle"

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
            self.y_vel += 1.7

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


def intervalle(a,b,pas):return[a+((b-a)/pas)*i for i in range(pas+1)]


def game_over_screen(joueur, bg_image):
    # Arrête tous les sons lorsque le Game Over apparaît
    pygame.mixer.stop()

    clock = pygame.time.Clock()
    # Utilisation de l'image "Bg egouts .png" comme arrière-plan
    background = bg_images = pygame.image.load("assets\\bossfight\\frame0000.jpg")
    # Création d'un overlay semi-transparent (avec canal alpha)
    overlay = pygame.Surface((1920, 1080), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    overlay_y = -1080
    animation_speed = 20  # Vitesse de glissement (pixels par frame)

    # Animation de glissement de l'overlay depuis le haut
    while overlay_y < 0:
        ecran.blit(background, (0, 0))
        ecran.blit(overlay, (0, overlay_y))
        pygame.display.update()
        overlay_y += animation_speed
        clock.tick(60)

    # Affichage du texte "GAME OVER" et des boutons
    button_width, button_height = 200, 50
    restart_button_rect = pygame.Rect(1920 / 2 - button_width - 20, 1080 / 2, button_width, button_height)
    quit_button_rect = pygame.Rect(1920 / 2 + 20, 1080 / 2, button_width, button_height)
    font_big = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 40)
    game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button_rect.collidepoint(mouse_pos):
                    return "restart"
                elif quit_button_rect.collidepoint(mouse_pos):
                    return "quit"
        ecran.blit(background, (0, 0))
        ecran.blit(overlay, (0, 0))
        ecran.blit(game_over_text, (1920 / 2 - game_over_text.get_width() / 2, 1080 / 2 - 150))
        pygame.draw.rect(ecran, (255, 255, 255), restart_button_rect)
        pygame.draw.rect(ecran, (255, 255, 255), quit_button_rect)
        restart_text = font_small.render("Restart", True, (0, 0, 0))
        quit_text = font_small.render("Quit", True, (0, 0, 0))
        ecran.blit(restart_text, (restart_button_rect.x + (button_width - restart_text.get_width()) / 2,
                                   restart_button_rect.y + (button_height - restart_text.get_height()) / 2))
        ecran.blit(quit_text, (quit_button_rect.x + (button_width - quit_text.get_width()) / 2,
                                quit_button_rect.y + (button_height - quit_text.get_height()) / 2))
        pygame.display.update()
        clock.tick(60)


def main(ecran):
    """
    Fonction principale pour exécuter la boucle de jeu.
    
    Paramètres:
    ecran (pygame.Surface): La surface sur laquelle le jeu sera dessiné.
    """
    image = pygame.image.load(join("assets\\chargementbg.jpg"))
    background, bg_image = get_background(image)
    dessiner(ecran, background, bg_image)
    pygame.display.flip() 

    bckg = Anima("assets\\bossfight")
    """ Crée un joueur, un train et un sol """
    diezone = CollideZone()
    diezone1 = CollideZone()
    sol = CollideZone(0,HAUTEUR-45, 1920, 20) # Crée un sol
    
    game(ecran, bckg, diezone, diezone1, sol)


def game(ecran, bckg, diezone, diezone1, sol):
    # Boucle principale du jeu
    joueur = Joueur(200, 200) # Crée un joueur
    diezones = pygame.sprite.Group()
    diezones.add(diezone)
    diezones.add(diezone1)
    
    allsprites = pygame.sprite.Group(sol,joueur, diezones)
    actime = pygame.time.get_ticks()
    lasttime = 0
    bosstime = 317 * 2
    indice = 0
    run = True  # Variable de contrôle pour maintenir la boucle de jeu active
    clock = pygame.time.Clock() # Initialisation de l'horloge du jeu pour contrôler le taux de rafraîchissement
    bckg.restart()
    background, bg_image = get_background(bckg.get_imgCourante())


    while run:
        clock.tick(FPS) # Limite le taux de rafraîchissement à la valeur de FPS (frames per second)

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
        plyr_inputs(joueur) # Déplace le joueur en fonction des touches du clavier appuyées
        # Mise à jour des animation
        if actime - lasttime > 60:
            if joueur.direction == 'droite':
                if joueur.action == 'idle' and joueur.floored and joueur.idleAnim.stop:
                    joueur.idleAnim.restart()
                    joueur.image = pygame.transform.scale(joueur.idleAnim.get_imgCourante(), (220, 220))
                elif joueur.action == 'idle' and joueur.floored:
                    joueur.idleAnim.defilement()
                    joueur.image = pygame.transform.scale(joueur.idleAnim.get_imgCourante(), (220, 220))
                if joueur.action == 'walk' and joueur.floored and joueur.walkAnim.stop:
                    joueur.walkAnim.restart()
                    joueur.image = pygame.transform.scale(joueur.walkAnim.get_imgCourante(), (220, 220))
                elif joueur.action == 'walk' and joueur.floored:
                    joueur.walkAnim.defilement()
                    joueur.image = pygame.transform.scale(joueur.walkAnim.get_imgCourante(), (220, 220))
            elif joueur.direction == 'gauche':
                if joueur.action == 'idle' and joueur.floored and joueur.idleAnim.stop:
                    joueur.idleAnim.restart()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.idleAnim.get_imgCourante(), True, False), (220, 220))
                elif joueur.action == 'idle' and joueur.floored:
                    joueur.idleAnim.defilement()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.idleAnim.get_imgCourante(), True, False), (220, 220))
                if joueur.action == 'walk' and joueur.floored and joueur.walkAnim.stop:
                    joueur.walkAnim.restart()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.walkAnim.get_imgCourante(), True, False), (220, 220))
                elif joueur.action == 'walk' and joueur.floored:
                    joueur.walkAnim.defilement()
                    joueur.image = pygame.transform.scale(pygame.transform.flip(joueur.walkAnim.get_imgCourante(), True, False), (220, 220))
            if indice > 0 and bosstime > 0:
                indice = 0
                bosstime -=1
                bckg.defilement()
                background, bg_image = get_background(bckg.get_imgCourante())
            indice += 1
            lasttime = actime

        diezone.set_size(0, 0)
        diezone1.set_size(0, 0)
        if 317*2 - bosstime >= 36*2 and 317*2 - bosstime <= 68*2:
            inter = intervalle(0, 1600, 68*2-36*2)
            diezone.set_size(120, 250)
            diezone.set_pos(inter[-(317*2 - bosstime -35*2 -1)], 400)
        if 317*2 - bosstime >= 86*2 and 317*2 - bosstime <= 103*2:
            inter = intervalle(-50, 1900, 103*2-86*2)
            diezone.set_size(250, 250)
            diezone.set_pos(inter[317*2 - bosstime -86*2], 400)
        if 317*2 - bosstime >= 124*2 and 317*2 - bosstime <= 140*2:
            inter = intervalle(-50, 1400, 140*2-124*2)
            diezone.set_size(250, 250)
            diezone.set_pos(inter[-(317*2 - bosstime -123*2 -1)], 400)
        if 317*2 - bosstime >= 168*2 and 317*2 - bosstime <= 174*2:
            inter = intervalle(200, 950, 174*2-168*2)
            inter1 = intervalle(950, 1620, 174*2-168*2)
            diezone.set_size(120, 250)
            diezone1.set_size(120, 250)
            diezone.set_pos(inter[317*2 - bosstime -168*2], 400)
            diezone1.set_pos(inter1[-(317*2 - bosstime -167*2 -1)], 400)
        if 317*2 - bosstime >= 192*2 and 317*2 - bosstime <= 198*2:
            inter = intervalle(-20, 1500, 140*2-124*2)
            diezone.set_size(600, 100)
            diezone.set_pos(1200, inter[317*2 - bosstime -192*2])
        if 317*2 - bosstime >= 198*2 and 317*2 - bosstime <= 203*2:
            inter = intervalle(0, 600, 203*2-198*2)
            diezone.set_size(600, 100)
            diezone.set_pos(1200, inter[-(317*2 - bosstime -197*2 -1)])
        if 317*2 - bosstime >= 207*2 and 317*2 - bosstime <= 212*2:
            inter = intervalle(-20, 600, 212*2-207*2)
            diezone.set_size(500, 100)
            diezone.set_pos(250, inter[317*2 - bosstime -207*2])
        if 317*2 - bosstime >= 212*2 and 317*2 - bosstime <= 217*2:
            inter = intervalle(0, 600, 217*2-212*2)
            diezone.set_size(500, 100)
            diezone.set_pos(250, inter[-(317*2 - bosstime -211*2 -1)])
        if 317*2 - bosstime >= 221*2 and 317*2 - bosstime <= 230*2:
            inter = intervalle(-20, 600, 230*2-221*2)
            diezone.set_size(500, 100)
            diezone1.set_size(500, 100)
            diezone.set_pos(250, inter[317*2 - bosstime -221*2])
            diezone1.set_pos(1200, inter[317*2 - bosstime -221*2])
        if 317*2 - bosstime >= 230*2 and 317*2 - bosstime <= 237*2:
            inter = intervalle(0, 600, 237*2-230*2)
            inter1 = intervalle(0, 600, 237*2-230*2)
            diezone.set_size(500, 100)
            diezone1.set_size(500, 100)
            diezone.set_pos(250, inter[-(317*2 - bosstime -229*2 -1)])
            diezone1.set_pos(1200, inter1[-(317*2 - bosstime -229*2 -1)])
        if 317*2 - bosstime >= 249*2 and 317*2 - bosstime <= 261*2:
            inter = intervalle(100, 950, 261*2-249*2)
            inter1 = intervalle(950, 1600, 261*2-249*2)
            diezone.set_size(120, 250)
            diezone1.set_size(120, 250)
            diezone.set_pos(inter[317*2 - bosstime -249*2], 400)
            diezone1.set_pos(inter1[-(317*2 - bosstime -248*2 -1)], 400)

        # Mise à jour de l'écran
        #print(type(background))
        dessiner(ecran, background, bg_image) # Dessine les éléments du jeu sur l'écran
        allsprites.update()
        allsprites.draw(ecran)
        pygame.display.flip() # Met à jour l'écran

        # collisions
        
        joueur.isFloored(sol)
        if joueur.collideDieZone(diezones):
            run = True
        else:
            run = False

    
    choice = game_over_screen(joueur, bg_image)
    if choice == "restart":
        game(ecran, bckg, diezone, diezone1, sol)  # Redémarrage
    else:
        pygame.quit()
        sys.exit()

# --------------------------------- # }


if __name__ == "__main__":
    main(ecran)