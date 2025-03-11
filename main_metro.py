import pygame
import sys
import random

pygame.init()
pygame.mixer.init()

# Info de l'écran
screen_info = pygame.display.Info()
LARGEUR_ECRAN = screen_info.current_w
HAUTEUR_ECRAN = screen_info.current_h
HAUTEUR_SOL = (7 * HAUTEUR_ECRAN) // 27

# Affichage
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Sons
son_ambiant = pygame.mixer.Sound('assets/metro/ambiant.wav')
son_alerte_train = pygame.mixer.Sound('assets/metro/claxon.wav')

# Images
image_train = pygame.image.load('assets/metro/train.png').convert_alpha()


game_over_bg_img = pygame.image.load('fond_sans_g_o.png').convert_alpha()
game_over_bg_img = pygame.transform.scale(game_over_bg_img, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
game_over_bg_img.set_alpha(204)  # Opacité à 80%

img_game_over = pygame.image.load('g_o.png').convert_alpha()


# Initialiser l'état de l'animation de fin de jeu :
mort_anim_timer = 0  # en secondes
boutons_game_over_actifs = False

class Joueur:
    def __init__(self):
        """
        Initialise une instance du joueur.
        Attributs:
            width (int): La largeur du joueur.
            original_height (int): La hauteur originale du joueur.
            height (int): La hauteur actuelle du joueur, initialisée à original_height.
            jump_force (int): La force appliquée lors d'un saut.
            gravity (int): La valeur de la gravité influant sur le joueur.
            x (int): La position horizontale initiale du joueur, centrée sur l'écran.
            base_y (int): La position verticale de base pour que le joueur soit correctement positionné sur le sol.
            y (int): La position verticale actuelle du joueur, initialisée à base_y.
            vel_y (int): La vitesse verticale actuelle du joueur.
            jumps_left (int): Le nombre de sauts restants (pour le double jump).
            direction (int): La direction actuelle du mouvement du joueur(-1 pour gauche, 1 pour droite.)
            current_speed (int): La vitesse de déplacement actuelle du joueur.
            is_grounded (bool): Indique si le joueur est en contact avec le sol.
            is_alive (bool): Indique si le joueur est en vie.
            on_train (NoneType ou autre): Si le joueur est sur un train.
            offset_x (int): Décalage horizontal appliqué au joueur.
            sprint_amount (float): Durée maximale de sprint autorisée (en secondes).
            is_sprinting (bool): Indique si le joueur est en train de sprinter.
            original_frames (list): Liste d'images pour l'animation originale du joueur, chargées depuis le dossier 'assets/metro'.
            idle_frames (list): Liste d'images pour l'animation d'idle du joueur, chargées depuis 'assets/PlayerAnim/IdlePlayerAnimMoha'.
            walk_frames (list): Liste d'images pour l'animation de marche du joueur, chargées depuis 'assets/PlayerAnim/WalkPlayerAnimMoha'.
            current_frame (int): Indice de la frame actuellement affichée dans l'animation.
            animation_timer (float): Chronomètre servant à contrôler le temps entre les frames d'animation.
            animation_speed (float): Temps en secondes entre chaque frame de l'animation.
            current_anim (str): État actuel de l'animation (par exemple, "idle" pour l'attente).
        """
        
        self.width = 100
        self.original_height = 100
        self.height = self.original_height
        self.jump_force = 27
        self.gravity = 1
        self.x = LARGEUR_ECRAN // 2
        self.base_y = HAUTEUR_ECRAN - HAUTEUR_SOL - self.original_height
        self.y = self.base_y
        self.vel_y = 0
        self.jumps_left = 2
        self.direction = 1
        self.current_speed = 0
        self.is_grounded = True
        self.is_alive = True
        self.on_train = None
        self.offset_x = 0
        self.sprint_amount = 5.0  # Max 5 secondes de sprint
        self.is_sprinting = False

        # Chargement des frames
        self.original_frames = [pygame.transform.scale(
            pygame.image.load(f'assets/metro/player{i}.png').convert_alpha(),
            (self.width, self.original_height)
        ) for i in range(1, 12)]

        # Frames d'attente et de marche
        self.idle_frames = [pygame.transform.scale(
            pygame.image.load(f'assets/PlayerAnim/IdlePlayerAnimMoha/IdlePlayerAnim{str(i).zfill(4)}.png').convert_alpha(),
            (self.width, self.original_height)
        ) for i in range(21)]
        self.walk_frames = [pygame.transform.scale(
            pygame.image.load(f'assets/PlayerAnim/WalkPlayerAnimMoha/WalkPlayerAnim{str(i).zfill(4)}.png').convert_alpha(),
            (self.width, self.original_height)
        ) for i in range(21)]

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08  # Temps entre les frames en secondes
        self.current_anim = "idle"

    def reset(self):
        """
        Réinitialise l'état du joueur pour rejouer.
        """
        self.x = LARGEUR_ECRAN // 2
        self.y = self.base_y
        self.vel_y = 0
        self.jumps_left = 2
        self.is_grounded = True
        self.is_alive = True
        self.on_train = None
        self.offset_x = 0
        self.height = self.original_height
        self.direction = 1
        self.sprint_amount = 5.0
        self.is_sprinting = False
        self.current_frame = 0
        self.animation_timer = 0

    def handle_input(self, keys):
        """
        Gère les entrées clavier pour déplacer le joueur et gérer les sauts.
        Args:
            keys (dict): Dictionnaire contenant les touches actuellement pressées.
        """
        prev_height = self.height
        self.is_sprinting = False
        self.current_speed = 0

        # Gestion des mouvements avec sprint
        if keys[pygame.K_d]:
            if keys[pygame.K_LCTRL] and self.sprint_amount > 0:
                self.current_speed = 10  # vitesse de sprint
                self.is_sprinting = True
            else:
                self.current_speed = 5   # vitesse de marche normale
            self.direction = 1
        elif keys[pygame.K_q]:
            if keys[pygame.K_LCTRL] and self.sprint_amount > 0:
                self.current_speed = -10  # vitesse de sprint à gauche
                self.is_sprinting = True
            else:
                self.current_speed = -5   # vitesse de marche à gauche
            self.direction = -1

    def update_sprint(self, dt):
        """
        Met à jour l'état du sprint du joueur.
        Args:
            dt (float): Temps écoulé depuis la dernière frame en secondes.
        """
        if self.is_sprinting and self.sprint_amount > 0:
            self.sprint_amount -= dt
        elif self.sprint_amount < 5:
            self.sprint_amount += dt  # Régénérer le sprint lorsqu'il ne sprint pas
        self.sprint_amount = max(0, min(self.sprint_amount, 5))

    def sauter(self):
        """
        Gère le saut du joueur.
        """
        if self.jumps_left > 0 and self.is_alive:
            self.vel_y = -self.jump_force
            self.jumps_left -= 1

    def update(self, dt):
        """
        Met à jour l'état du joueur en fonction du temps écoulé.
        args:
            dt (float): Temps écoulé depuis la dernière frame en secondes.
        """
        was_grounded = self.is_grounded
        self.vel_y += self.gravity
        self.y += self.vel_y

        ground_position = HAUTEUR_ECRAN - HAUTEUR_SOL - self.height
        if self.y >= ground_position:
            self.is_grounded = True
            self.y = ground_position
            self.vel_y = 0
            self.jumps_left = 2
            self.on_train = None
        else:
            self.is_grounded = False

        if was_grounded and not self.is_grounded:
            self.on_train = None

        # Sélection de l'animation en fonction de l'état
        if self.current_speed == 0:
            desired = "idle"
            frame_list = self.idle_frames
        else:
            desired = "walk"
            frame_list = self.walk_frames

        if self.current_anim != desired:
            self.current_anim = desired
            self.current_frame = 0
            self.animation_timer = 0
        else:
            self.animation_timer += dt
            effective_speed = self.animation_speed
            if desired == "walk" and self.is_sprinting and self.sprint_amount > 0:
                effective_speed /= 3
            if self.animation_timer >= effective_speed:
                self.current_frame = (self.current_frame + 1) % len(frame_list)
                self.animation_timer = 0

    def draw(self, ecran):
        """
        Dessine le joueur sur l'écran.
        Args:
            ecran (pygame.Surface): La surface sur laquelle on va dessiner le joueur.
        """
        # Sélectionner les frames en fonction de l'état d'animation actuel
        if self.current_anim == "idle":
            frames = self.idle_frames
        elif self.current_anim == "walk":
            frames = self.walk_frames
        else:
            frames = self.idle_frames
        current_image = frames[self.current_frame % len(frames)]
        flipped_img = pygame.transform.flip(current_image, self.direction == -1, False)
        ecran.blit(flipped_img, (self.x, self.y))


def dessiner_barre_sprint(ecran, sprint_amount):
    """
    Dessine la barre de sprint sur l'écran.
    Args:
        ecran (pygame.Surface): La surface sur laquelle on va dessiner la barre de sprint.
        sprint_amount (float): La quantité de sprint restante (de 0 à 5).
    """
    bar_width = 200
    bar_height = 20
    bar_x = (LARGEUR_ECRAN - bar_width) // 2
    bar_y = HAUTEUR_ECRAN - 50
    
    # Dessiner la barre de fond de sprinte
    pygame.draw.rect(ecran, (20, 21, 23), (bar_x, bar_y, bar_width, bar_height))
    
    # Dessiner la barre de sprint restante
    remaining_width = (sprint_amount / 5) * bar_width
    pygame.draw.rect(ecran, (20, 138, 255), (bar_x, bar_y, remaining_width, bar_height))
    
class TrainDeDroite:
    def __init__(self, speed):
        """
        Initialise une instance de train se déplaçant de droite à gauche.
        Args:
            speed (int): La vitesse de déplacement du train.
        
        Attributs:
            width (int): La largeur du train.
            height (int): La hauteur du train.
            x (int): La position horizontale du train.
            y (int): La position verticale du train.
            speed (int): La vitesse de déplacement du train.
            image (pygame.Surface): L'image du train.
            front_hitbox (pygame.Rect): La hitbox frontale du train.
            top_hitbox (pygame.Rect): La hitbox supérieure du train (le toit).    
            sound_channel (pygame.mixer.Channel): Le canal de son pour le claxon du train.
    """ 
        self.width = 7125
        self.height = 590
        self.x = LARGEUR_ECRAN
        self.y = HAUTEUR_ECRAN - HAUTEUR_SOL - self.height
        self.speed = speed
        self.image = pygame.transform.scale(image_train, (self.width, self.height))
        # Initialize front hitbox with temporary values, updated in update()
        self.front_hitbox = pygame.Rect(0, self.y + 50, 0, self.height - 100)
        self.top_hitbox = pygame.Rect(self.x, self.y, self.width, 10)
        self.sound_channel = None

    def update(self):
        """
        Met à jour la position du train et les hitboxes.
        Retourne:
            bool: True si le train est sorti de l'écran, False sinon.
        """
        self.x -= self.speed
        # Update front hitbox to cover the area swept this frame
        self.front_hitbox.x = self.x + 50 - self.speed  # Previous position
        self.front_hitbox.width = self.speed  # Width equals distance moved
        self.front_hitbox.y = self.y + 50
        self.front_hitbox.height = self.height - 100
        # Update top hitbox
        self.top_hitbox.x = self.x
        self.top_hitbox.y = self.y
        return self.x + self.width < 0

    def draw(self, ecran):
        """
        Dessine le train sur l'écran.
        Args:
            ecran (pygame.Surface): La surface sur laquelle on va dessiner le train
        """
        ecran.blit(self.image, (self.x, self.y))

class TrainDeGauche:
    def __init__(self, speed):
        """
        Initialise une instance de train se déplaçant de gauche à droite.
        Args:
            speed (int): La vitesse de déplacement du train.
            
            Attributs:
            width (int): La largeur du train.
            height (int): La hauteur du train.  
            x (int): La position horizontale du train.
            y (int): La position verticale du train.
            speed (int): La vitesse de déplacement du train.
            image (pygame.Surface): L'image du train.
            front_hitbox (pygame.Rect): La hitbox frontale du train.
            top_hitbox (pygame.Rect): La hitbox supérieure du train (le toit).
            sound_channel (pygame.mixer.Channel): Le canal de son pour le claxon du train.
"""
        self.width = 7125
        self.height = 590
        self.x = -self.width
        self.y = HAUTEUR_ECRAN - HAUTEUR_SOL - self.height
        self.speed = speed
        self.image = pygame.transform.flip(
            pygame.transform.scale(image_train, (self.width, self.height)),
            True, False
        )
        # Initialise la hitbox frontale avec des valeurs qui sont temporaires, elles sont mises à jour dans update()
        self.front_hitbox = pygame.Rect(0, self.y + 50, 0, self.height - 100)
        self.top_hitbox = pygame.Rect(self.x, self.y, self.width, 10)
        self.sound_channel = None

    def update(self):
        """
        Met à jour la position du train et les hitboxes.
        Retourne:
            bool: True si le train est sorti de l'écran, False sinon.
        """
        self.x += self.speed
        previous_right_edge = (self.x - self.speed) + self.width
        self.front_hitbox.x = previous_right_edge
        self.front_hitbox.width = self.speed
        self.front_hitbox.y = self.y + 50
        self.front_hitbox.height = self.height - 100

        # On update la hitbox du haut
        self.top_hitbox.x = self.x
        self.top_hitbox.y = self.y

        return self.x > LARGEUR_ECRAN

    def draw(self, ecran):
        """
        Dessine le train sur l'écran.
        Args:
            ecran (pygame.Surface): La surface sur laquelle on va dessiner le train.
        """
        ecran.blit(self.image, (self.x, self.y))

class TrainManager:
    def __init__(self):
        """
        Initialise le gestionnaire de trains.
        Attributs:
            trains (list): Liste des trains se déplaçant de droite à gauche.
            right_trains (list): Liste des trains se déplaçant de gauche à droite.
            base_speed (int): La vitesse de déplacement de base des trains.
            right_train_speed (int): La vitesse de déplacement initiale des trains de gauche à droite.
            spawn_timer (int): Le temps en millisecondes avant l'apparition du prochain train de droite à gauche.
            right_spawn_timer (int): Le temps en millisecondes avant l'apparition du prochain train de gauche à droite.
            next_left_spawn_time (int): L'heure à laquelle le prochain train de droite à gauche doit apparaître.
            next_right_spawn_time (int): L'heure à laquelle le prochain train de gauche à droite doit apparaître.
            left_claxon_started (bool): Indique si le claxon du train de droite à gauche a commencé.
            right_claxon_started (bool): Indique si le claxon du train de gauche à droite a commencé.
            left_claxon_channel (pygame.mixer.Channel): Le canal de son pour le claxon du train de droite à gauche.
            right_claxon_channel (pygame.mixer.Channel): Le canal de son pour le claxon du train de gauche à droite.
            ambient_playing (bool): Indique si le son ambiant est actuellement en cours de lecture.
            """
        self.trains = []
        self.right_trains = []
        self.base_speed = 50
        self.right_train_speed = 50  # Initial right train speed
        self.spawn_timer = random.randint(2000, 10000)
        self.right_spawn_timer = random.randint(2000, 15000)
        self.next_left_spawn_time = pygame.time.get_ticks() + self.spawn_timer
        self.next_right_spawn_time = pygame.time.get_ticks() + self.right_spawn_timer
        self.left_claxon_started = False
        self.right_claxon_started = False
        self.left_claxon_channel = None
        self.right_claxon_channel = None
        self.ambient_playing = False

    def reset(self):
        """
        Réinitialise l'état du gestionnaire de trains pour rejouer.
        """
        self.trains = []
        self.right_trains = []
        self.base_speed = 50
        self.right_train_speed = 50  # Reset right train speed
        self.spawn_timer = random.randint(2000, 10000)
        self.right_spawn_timer = random.randint(2000, 15000)
        self.next_left_spawn_time = pygame.time.get_ticks() + self.spawn_timer
        self.next_right_spawn_time = pygame.time.get_ticks() + self.right_spawn_timer
        self.left_claxon_started = False
        self.right_claxon_started = False
        if self.left_claxon_channel:
            self.left_claxon_channel.stop()
        if self.right_claxon_channel:
            self.right_claxon_channel.stop()
        self.left_claxon_channel = None
        self.right_claxon_channel = None
        self.ambient_playing = False

    def update(self, player):
        """
        Met à jour l'état des trains et vérifie les collisions avec le joueur.
        Args:
            player (Joueur): L'instance du joueur.
        Retourne:
            bool: True si le joueur est mort, False sinon.
        """
        current_time = pygame.time.get_ticks()
        game_over = False

        # Update le train de droite
        time_until_left = self.next_left_spawn_time - current_time
        if time_until_left <= 1000 and not self.left_claxon_started and not self.trains:
            self.left_claxon_channel = son_alerte_train.play(loops=-1)
            self.left_claxon_started = True
        
        if current_time >= self.next_left_spawn_time and not self.trains:
            self.trains.append(TrainDeDroite
        (self.base_speed))
            self.trains[-1].sound_channel = self.left_claxon_channel
            self.spawn_timer = random.randint(2000, 10000)
            self.next_left_spawn_time = current_time + self.spawn_timer
            self.base_speed = min(self.base_speed + 15, 150)
            self.left_claxon_started = False
            self.left_claxon_channel = None

        # Update le train de gauche
        time_until_right = self.next_right_spawn_time - current_time
        if time_until_right <= 1000 and not self.right_claxon_started and not self.right_trains:
            self.right_claxon_channel = son_alerte_train.play(loops=-1)
            self.right_claxon_started = True
        
        if current_time >= self.next_right_spawn_time and not self.right_trains:
            self.right_trains.append(TrainDeGauche(self.right_train_speed))
            self.right_trains[-1].sound_channel = self.right_claxon_channel
            self.right_spawn_timer = random.randint(2000, 15000)
            self.next_right_spawn_time = current_time + self.right_spawn_timer
            self.right_claxon_started = False
            self.right_claxon_channel = None

        # Onverifie si un claxon est en cours de lecture
        any_claxons = False
        if self.left_claxon_channel and self.left_claxon_channel.get_busy():
            any_claxons = True
        if self.right_claxon_channel and self.right_claxon_channel.get_busy():
            any_claxons = True
        for train in self.trains + self.right_trains:
            if train.sound_channel and train.sound_channel.get_busy():
                any_claxons = True
                break

        if any_claxons:
            if self.ambient_playing:
                son_ambiant.stop()
                self.ambient_playing = False
        else:
            if not self.ambient_playing:
                son_ambiant.play(-1)
                self.ambient_playing = True

        # On update les trains et on vérifie les collisions
        for train in self.trains.copy():
            if train.update():
                self.trains.remove(train)
                if train.sound_channel:
                    train.sound_channel.fadeout(1500)
                self.next_left_spawn_time = pygame.time.get_ticks() + self.spawn_timer
            else:
                if player.on_train != train:
                    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                    if player_rect.colliderect(train.front_hitbox):
                        game_over = True
                    if player_rect.colliderect(train.top_hitbox):
                        if player.vel_y >= 0:
                            player.y = train.top_hitbox.y - player.height
                            player.vel_y = 0
                            player.jumps_left = 2
                            player.is_grounded = True
                            player.on_train = train

        if any_claxons:
            if self.ambient_playing:
                son_ambiant.stop()
                self.ambient_playing = False
        else:
            if not self.ambient_playing:
                son_ambiant.play(-1)
                self.ambient_playing = True

        # On update les trains de droite et on gère les augmentations de vitesse
        for train in self.trains.copy():
            if train.update():
                self.trains.remove(train)
                if train.sound_channel:
                    train.sound_channel.fadeout(1500)
                self.next_left_spawn_time = pygame.time.get_ticks() + self.spawn_timer
            else:
                if player.on_train != train:
                    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                    if player_rect.colliderect(train.front_hitbox):
                        game_over = True
                    if player_rect.colliderect(train.top_hitbox):
                        if player.vel_y >= 0:
                            player.y = train.top_hitbox.y - player.height
                            player.vel_y = 0
                            player.jumps_left = 2
                            player.is_grounded = True
                            player.on_train = train
                            player.offset_x = player.x - train.x
                    elif player.on_train == train:
                        player.on_train = None

        # On update les trains de gauche et on gère les augmentations de vitesse
        for train in self.right_trains.copy():
            if train.update():
                self.right_trains.remove(train)
                if train.sound_channel:
                    train.sound_channel.fadeout(1500)

                self.right_train_speed = min(self.right_train_speed + 15, 150)
                self.right_spawn_timer = random.randint(2000, 15000)
                self.next_right_spawn_time = current_time + self.right_spawn_timer
                self.right_claxon_started = False
                self.right_claxon_channel = None
            else:
                if player.on_train != train:
                    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)  
                    if player_rect.colliderect(train.front_hitbox) and player.x > train.x + train.width - 50:
                        game_over = True
                    if player_rect.colliderect(train.top_hitbox):
                        if player.vel_y >= 0:
                            player.y = train.top_hitbox.y - player.height
                            player.vel_y = 0
                            player.jumps_left = 2
                            player.is_grounded = True
                            player.on_train = train
                            player.offset_x = player.x - train.x
                    elif player.on_train == train:
                        player.on_train = None

        return game_over

    def draw(self, ecran):
        """
        Dessine les trains sur l'écran.
        Args:
            ecran (pygame.Surface): La surface sur laquelle on va dessiner les trains.
        """
        for train in self.trains:
            train.draw(ecran)
        for train in self.right_trains:
            train.draw(ecran)

