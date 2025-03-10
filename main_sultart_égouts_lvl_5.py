import pygame
import random
import math
import sys
from animation import Anima  # Import de la classe d'animation

# Initialisation de Pygame et du module son
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

# --------------------------
# Définition des constantes
# --------------------------
WIDTH, HEIGHT = 1920, 1080
GRAVITY = 1.8
JUMP_MAX = -30
SPEED = 17
LEVEL_DURATION = 125  # en secondes

PLAYER_SIZE = 100
SMALL_RAT_SIZE = 50
BIG_RAT_SIZE = int(PLAYER_SIZE * 1.2)
RAT_SPEED = int(1.2 * SPEED)

# Intervalles de spawn (en ms)
INITIAL_MIN_SPAWN_INTERVAL = 5000
INITIAL_MAX_SPAWN_INTERVAL = 9000

# Position du sol
FLOOR_Y = HEIGHT - 355

# --------------------------
# Création de la fenêtre (obligatoire AVANT le chargement des images avec convert_alpha)
# --------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sultan Art'ventures LvL 5")

# --------------------------
# Chargement des ressources
# --------------------------
# Fonds
bg_images = [
    pygame.image.load("égouts/Bg egouts .png"),
    pygame.image.load("égouts/Bg egouts .png"),
    pygame.image.load("égouts/Bg egouts .png")
]
floor_image = pygame.image.load("égouts/Sol egouts HD.png")
final_bg_image = pygame.image.load("égouts/Fond egouts .png")
final_combined_bg = pygame.image.load("égouts/fond combiné.png")
final_transition_progress = 0
final_transition_started = False

# Pictogrammes d'attaque
attack_left_icon = pygame.image.load("égouts/icone poing final.png").convert_alpha()
attack_right_icon = pygame.image.load("égouts/icone sabre final.png").convert_alpha()

# Animations d'attaque
attack1 = pygame.image.load("égouts/Punch anim.png.").convert_alpha()
attack2 = pygame.image.load("égouts/Anim épée.png.").convert_alpha()
attack_anim_left = pygame.transform.scale(attack1, (100, 100))
attack_anim_right = pygame.transform.scale(attack2, (100, 100))
left_attack_anim_start = None
right_attack_anim_start = None
attack_anim_duration = 200  # Durée du fade-out en ms

# Images pour les animations de mort (gros rat)
rat_head = pygame.image.load("égouts/G.Rat cul.png").convert_alpha()
rat_tail = pygame.image.load("égouts/G.Rat tete.png").convert_alpha()

# Images des rats
rat_image_red = pygame.image.load("égouts/rat court 1 (2).png").convert_alpha()
rat_image_blue = pygame.image.load("égouts/rat court 2 (2).png").convert_alpha()
rat_image_jump = pygame.image.load("égouts/rat saut new.png").convert_alpha()
big_rat_red = pygame.image.load("égouts/G.Rat cours 1 (2).png.").convert_alpha()
big_rat_blue = pygame.image.load("égouts/G.Rat cours 2 (2).png.").convert_alpha()
big_rat_jump = pygame.image.load("égouts/G.Rat saut (2).png").convert_alpha()

# Police
game_font = pygame.font.Font("égouts/Baberry.ttf", 25)

