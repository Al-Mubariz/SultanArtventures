#README
#Introduisez dans votre programme les variables suivantes : game_over_bg = pygame.image.load("fond_sans_g_o.png").convert_alpha() et game_over_fg = pygame.image.load("g_o.png").convert_alpha()

def game_over_screen():
    # Arrête tous les sons et la musique d'ambiance actuelle
    pygame.mixer.stop()
    clock = pygame.time.Clock()

    # On conserve le background figé (par exemple, le background des egouts)
    background = bg_images[0]

    # On suppose que ces images ont été chargées préalablement dans le code :
    # game_over_bg et game_over_fg
    # On prépare game_over_bg avec une opacité réduite (60 % ≈ 153 sur 255)
    game_over_bg_alpha = game_over_bg.copy()
    game_over_bg_alpha.set_alpha(215)

    # Initialisation de la position de départ pour le sliding (hors de l'écran en haut)
    slide_y = -HEIGHT
    animation_speed = 25  # Vitesse plus lente pour le sliding

    # Animation du sliding des images Game Over depuis le haut
    while slide_y < 0:
        screen.blit(background, (0, 0))
        screen.blit(game_over_bg_alpha, (0, slide_y))
        screen.blit(game_over_fg, (0, slide_y))
        pygame.display.update()
        slide_y += animation_speed
        clock.tick(60)

    # Préparation des boutons de Restart et Quit
    button_width, button_height = 200, 50
    restart_button_rect = pygame.Rect(WIDTH / 2 - button_width - 20, HEIGHT / 2, button_width, button_height)
    quit_button_rect = pygame.Rect(WIDTH / 2 + 20, HEIGHT / 2, button_width, button_height)
    font_small = pygame.font.Font(None, 40)

    # Boucle d'affichage finale du Game Over sans le texte "GAME OVER"
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
        screen.blit(game_over_bg_alpha, (0, 0))
        screen.blit(game_over_fg, (0, 0))
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