class BackgroundManager:
    def __init__(self):
        """
        Initialise le gestionnaire de background.
        Attributs:
            original_bg (pygame.Surface): L'image de fond originale.
            background (pygame.Surface): L'image de fond redimensionnée.
            total_length (int): La longueur totale de l'image de fond.
            scale_factor (float): Le facteur de mise à l'échelle de l'image de fond.
            max_camera_x (int): La position maximale de la caméra en x.
            camera_x (int): La position actuelle de la caméra en x.
        """
        self.original_bg = pygame.image.load('assets/metro/background.png').convert_alpha()
        original_width = self.original_bg.get_width()
        original_height = self.original_bg.get_height()
        scaled_height = HAUTEUR_ECRAN
        self.scale_factor = scaled_height / original_height
        scaled_width = int(original_width * self.scale_factor)
        self.background = pygame.transform.scale(self.original_bg, (scaled_width, scaled_height))
        self.total_length = scaled_width
        self.max_camera_x = self.total_length - LARGEUR_ECRAN
        self.camera_x = 0

    def update(self, speed):
        """
        Met à jour la position de la caméra en fonction de la vitesse du joueur."
        Args:
            speed (int): La vitesse actuelle du joueur.
        """
        if not player.on_train:
            self.camera_x += speed
            self.camera_x = max(0, min(self.camera_x, self.max_camera_x))

    def draw(self, ecran):
        """
        Dessine l'image de fond sur l'écran.
        Args:
            ecran (pygame.Surface): La surface sur laquelle on va dessiner l'image de fond."""
        source_rect = pygame.Rect(self.camera_x, 0, LARGEUR_ECRAN, HAUTEUR_ECRAN)
        ecran.blit(self.background, (0, 0), source_rect)

    def reset(self):
        """ Réinitialise la position de la caméra en x. """
        self.camera_x = 0

