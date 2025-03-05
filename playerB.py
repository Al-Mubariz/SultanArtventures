import pygame,math,boulette
from pygame.locals import *
GRAVITY = 1
JUMPFORCE = 20
class Player(pygame.sprite.Sprite):
    """on crée un joueur qui herite des propriétés de la class pygame.sprite.Sprite pour heriter des fonctions natives pygame telles que colliderct"""
    def __init__(self,scrn, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((50,50))
        self.image.fill((255,0,255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (200,300)
        self.spd = 10
        self.Yspd = 0
        self.dirX = 0
        self.floored = False
        self.canmoveright = True
        self.canmoveleft = True
        self.lastFloor = pygame.Rect(0,0,0,0)
        self.lastLeft = pygame.Rect(0,0,0,0)
        self.lastRight = pygame.Rect(0,0,0,0)
        self.screen = scrn

    def update(self): 
        """gere les deplacement"""
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            if self.floored:
                self.jump()
        if keys[K_q]:
            if self.canmoveleft:
                self.rect = self.rect.move(-self.spd,0)
                self.dirX = -1
                self.canmoveright = True
        elif keys[K_d]:
            if self.canmoveright:
                self.rect = self.rect.move(self.spd,0)
                self.dirX = 1
                self.canmoveleft = True
        else:
            self.dirX = 0
        constrain(self,20,self.screen.get_width()-20)
        
        if not self.floored:
            self.rect = self.rect.move(0,self.Yspd)
            self.Yspd += GRAVITY
    
    
    def isFloored(self, *others):
        for other in others:
            
            d = abs(self.rect.bottom - other.rect.top)
            m = math.ceil(self.Yspd)
            if m != 0 and d%m == 0:
                m = m+1
            self.projF = self.rect.move(0,m)
            if self.projF.colliderect(other):
                if other.rect.top > self.rect.bottom:
                    self.floored = True
                    self.rect.bottom = other.rect.top
                    #self.lastFloor = other
                    
        #if self.floored and not self.rect.move(0,1).collidelist(others): self.floored = False

    def isKill(self,other):
        d = abs(self.rect.top - other.rect.bottom)
        m = 2
        if m != 0 and d%m == 0:
            m = m+1
        self.projK = self.rect.move(0,-m)
        if self.projK.colliderect(other):
            
            if other.rect.bottom > self.rect.top:
                return True
        return False
    def collideRight(self,other):
        if self.dirX == 1:
            d = abs(self.rect.right - other.rect.left)
            m = math.ceil(self.spd)
            if m != 0 and d%m == 0:
                m = m+1
            self.projR = self.rect.move(m,0)
            if self.projR.colliderect(other):
                if other.rect.left > self.rect.right:  
                    self.rect.right = other.rect.left
                    self.canmoveright = False
                    self.lastRight = other
            elif not self.rect.move(1,0).colliderect(self.lastRight): self.canmoveright = True

    def collideLeft(self,other):
        if self.dirX == -1:
            d = abs(self.rect.left - other.rect.right)
            m = math.ceil(self.spd)
            if m != 0 and d%m == 0:
                m = m+1
            self.projL = self.rect.move(-m,0)
            if self.projL.colliderect(other):
                if other.rect.right < self.rect.left:
                    self.rect.left = other.rect.right
                    self.canmoveleft = False
                    self.lastLeft = other
            elif not self.rect.move(-1,0).colliderect(self.lastLeft): self.canmoveleft = True
    def jump(self):
        self.floored = False
        self.Yspd = -JUMPFORCE
    def checkvictory(self,value):
        if self.rect.bottom <= value:
            return True
    def draw(self,screen):
        pygame.draw.rect(screen,(255,0,255),self.rect)
def constrain(p,xmin,xmax):
    p.rect.x = xmin if p.rect.x<xmin else xmax-p.rect.width if p.rect.x>xmax-p.rect.width else p.rect.x

if __name__ == "__main__":
    p = Player(pygame.surface.Surface((5,5)))
    b = [boulette.Boulette(i*20,20,1,0) for i in range(10)]
    print()
    for bl in b:

        p.isFloored(bl)
    