import pygame
from os import listdir
from os.path import join

class Anima:
    def __init__(self, routeDossierNom):
        """
        Constructeur de la classe Anima (animation)
        :param routeDossierNom: Route vers le dossier ou l'animation est
        """
        # Condition pour arrété l'animation :
        self.stop = False
        # La route du dossier ou se trouve l'animation :
        self.rtDos = routeDossierNom
        # La liste de tous les noms des images de l'animation :
        self.lstnom = listdir(self.rtDos)
        # la liste de toutes les images de l'animation :
        self.lstImage = [pygame.image.load(join(self.rtDos, self.lstnom[i])) for i in range(len(self.lstnom))]
        # L'image courante de l'animation :
        self.__image = self.lstImage[0]
        # Un dictonaire contenant comme clef les images et comme valeur associative l'image suivante de l'animation :
        self.dictImage = {self.lstImage[i] : self.lstImage[i+1] if i+1<len(self.lstImage) else self.lstImage[0] for i in range(len(self.lstImage))}
        # Une image vide :
        self.vide = pygame.image.load('assets/PlayerAnim/vide.png')

    def defilement(self):
        """Met la prochaine image de l'animation en image courante."""
        if self.stop == False:
            self.__image = self.dictImage[self.__image]

    def restart(self):
        """Met l'image initial de l'animation en image courante."""
        self.stop = False
        self.__image = self.lstImage[0]

    def cacher(self):
        """Met l'image vide en image de l'animation courante."""
        self.stop = True
        self.__image = self.vide

    def get_imgCourante(self):
        """Retourne l'image courante de l'animation."""
        return self.__image
    
if __name__ == '__main__':
    idleAnim = Anima('assets/PlayerAnim/IdlePlayerAnim/')
    image = idleAnim.get_imgCourante()
    print(image)
    idleAnim.defilement()
    image = idleAnim.get_imgCourante()
    print(image)