# On initialise les objets du jeu
player = Joueur()
bg_manager = BackgroundManager()
train_manager = TrainManager()

level_complete = False

# Boucle principale du niveau
running = True
while running:
    dt = clock.tick(60) / 1000.0  # Delta temps en secondes
    ecran.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not level_complete:  
            if player.is_alive:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        player.sauter()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if boutons_game_over_actifs:
                        if recommencer_rect.collidepoint(mouse_pos):
                            # Restart le niveau
                            player.reset()
                            train_manager.reset()
                            bg_manager.reset()
                            mort_anim_timer = 0
                            boutons_game_over_actifs = False
                        elif quitter_rect.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
        else:
            # Level réussi : on vérifie si le joueur clique sur un bouton
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                elif next_level_rect.collidepoint(mouse_pos):
                    import subprocess
                    pygame.quit()
                    subprocess.Popen(["python", "niveauapres.py"])
                    sys.exit()

    # Qaund le joueur est mort, on incrémente le timer d'animation de mort
    if not player.is_alive:
        mort_anim_timer = min(mort_anim_timer + dt, 1.0)
    
    # Uniquement mettre à jour les objets du jeu si le niveau n'est pas terminé
    if not level_complete and player.is_alive:
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(dt)  
        player.update_sprint(dt)
        bg_manager.update(player.current_speed)
        
        # On vérifie si le joueur a atteint la fin du niveau
        if bg_manager.camera_x >= bg_manager.max_camera_x:
            level_complete = True
            son_ambiant.stop()
        
        game_over = train_manager.update(player)
    
        if game_over:
            player.is_alive = False
            son_ambiant.stop()
            for train in train_manager.trains + train_manager.right_trains:
                if train.sound_channel:
                    train.sound_channel.stop()

    # Dessine les objets du jeu
    bg_manager.draw(ecran)
    train_manager.draw(ecran)
    player.draw(ecran)
    dessiner_barre_sprint(ecran, player.sprint_amount)

    # Level réussi 
    if level_complete:
        # Afficher le texte "Niveau réussi !"
        win_font = pygame.font.Font(None, 72)
        win_text = win_font.render("Niveau réussi !", True, (255, 255, 255))
        win_text_rect = win_text.get_rect(center=(LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 3))
        ecran.blit(win_text, win_text_rect)
        
        # Dessiner les boutons "Niveau suivant" et "Quitter"
        button_width = 200
        button_height = 60
        spacing = 20
        total_buttons_width = 2 * button_width + spacing
        buttons_x = (LARGEUR_ECRAN - total_buttons_width) // 2
        button_y = HAUTEUR_ECRAN // 2
        next_level_rect = pygame.Rect(buttons_x, button_y, button_width, button_height)
        exit_rect = pygame.Rect(buttons_x + button_width + spacing, button_y, button_width, button_height)
        pygame.draw.rect(ecran, (255, 255, 255), next_level_rect)
        pygame.draw.rect(ecran, (255, 255, 255), exit_rect)
        btn_font = pygame.font.Font(None, 36)
        next_text = btn_font.render("Niveau suivant", True, (0, 0, 0))
        exit_text = btn_font.render("Quitter", True, (0, 0, 0))
        next_text_rect = next_text.get_rect(center=next_level_rect.center)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        ecran.blit(next_text, next_text_rect)
        ecran.blit(exit_text, exit_text_rect)

    # Game over
    if not player.is_alive and not level_complete:
        factor = mort_anim_timer  


        bg_y = -HAUTEUR_ECRAN + int(factor * HAUTEUR_ECRAN)
        ecran.blit(game_over_bg_img, (0, bg_y))


        img_game_over_height = img_game_over.get_height()
        target_y = HAUTEUR_ECRAN // 3 - img_game_over_height // 2 + 200  
        game_over_y = -img_game_over_height + int(factor * (target_y + img_game_over_height))
        game_over_x = (LARGEUR_ECRAN - img_game_over.get_width()) // 2
        ecran.blit(img_game_over, (game_over_x, game_over_y))

       
        if mort_anim_timer >= 1.0:
            boutons_game_over_actifs = True

            button_width = 200
            button_height = 60
            spacing = 20
            total_buttons_width = 2 * button_width + spacing
            button_y = (HAUTEUR_ECRAN - button_height) // 2  
            left_button_x = (LARGEUR_ECRAN - total_buttons_width) // 2
            right_button_x = left_button_x + button_width + spacing

            
            recommencer_rect = pygame.Rect(left_button_x, button_y, button_width, button_height)
            quitter_rect = pygame.Rect(right_button_x, button_y, button_width, button_height)

            
            pygame.draw.rect(ecran, (255, 255, 255), recommencer_rect)
            pygame.draw.rect(ecran, (255, 255, 255), quitter_rect)

            font = pygame.font.Font(None, 36)
            rec_text = font.render("Recommencer", True, (0, 0, 0))
            quit_text = font.render("Quitter", True, (0, 0, 0))
            rec_text_rect = rec_text.get_rect(center=recommencer_rect.center)
            quit_text_rect = quit_text.get_rect(center=quitter_rect.center)
            ecran.blit(rec_text, rec_text_rect)
            ecran.blit(quit_text, quit_text_rect)

    pygame.display.flip()

pygame.mixer.quit()
pygame.quit()
sys.exit()