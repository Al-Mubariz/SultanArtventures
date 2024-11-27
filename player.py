# Classe Joueur
import pygame

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


   