# Sons et musique
pygame.mixer.music.load("égouts/ambiance égouts.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

footstep_sound = pygame.mixer.Sound("égouts/son egouts 2.mp3")
footstep_sound.set_volume(0.7)
# Le son de déplacement est affecté à un canal dédié
footstep_channel = pygame.mixer.Channel(0)

jump_sound = pygame.mixer.Sound("égouts/jump.mp3")
attack_left_sound = pygame.mixer.Sound("égouts/punch.mp3")
attack_right_sound_default = pygame.mixer.Sound("égouts/epée son.mp3")
attack_right_sound_special = pygame.mixer.Sound("égouts/ching.mp3")
attack_left_sound.set_volume(0.8)
attack_right_sound_default.set_volume(0.8)
attack_right_sound_special.set_volume(1)
rat_bite_sound = pygame.mixer.Sound("égouts/morsure2.mp3")
rat_bite_sound.set_volume(0.1)

special_right_attack_played = False

# Sons de spawn pour les rats (à ajuster si nécessaire)
rat_spawn_sounds = [
    pygame.mixer.Sound("égouts/rats/rats 1.mp3"),
    pygame.mixer.Sound("égouts/rats/rats 2.mp3"),
    pygame.mixer.Sound("égouts/rats/rats 3.mp3")
]
for sound in rat_spawn_sounds:
    sound.set_volume(0.8)

# Variables globales pour le défilement
scroll_x = 0
bg_index = 0
scroll_direction = 0  

# Variables de recharge d'attaque
last_left_attack_time = 0
last_right_attack_time = 0
left_attack_cooldown = 1500  # ms
right_attack_cooldown = 5000  # ms

# File de spawn et animations de mort
spawn_queue = []
death_animations = []

# --------------------------
# Définition des classes
# --------------------------
class Player:
    def __init__(self, x, y):
        # Utilisation de PLAYER_SIZE pour la taille du joueur
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.vel_y = 0
        self.on_ground = True
        self.hp = 1001
        # Intégration des animations pour le player
        self.idleAnim = Anima('assets/PlayerAnim/IdlePlayerAnim1/')
        self.walkAnim = Anima('assets/PlayerAnim/WalkPlayerAnim1/')
        self.action = 'idle'      # état par défaut
        self.direction = 'droite' # pour gérer l'orientation

    def jump(self, keys):
        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.vel_y = JUMP_MAX
                self.on_ground = False
                jump_sound.play()
            else:
                self.vel_y = max(self.vel_y - 0.5, JUMP_MAX)
        else:
            if self.vel_y < 0:
                self.vel_y += 1

    def apply_gravity(self):
        if not self.on_ground:
            self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.on_ground = True
            self.vel_y = 0

    def display(self):
        # Sélection de l'image selon l'action (idle ou walk)
        if self.action == 'idle':
            img = self.idleAnim.get_imgCourante()
        elif self.action == 'walk':
            img = self.walkAnim.get_imgCourante()
        else:
            img = self.idleAnim.get_imgCourante()  # par défaut

        # Gestion de l'orientation
        if self.direction == 'gauche':
            img = pygame.transform.flip(img, True, False)
        # Redimensionnement de l'image
        img = pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE))
        screen.blit(img, self.rect.topleft)

    def update(self):
        # Mise à jour de l'animation selon l'état
        if self.action == 'idle':
            self.idleAnim.defilement()
        elif self.action == 'walk':
            self.walkAnim.defilement()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def draw_HP(self):
        max_hp = 1001
        bar_width = 350
        bar_height = 35
        current_hp = self.hp
        health_ratio = current_hp / max_hp
        health_width = bar_width * health_ratio
        bar_x = 75
        bar_y = HEIGHT - 90
        pygame.draw.rect(screen, (169, 169, 169), (bar_x, bar_y, bar_width, bar_height))
        color = (0, 255, 0) if health_ratio > 0.5 else ((255, 255, 0) if health_ratio > 0.2 else (255, 0, 0))
        pygame.draw.rect(screen, color, (bar_x, bar_y, health_width, bar_height))
        health_text = game_font.render(f"HP: {current_hp}/{max_hp}", True, (255, 255, 255))
        screen.blit(health_text, (bar_x + bar_width + 10, bar_y + 5))


