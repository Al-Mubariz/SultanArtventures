import pygame
import random,sys
from boulette import * 
from playerB import *
def game_over_screen(screen):
    WIDTH, HEIGHT = 1920,1080 
    # Arrête tous les sons lorsque le Game Over apparaît
    pygame.mixer.stop()
    bg_images = [pygame.image.load("assets/paris.jpg")]
    clock = pygame.time.Clock()
    # Utilisation de l'image "Bg egouts .png" comme arrière-plan
    background = bg_images[0]
    # Création d'un overlay semi-transparent (avec canal alpha)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    overlay_y = -HEIGHT
    animation_speed = 20  # Vitesse de glissement (pixels par frame)

    # Animation de glissement de l'overlay depuis le haut
    while overlay_y < 0:
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, overlay_y))
        pygame.display.update()
        overlay_y += animation_speed
        clock.tick(60)

    # Affichage du texte "GAME OVER" et des boutons
    button_width, button_height = 200, 50
    restart_button_rect = pygame.Rect(WIDTH / 2 - button_width - 20, HEIGHT / 2, button_width, button_height)
    quit_button_rect = pygame.Rect(WIDTH / 2 + 20, HEIGHT / 2, button_width, button_height)
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
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(game_over_text, (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2 - 150))
        pygame.draw.rect(screen, (255, 255, 255), restart_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), quit_button_rect)
        restart_text = font_small.render("Restart", True, (0, 0, 0))
        quit_text = font_small.render("Quit", True, (0, 0, 0))
        screen.blit(restart_text, (restart_button_rect.x + (button_width - restart_text.get_width()) / 2,
                                   restart_button_rect.y + (button_height - restart_text.get_height()) / 2))
        screen.blit(quit_text, (quit_button_rect.x + (button_width - quit_text.get_width()) / 2,
                                quit_button_rect.y + (button_height - quit_text.get_height()) / 2))
        pygame.display.update()
        clock.tick(60)

def main():
    # Définir la taille de la fenêtre
    WIDTH, HEIGHT = 1920,1080 
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("niveau boulette")

    bs = pygame.sprite.Group()
    b1 = Boulette(0,WIDTH//2,0,30,bs)
    sols = pygame.sprite.Group()
    sol = Sol(0,screen.get_height()-20, screen.get_width(),20, sols)
    
    p = Player(screen)
    print(sols in sols)

    

    # Définir les couleurs
    WHITE = (255, 255, 255)
    RED = (255,0,0)
    BLUE = (0,0,255)
    GREEN = (0,255,0)

    # Définir les paramètres de la boucle de jeu
    FPS = 30
    clock = pygame.time.Clock()

    # Fonction principale du jeu
    loop = 1
    frame = 0
    seconds = 1
    running = True
    while running:
        # timing d'apparition des boulettes
        frame += 1
        if frame >= FPS :
            seconds+=1
            frame = 0 
        if seconds%loop == 0:
            loop = random.randint(2,7)
            size = random.randint(1,7)
            spd = 9
            # création de nouvelles boulettes selon une distribution gaussienne
            x = random.gauss(screen.get_width()//2,400)
            x = constrained(x,20,screen.get_width()-20) # evite de sortir de l'ecran/poubelle
            bs.add(Boulette(x,-50,spd,size))
            sols.add(bs)
            
            
        
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                sys.exit()

        # Remplir l'écran avec une couleur
        screen.fill(WHITE)
        # on affiche le sol et on gere les fonctions de tous les sprites
        sol.draw(screen)
        #p.isFloored(sol)
        for b in sols.sprites():
            p.isFloored(b)
        
        for b in bs.sprites():# check si les sprites sont au sol
            b.isFloored(sol)
            for bb in bs:
                if bb != b != p:
                    b.isFloored(bb)
            if b != p:
                # collisions
                p.collideRight(b)
                p.collideLeft(b)

                if p.isKill(b): # event mort
                    running = False
        # on met a jour les variables puis on affiche les sprites
        """if p.checkvictory(0):
            running ==  False"""
        bs.update()
        p.update()
        bs.draw(screen)
        p.draw(screen)
        
        
        # Mettre à jour l'affichage
        pygame.display.flip()

        # Limiter la vitesse de la boucle à 60 FPS
        clock.tick(FPS)

    
    if not p.checkvictory(0):
        choice = game_over_screen(screen)
        if choice == "restart":
            main()  # Redémarrage
        else:
            pygame.quit()
            sys.exit()
    else:
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    main()