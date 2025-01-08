import pygame, sys
from button import Button

import main_moha

pygame.init()

SCREEN = pygame.display.set_mode((main_moha.LARGEUR, main_moha.HAUTEUR)) # Crée la fenêtre
pygame.display.set_caption("Menu") # Nom de la fenêtre

BG = pygame.image.load("assets/Background.png") # Background

def get_font(size):
    """ Retourne la police Press-Start-2P dans la taille désirée """
    return pygame.font.Font("assets/font.ttf", size)

def play():
    """ Lance le jeu """
    main_moha.main(main_moha.ecran)

def options():
    """ Options du jeu """
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos() # Position de la souris

        SCREEN.fill("white") # Fond blanc

        OPTIONS_TEXT = get_font(45).render("En Developpement...", True, "Black") # Texte
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260)) # Position du texte
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT) # Affiche le texte

        OPTIONS_BACK = Button(image=None, pos=(640, 460),  # Bouton retour
                            text_input="RETOUR", font=get_font(75), base_color="Black", hovering_color="Green") 

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS) # Change la couleur du texte
        OPTIONS_BACK.update(SCREEN) # Met à jour le bouton

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    """ Menu principal """
    while True:
        
        SCREEN.blit(BG, (0, 0))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MENU PRINCIPAL", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        # Boutons
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250), 
                            text_input="JOUER", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), 
                            text_input="QUITTER", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        
        # Met à jour les boutons
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        # Vérifie les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                    
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                    
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
                    

        pygame.display.update()

main_menu()