class Rat:
    def __init__(self, is_big=False):
        self.is_big = is_big
        if self.is_big:
            self.size = BIG_RAT_SIZE
            self.damage = random.randint(40, 52) * 1001 // 100
        else:
            self.size = SMALL_RAT_SIZE
            self.damage = random.randint(15, 19) * 1001 // 100
        self.rect = pygame.Rect(WIDTH, 0, self.size, self.size)
        if self.is_big:
            self.rect.bottom = FLOOR_Y - 50
        else:
            self.rect.bottom = FLOOR_Y - 25
        self.speed = RAT_SPEED
        self.jumping = False
        self.vel_y = 0
        self.jump_triggered = False
        self.jump_dx = 0
        self.colors = [(255, 0, 0), (0, 0, 255)]
        self.current_color_index = 0
        self.last_color_change = 0

    def move(self, current_time):
        if not self.jumping:
            self.rect.x -= self.speed
            if (not self.jump_triggered) and (self.rect.x <= player.rect.x + 600):
                self.jumping = True
                self.jump_triggered = True
                self.vel_y = -25
                dx = player.rect.centerx - self.rect.centerx
                self.jump_dx = dx / 25.0
        else:
            self.rect.x += self.jump_dx
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            floor_adjustment = 50 if self.is_big else 25
            if self.rect.bottom >= FLOOR_Y - floor_adjustment:
                self.rect.bottom = FLOOR_Y - floor_adjustment
                dx = self.rect.centerx - player.rect.centerx
                dy = self.rect.centery - player.rect.centery
                if dx * dx + dy * dy <= 10000:
                    self.attack_player()
                else:
                    self.jumping = False
                    self.vel_y = 0
        if self.rect.right < -250 and self in enemies:
            enemies.remove(self)

    def draw(self, current_time):
        if self.last_color_change == 0:
            self.last_color_change = current_time
        if current_time - self.last_color_change >= 250:
            self.current_color_index = (self.current_color_index + 1) % len(self.colors)
            self.last_color_change = current_time
        if self.is_big:
            if self.jumping:
                screen.blit(big_rat_jump, self.rect)
            else:
                img = big_rat_red if self.colors[self.current_color_index] == (255, 0, 0) else big_rat_blue
                screen.blit(img, self.rect)
        else:
            if self.jumping:
                screen.blit(rat_image_jump, self.rect)
            else:
                img = rat_image_red if self.colors[self.current_color_index] == (255, 0, 0) else rat_image_blue
                screen.blit(img, self.rect)

    def take_damage(self, attack_type):
        if attack_type == "left_click" and not self.is_big:
            if self in enemies:
                enemies.remove(self)
        elif attack_type == "right_click":
            if self in enemies:
                if self.is_big:
                    head_pos = (self.rect.x, self.rect.y)
                    tail_pos = (self.rect.x + self.rect.width - rat_tail.get_width() + 30,
                                self.rect.y + self.rect.height - rat_tail.get_height() + 30)
                    death_animations.append({"image": rat_head, "pos": list(head_pos), "velocity": 30})
                    death_animations.append({"image": rat_tail, "pos": list(tail_pos), "velocity": 30})
                enemies.remove(self)

    def attack_player(self):
        rat_bite_sound.play()
        player.take_damage(self.damage)
        if self in enemies:
            enemies.remove(self)

# --------------------------
# Fonctions utilitaires
# --------------------------
def draw_attack_icons():
    icon_size = 120
    icon_x = 140
    icon_y = HEIGHT - 230
    spacing = 140
    current_time = pygame.time.get_ticks()
    left_opacity = 255 if current_time - last_left_attack_time >= left_attack_cooldown else 100
    right_opacity = 255 if current_time - last_right_attack_time >= right_attack_cooldown else 100
    left_icon = pygame.transform.scale(attack_left_icon, (icon_size, icon_size)).copy()
    right_icon = pygame.transform.scale(attack_right_icon, (icon_size, icon_size)).copy()
    left_icon.fill((255, 255, 255, left_opacity), special_flags=pygame.BLEND_RGBA_MULT)
    right_icon.fill((255, 255, 255, right_opacity), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(left_icon, (icon_x, icon_y))
    screen.blit(right_icon, (icon_x + spacing, icon_y))

def scroll_background():
    global scroll_x, bg_index, scroll_direction
    screen.blit(bg_images[bg_index], (-scroll_x, 0))
    screen.blit(bg_images[(bg_index + 1) % len(bg_images)], (WIDTH - scroll_x, 0))
    scroll_x += SPEED * scroll_direction
    if scroll_direction > 0 and scroll_x >= WIDTH:
        scroll_x = 0
        bg_index = (bg_index + 1) % len(bg_images)
    elif scroll_direction < 0 and scroll_x <= 0:
        scroll_x = WIDTH
        bg_index = (bg_index - 1) % len(bg_images)

def process_spawn_queue(current_time):
    i = 0
    while i < len(spawn_queue):
        spawn_time, is_big, x_position = spawn_queue[i]
        if current_time >= spawn_time:
            rat = Rat(is_big)
            rat.rect.x = x_position
            enemies.append(rat)
            spawn_queue.pop(i)
        else:
            i += 1

def game_over_screen():
    # Arrête tous les sons lorsque le Game Over apparaît
    pygame.mixer.stop()
    clock = pygame.time.Clock()
    background = bg_images[0]
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    overlay_y = -HEIGHT
    animation_speed = 20  # Vitesse de glissement (pixels par frame)
    while overlay_y < 0:
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, overlay_y))
        pygame.display.update()
        overlay_y += animation_speed
        clock.tick(60)
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

