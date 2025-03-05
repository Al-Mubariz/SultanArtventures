import pygame,math
pygame.init()
class Boulette(pygame.sprite.Sprite):
    """crée un objet boulette, carré de 20*size en (x,y)"""
    def __init__(self,x,y,spd,size: int, *groups):
        super().__init__(*groups)
        self.image = pygame.surface.Surface((size*20,size*20))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.floored = False
        self.spd = spd

    def update(self):
        """mise a jour de la position"""
        if not self.floored:
            self.rect.y += self.spd
        
    def isFloored(self,other):
        """test de collision avec le sol"""
        d = abs(self.rect.bottom - other.rect.top)
        m = math.ceil(self.spd)
        if m != 0 and d%m == 0:
            m += 1
        
        self.proj = self.rect.move(0,m)

        if self.proj.colliderect(other)and other.rect.left <= self.rect.centerx <= other.rect.right:
            
            if other.rect.top > self.rect.bottom:
                self.rect.bottom = other.rect.top
                self.floored = True
                
    



class Sol(pygame.sprite.Sprite):
    """crée un objet de type sol """
    def __init__(self,x,y,w,h, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((w,h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    def draw(self,screen):
        pygame.draw.rect(screen,(0,0,255),self.rect)
        
def constrained(x,mini,maxi):
    return maxi if x > maxi else mini if x < mini else x

if __name__ == "__main__":
    print(constrained(8,2,10))
    print(constrained(1,2,10))
    print(constrained(11,2,10))
