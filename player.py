# Classe Joueur
import pygame


class Joueur(pygame.sprite.Sprite):
    COULEUR = (255,0,0) # Couleur du joueur

    def __init__(self, x, y, largeur, hauteur, jumpforce): 
        """
        Constucteur de la classe Joueur, qui prend pour paramètres les coordonnées x et y du joueur, ainsi que sa largeur et sa hauteur. 
        (tsais les trucs que Mr Djahnit veut qu'on mette dans le constructeur)
        """
        self.jumpforce = jumpforce
        self.rect= pygame.Rect(x, y, largeur, hauteur) # Crée un rectangle pour le joueur
        self.x_vitesse = 0  # Vitesse de déplacement du joueur
        self.y_vel = 0
        self.direction = "gauche" # Direction du joueur
        self.compteur_animation = 0 # Compteur pour l'animation du joueur
        self.floored = False

    def mouvement(self, dx):
        self.rect.x += dx # Ajoute la vitesse de déplacement à la vitesse actuelle


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
        pygame.draw.rect(ecran, self.COULEUR, self.rect)

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
    
    def update(self, grav):
        """
        Met à jour la position verticale du joueur en fonction de la gravité.
        Args:
            grav (float): La valeur de la gravité à appliquer à la vitesse verticale du joueur.
        Attributs modifiés:
            self.lastY (int): La dernière position verticale du joueur.
            self.y_vel (float): La vitesse verticale du joueur, augmentée par la gravité.
            self.rect.y (int): La nouvelle position verticale du joueur, ajustée en fonction de la vitesse verticale.
        """

        self.lastY = self.rect.y
        self.y_vel+= grav
        
        if self.floored:
            self.rect.y = self.lastY
        else:
            self.rect.y += self.y_vel

    def collideSol(self, sol):
        """
        Vérifie si le joueur entre en collision avec le sol.
        Cette méthode déplace le rectangle de collision du joueur de 5 pixels vers la droite
        et vérifie s'il entre en collision avec le rectangle du sol. Si une collision est détectée,
        l'attribut 'floored' du joueur est défini sur True, sinon il est défini sur False.
        Args:
            sol (pygame.Rect): Le rectangle représentant le sol avec lequel vérifier la collision.
        """

        
        proj = self.rect.move(5,0)
        if proj.colliderect(sol):
            self.floored = True
        else: self.floored = False




   