# --------------------------
# Fonction principale du jeu
# --------------------------
def main():
    global scroll_x, bg_index, scroll_direction, final_transition_started, final_transition_progress
    global left_attack_anim_start, right_attack_anim_start, last_left_attack_time, last_right_attack_time
    global special_right_attack_played, spawn_queue, enemies, death_animations, player

    # Réinitialisation des variables globales
    scroll_x = 0
    bg_index = 0
    scroll_direction = 0
    final_transition_started = False
    final_transition_progress = 0
    left_attack_anim_start = None
    right_attack_anim_start = None
    last_left_attack_time = 0
    last_right_attack_time = 0
    special_right_attack_played = False
    spawn_queue = []
    enemies = []
    death_animations = []

    player = Player(WIDTH // 3, HEIGHT - 100)

    last_small_spawn = pygame.time.get_ticks()
    last_big_spawn = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()
    spawn_stop_time = start_time + LEVEL_DURATION * 1000 - 4300

    clock = pygame.time.Clock()
    going = True

    while going:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Attaque gauche (bouton 1)
                if event.button == 1:
                    if current_time - last_left_attack_time >= left_attack_cooldown:
                        channel = pygame.mixer.find_channel()
                        if channel:
                            channel.play(attack_left_sound)
                        killed = False
                        for enemy in enemies[:]:
                            if (not enemy.is_big) and abs(enemy.rect.centerx - player.rect.centerx) <= 350:
                                enemy.take_damage("left_click")
                                killed = True
                        last_left_attack_time = current_time
                        if killed:
                            left_attack_anim_start = current_time

                # Attaque droite (bouton 3)
                elif event.button == 3:
                    if current_time - last_right_attack_time >= right_attack_cooldown:
                        channel = pygame.mixer.find_channel()
                        if channel:
                            if not special_right_attack_played and random.random() < 0.2:
                                channel.play(attack_right_sound_special)
                                special_right_attack_played = True
                            else:
                                channel.play(attack_right_sound_default)
                        killed = False
                        for enemy in enemies[:]:
                            attack_range = 170
                            if enemy.is_big:
                                attack_range += (BIG_RAT_SIZE - SMALL_RAT_SIZE) // 2
                            if abs(enemy.rect.centerx - player.rect.centerx) <= attack_range:
                                enemy.take_damage("right_click")
                                killed = True
                        last_right_attack_time = current_time
                        if killed:
                            right_attack_anim_start = current_time

        keys = pygame.key.get_pressed()
        if player.on_ground and keys[pygame.K_d]:
            if not footstep_channel.get_busy():
                footstep_channel.play(footstep_sound)
        else:
            if footstep_channel.get_busy():
                footstep_channel.stop()

        # Gestion du défilement du fond ou transition finale
        if elapsed_time < LEVEL_DURATION:
            if keys[pygame.K_d]:
                scroll_direction = 1
            elif keys[pygame.K_q]:
                scroll_direction = -1
            else:
                scroll_direction = 0

            if scroll_direction != 0:
                scroll_background()
            else:
                screen.blit(bg_images[bg_index], (-scroll_x, 0))
                screen.blit(bg_images[(bg_index + 1) % len(bg_images)], (WIDTH - scroll_x, 0))
        else:
            if not final_transition_started:
                final_transition_started = True
                final_transition_progress = 0
            if final_transition_progress < 3840 - WIDTH:
                screen.blit(final_combined_bg, (-final_transition_progress, 0))
                final_transition_progress += SPEED
            else:
                screen.blit(final_bg_image, (0, 0))

        screen.blit(floor_image, (0, FLOOR_Y))
        # Gestion du saut et de la gravité
        player.jump(keys)
        player.apply_gravity()

        # Mise à jour de l'état du joueur en fonction des touches
        if keys[pygame.K_d]:
            player.action = 'walk'
            player.direction = 'droite'
        elif keys[pygame.K_q]:
            player.action = 'walk'
            player.direction = 'gauche'
        else:
            player.action = 'idle'

        player.update()   # Actualise l'animation
        player.display()  # Affiche le sprite animé
        player.draw_HP()
        draw_attack_icons()

        # Animation d'attaque gauche (fade-out)
        if left_attack_anim_start is not None:
            elapsed = current_time - left_attack_anim_start
            if elapsed < attack_anim_duration:
                alpha = int(255 * (1 - elapsed / attack_anim_duration))
                temp_image = attack_anim_left.copy()
                temp_image.set_alpha(alpha)
                anim_pos = (player.rect.centerx + 50, player.rect.centery - 95)
                screen.blit(temp_image, anim_pos)
            else:
                left_attack_anim_start = None

        # Animation d'attaque droite (fade-out)
        if right_attack_anim_start is not None:
            elapsed = current_time - right_attack_anim_start
            if elapsed < attack_anim_duration:
                alpha = int(255 * (1 - elapsed / attack_anim_duration))
                temp_image = attack_anim_right.copy()
                temp_image.set_alpha(alpha)
                anim_pos = (player.rect.centerx + 75, player.rect.centery - 95)
                screen.blit(temp_image, anim_pos)
            else:
                right_attack_anim_start = None

        # Mise à jour des animations de mort (tête et queue)
        for anim in death_animations[:]:
            anim["pos"][1] += anim["velocity"]
            screen.blit(anim["image"], anim["pos"])
            if anim["pos"][1] > HEIGHT:
                death_animations.remove(anim)

        # Gestion des spawns
        if current_time < spawn_stop_time:
            if elapsed_time >= 10:
                spawn_interval_small = random.randint(INITIAL_MIN_SPAWN_INTERVAL, INITIAL_MAX_SPAWN_INTERVAL)
                if current_time - last_small_spawn > spawn_interval_small:
                    num_spawn = random.randint(1, 4)
                    base_x_position = WIDTH
                    separation_distance = 100
                    for i in range(num_spawn):
                        spawn_queue.append((current_time + i * 1000, False, base_x_position + i * separation_distance))
                    last_small_spawn = current_time

            if 45 <= elapsed_time < 70:
                spawn_interval_big = random.randint(3000, 5000)
                if current_time - last_big_spawn > spawn_interval_big:
                    num_spawn = random.randint(1, 3)
                    base_x_position = WIDTH
                    separation_distance = 2000
                    for i in range(num_spawn):
                        spawn_queue.append((current_time + i * 1000, True, base_x_position + i * separation_distance))
                    last_big_spawn = current_time

            if elapsed_time >= LEVEL_DURATION - 30:
                spawn_interval_chaos = random.randint(1000, 3000)
                if current_time - last_small_spawn > spawn_interval_chaos:
                    num_spawn = random.randint(1, 4)
                    base_x_position = WIDTH
                    separation_distance = 100
                    for i in range(num_spawn):
                        spawn_queue.append((current_time + i * 1000, False, base_x_position + i * separation_distance))
                    last_small_spawn = current_time

                if current_time - last_big_spawn > spawn_interval_chaos:
                    num_spawn = random.randint(1, 2)
                    base_x_position = WIDTH
                    separation_distance = 100
                    for i in range(num_spawn):
                        spawn_queue.append((current_time + i * 1000, True, base_x_position + i * separation_distance))
                    last_big_spawn = current_time

        process_spawn_queue(current_time)

        for enemy in enemies[:]:
            enemy.move(current_time)
        for enemy in enemies:
            if not enemy.is_big:
                enemy.draw(current_time)
        for enemy in enemies:
            if enemy.is_big:
                enemy.draw(current_time)

        pygame.display.update()
        clock.tick(60)

        if player.hp <= 0:
            going = False

    choice = game_over_screen()
    if choice == "restart":
        main()  # Redémarrage
    else:
        pygame.quit()
        sys.exit()

# Lancement du jeu
main()
