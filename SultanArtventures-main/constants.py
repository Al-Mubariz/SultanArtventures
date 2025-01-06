import pygame

# constantes 

LARGEUR, HAUTEUR = 1000, 700
FPS = 60
VITESSE_JOUEUR = 5
VITESSE_TRAIN = 20
JUMPFORCE = 30
GRAVITE = 1
WHITE, BLACK, RED, BLUE, GREEN= (255,255,255),(0,0,0),(255,0,0),(0,0,255),(0,255,0)

# fonctions
def constrain(var, minV, maxV): 
    """on regarde si la variable var est entre minV et maxV sinon on renvoie minV ou maxV"""
    if var > maxV:
        return maxV
    if var < minV:
        return minV
    else:
        return var


# classes
class Sprt(pygame.sprite.Sprite):
    """classe qui sert pour faire des sprites qui servent seulement a des fonctions internes (non visibles)"""
    def __init__(self,rect,mv, *groups):
        super().__init__(*groups)
        self.rect = rect.move(mv)
        self.image = pygame.surface.Surface((1,1))



# assets
# on mettra les imports d'image ici, tout est importé ensuite sur les autres fichiers
