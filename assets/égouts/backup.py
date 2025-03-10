#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jeu "Sultan Art'ventures Niveau 5"

Ce script utilise Pygame pour créer un jeu d'action dans lequel le joueur qui incarne un dessin représentant
un sultan ottoman doit éviter et attaquer des rats (petits et gros) qui apparaissent et se déplacent dans un décor.
Chaque type d'événement (apparition, saut, attaque) déclenche un son spécifique, et certains sons 
sont joués sur des canaux dédiés.

Date : 02-03-2025
"""

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
# Définition des constantes (en français)
# --------------------------
LARGEUR, HAUTEUR = 1920, 1080
GRAVITE = 1.8
SAUT_MAX = -30
VITESSE = 17
DUREE_NIVEAU = 125  # en secondes

TAILLE_JOUEUR = 100
TAILLE_RAT_PETIT = 50
TAILLE_RAT_GRAND = int(TAILLE_JOUEUR * 1.2)
VITESSE_RAT = int(1.2 * VITESSE)

# Intervalles de spawn (en ms)
INTERVALLE_MIN_SPAWN = 5000
INTERVALLE_MAX_SPAWN = 9000

# Position du sol
SOL_Y = HAUTEUR - 355

# --------------------------
# Création de la fenêtre
# --------------------------
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Sultan Art'ventures LvL 5")

# --------------------------
# Chargement des ressources
# --------------------------
images_fond = [
    pygame.image.load("bg_egouts.png"),
    pygame.image.load("bg_egouts.png"),
    pygame.image.load("bg_egouts.png")
]
image_sol = pygame.image.load("sol_egouts.png")
image_fond_final = pygame.image.load("fond_egouts.png")
image_fond_combine = pygame.image.load("fond_combine.png")

# Images pour l'écran Game Over
image_game_over_bg = pygame.image.load("fond_sans_g_o.png").convert_alpha()
image_game_over_fg = pygame.image.load("g_o.png").convert_alpha()

progression_transition_finale = 0
transition_finale_lancee = False

# Icônes d'attaque
icone_attaque_gauche = pygame.image.load("icone_poing_final.png").convert_alpha()
icone_attaque_droite = pygame.image.load("icone_sabre_final.png").convert_alpha()

# Animations d'attaque
attaque1 = pygame.image.load("punch_anim.png.").convert_alpha()
attaque2 = pygame.image.load("anim-epee.png.").convert_alpha()
anim_attaque_gauche = pygame.transform.scale(attaque1, (100, 100))
anim_attaque_droite = pygame.transform.scale(attaque2, (100, 100))
debut_anim_attaque_gauche = None
debut_anim_attaque_droite = None
duree_anim_attaque = 200  # Durée du fade-out en ms

# Images pour les animations de mort (gros rat)
tete_rat = pygame.image.load("g.rat_cul.png").convert_alpha()
queue_rat = pygame.image.load("g.rat_tete.png").convert_alpha()

# Images des rats
image_rat_rouge = pygame.image.load("rat court 1 (2).png").convert_alpha()
image_rat_bleu = pygame.image.load("rat court 2 (2).png").convert_alpha()
image_rat_saut = pygame.image.load("rat saut new.png").convert_alpha()
rat_grand_rouge = pygame.image.load("g.rat_cours_1.png").convert_alpha()
rat_grand_bleu = pygame.image.load("g.rat_cours_2.png").convert_alpha()
rat_grand_saut = pygame.image.load("g.rat_saut.png").convert_alpha()

# Police
police_jeu = pygame.font.Font("baberry.ttf", 25)

# Sons et musique
pygame.mixer.music.load("ambiance_egouts.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

son_pas = pygame.mixer.Sound("son egouts 2.mp3")
son_pas.set_volume(0.7)
# Canal dédié pour le son de déplacement (pas)
canal_pas = pygame.mixer.Channel(0)

son_saut = pygame.mixer.Sound("jump.mp3")
son_attaque_gauche = pygame.mixer.Sound("punch.mp3")
son_attaque_droite_defaut = pygame.mixer.Sound("epee_son.mp3")
son_attaque_droite_special = pygame.mixer.Sound("ching.mp3")
son_attaque_gauche.set_volume(0.8)
son_attaque_droite_defaut.set_volume(0.6)
son_attaque_droite_special.set_volume(1)
son_morsure_rat = pygame.mixer.Sound("morsure2.mp3")
son_morsure_rat.set_volume(0.1)

attaque_droite_speciale_jouee = False

# Sons liés aux rats
son_spawn_rat_petit = pygame.mixer.Sound("rats\petits_rats_ambiance.wav")
son_spawn_rat_grand = pygame.mixer.Sound("rats\gros_rats_ambiance.wav")
son_saut_rat_petit = pygame.mixer.Sound("rats\petit_rat_saut.wav")
sons_saut_rat_grand = [
    pygame.mixer.Sound("rats\gros_rat\gros_rat_attaque_1.wav"),
    pygame.mixer.Sound("rats\gros_rat\gros_rat_attaque_2.wav"),
    pygame.mixer.Sound("rats\gros_rat\gros_rat_attaque_3.wav")
]

# Canaux dédiés pour les sons liés aux rats
canal_spawn_rat_petit = pygame.mixer.Channel(10)
canal_spawn_rat_grand = pygame.mixer.Channel(11)
canal_saut_rat_petit = pygame.mixer.Channel(12)
canal_saut_rat_grand = pygame.mixer.Channel(13)

pygame.mixer.Channel(10).set_volume(0.7)
pygame.mixer.Channel(11).set_volume(0.5)
pygame.mixer.Channel(12).set_volume(0.7)
pygame.mixer.Channel(13).set_volume(0.5)

# Variables globales pour le défilement du fond
decalage_x = 0
indice_fond = 0
direction_defilement = 0

# Variables pour la gestion des attaques (cooldowns)
dernier_temps_attaque_gauche = 0
dernier_temps_attaque_droite = 0
delai_attaque_gauche = 900   # ms
delai_attaque_droite = 3000  # ms

# File de spawn et animations de mort
file_spawn = []
animations_mort = []

# --------------------------
# Définition des classes et fonctions
# --------------------------

class Player:
    """
    Classe représentant le joueur avec animations.
    """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TAILLE_JOUEUR, TAILLE_JOUEUR)
        self.vitesse_y = 0
        self.au_sol = False
        self.pv = 1001
        # Intégration des animations pour le player
        self.idleAnim = Anima('assets/PlayerAnim/IdlePlayerAnim1/')
        self.walkAnim = Anima('assets/PlayerAnim/WalkPlayerAnim1/')
        self.action = 'idle'      # état par défaut
        self.direction = 'droite' # pour gérer l'orientation

    def jump(self, touches):
        """Gère le saut du joueur."""
        if touches[pygame.K_SPACE]:
            if self.au_sol:
                self.vitesse_y = SAUT_MAX
                self.au_sol = False
                son_saut.play()
            else:
                self.vitesse_y = max(self.vitesse_y - 0.5, SAUT_MAX)
        else:
            if self.vitesse_y < 0:
                self.vitesse_y += 1

    def apply_gravity(self):
        """Applique la gravité et met à jour la position verticale."""
        if not self.au_sol:
            self.vitesse_y += GRAVITE
        self.rect.y += self.vitesse_y
        if self.rect.bottom >= SOL_Y:
            self.rect.bottom = SOL_Y
            self.au_sol = True
            self.vitesse_y = 0

    def display(self):
        """Affiche le joueur en utilisant les animations."""
        if self.action == 'idle':
            img = self.idleAnim.get_imgCourante()
        elif self.action == 'walk':
            img = self.walkAnim.get_imgCourante()
        else:
            img = self.idleAnim.get_imgCourante()  # valeur par défaut

        if self.direction == 'gauche':
            img = pygame.transform.flip(img, True, False)
        img = pygame.transform.scale(img, (TAILLE_JOUEUR, TAILLE_JOUEUR))
        ecran.blit(img, self.rect.topleft)

    def update(self):
        """Met à jour l'animation en fonction de l'action du joueur."""
        if self.action == 'idle':
            self.idleAnim.defilement()
        elif self.action == 'walk':
            self.walkAnim.defilement()

    def take_damage(self, amount):
        """Réduit les points de vie du joueur."""
        self.pv -= amount
        if self.pv < 0:
            self.pv = 0

    def display_hp(self):
        """Affiche la barre de vie du joueur."""
        pv_max = 1001
        largeur_barre = 350
        hauteur_barre = 35
        pv_actuels = self.pv
        ratio_vie = pv_actuels / pv_max
        largeur_vie = largeur_barre * ratio_vie
        pos_x = 75
        pos_y = HAUTEUR - 90
        pygame.draw.rect(ecran, (169, 169, 169), (pos_x, pos_y, largeur_barre, hauteur_barre))
        couleur = (0, 255, 0) if ratio_vie > 0.5 else ((255, 255, 0) if ratio_vie > 0.2 else (255, 0, 0))
        pygame.draw.rect(ecran, couleur, (pos_x, pos_y, largeur_vie, hauteur_barre))
        texte_vie = police_jeu.render(f"PV : {pv_actuels}/{pv_max}", True, (255, 255, 255))
        ecran.blit(texte_vie, (pos_x + largeur_barre + 10, pos_y + 5))


class Rat:
    """
    Classe représentant un rat (petit ou grand).
    """
    def __init__(self, est_grand=False):
        self.est_grand = est_grand
        if self.est_grand:
            self.taille = TAILLE_RAT_GRAND
            self.degats = random.randint(40, 52) * 1001 // 100
        else:
            self.taille = TAILLE_RAT_PETIT
            self.degats = random.randint(15, 19) * 1001 // 100
        self.rect = pygame.Rect(LARGEUR, 0, self.taille, self.taille)
        if self.est_grand:
            self.rect.bottom = SOL_Y - 50
        else:
            self.rect.bottom = SOL_Y - 25
        self.vitesse = VITESSE_RAT
        self.en_saut = False
        self.vitesse_y = 0
        self.saut_declenche = False
        self.decalage_saut_x = 0
        self.couleurs = [(255, 0, 0), (0, 0, 255)]
        self.indice_couleur_courante = 0
        self.dernier_changement_couleur = 0
        self.canal_spawn = None

    def move(self, current_time):
        """
        Met à jour la position du rat et gère son saut ainsi que l'arrêt du son de spawn
        lorsqu'il sort de l'écran.
        """
        if not self.en_saut:
            self.rect.x -= self.vitesse
            if (not self.saut_declenche) and (self.rect.x <= player.rect.x + 600):
                self.en_saut = True
                self.saut_declenche = True
                self.vitesse_y = -25
                dx = player.rect.centerx - self.rect.centerx
                self.decalage_saut_x = dx / 25.0
                # Joue le son du saut via les canaux dédiés
                if self.est_grand:
                    pygame.mixer.Channel(13).play(random.choice(sons_saut_rat_grand))
                else:
                    pygame.mixer.Channel(12).play(son_saut_rat_petit)
        else:
            self.rect.x += self.decalage_saut_x
            self.vitesse_y += GRAVITE
            self.rect.y += self.vitesse_y
            ajustement_sol = 50 if self.est_grand else 25
            if self.rect.bottom >= SOL_Y - ajustement_sol:
                self.rect.bottom = SOL_Y - ajustement_sol
                dx = self.rect.centerx - player.rect.centerx
                dy = self.rect.centery - player.rect.centery
                if dx * dx + dy * dy <= 10000:
                    self.attack_player()
                else:
                    self.en_saut = False
                    self.vitesse_y = 0

        if self.rect.right < -250:
            if self.canal_spawn is not None:
                self.canal_spawn.stop()
            if self in ennemis:
                ennemis.remove(self)

    def display(self, current_time):
        """
        Affiche le rat en alternant sa couleur toutes les 250 ms.
        """
        if self.dernier_changement_couleur == 0:
            self.dernier_changement_couleur = current_time
        if current_time - self.dernier_changement_couleur >= 250:
            self.indice_couleur_courante = (self.indice_couleur_courante + 1) % len(self.couleurs)
            self.dernier_changement_couleur = current_time
        if self.est_grand:
            if self.en_saut:
                ecran.blit(rat_grand_saut, self.rect)
            else:
                img = rat_grand_rouge if self.couleurs[self.indice_couleur_courante] == (255, 0, 0) else rat_grand_bleu
                ecran.blit(img, self.rect)
        else:
            if self.en_saut:
                ecran.blit(image_rat_saut, self.rect)
            else:
                img = image_rat_rouge if self.couleurs[self.indice_couleur_courante] == (255, 0, 0) else image_rat_bleu
                ecran.blit(img, self.rect)

    def take_damage(self, attack_type):
        """
        Gère la réaction du rat lors d'une attaque.
        Pour une attaque gauche sur un petit rat, le rat est retiré.
        Pour une attaque droite, le rat est retiré, et s'il est grand, on lance une animation de mort.
        """
        if attack_type == "clic_gauche" and not self.est_grand:
            if self in ennemis:
                ennemis.remove(self)
        elif attack_type == "clic_droite":
            if self in ennemis:
                if self.est_grand:
                    pos_tete = (self.rect.x, self.rect.y)
                    pos_queue = (self.rect.x + self.rect.width - queue_rat.get_width() + 30,
                                 self.rect.y + self.rect.height - queue_rat.get_height() + 30)
                    animations_mort.append({"image": tete_rat, "pos": list(pos_tete), "vitesse": 30})
                    animations_mort.append({"image": queue_rat, "pos": list(pos_queue), "vitesse": 30})
                ennemis.remove(self)

    def attack_player(self):
        """Le rat attaque le joueur et lui inflige des dégâts."""
        son_morsure_rat.play()
        player.take_damage(self.degats)
        if self in ennemis:
            ennemis.remove(self)

def display_attack_icons():
    """
    Affiche les icônes d'attaque (gauche et droite) en bas de l'écran,
    avec une opacité réduite si l'attaque est en cooldown.
    """
    taille_icone = 120
    pos_x = 140
    pos_y = HAUTEUR - 230
    espacement = 140
    temps_actuel = pygame.time.get_ticks()
    opacite_gauche = 255 if temps_actuel - dernier_temps_attaque_gauche >= delai_attaque_gauche else 100
    opacite_droite = 255 if temps_actuel - dernier_temps_attaque_droite >= delai_attaque_droite else 100
    icone_gauche = pygame.transform.scale(icone_attaque_gauche, (taille_icone, taille_icone)).copy()
    icone_droite = pygame.transform.scale(icone_attaque_droite, (taille_icone, taille_icone)).copy()
    icone_gauche.fill((255, 255, 255, opacite_gauche), special_flags=pygame.BLEND_RGBA_MULT)
    icone_droite.fill((255, 255, 255, opacite_droite), special_flags=pygame.BLEND_RGBA_MULT)
    ecran.blit(icone_gauche, (pos_x, pos_y))
    ecran.blit(icone_droite, (pos_x + espacement, pos_y))

def scroll_background():
    """
    Gère le défilement horizontal du fond.
    """
    global decalage_x, indice_fond, direction_defilement
    ecran.blit(images_fond[indice_fond], (-decalage_x, 0))
    ecran.blit(images_fond[(indice_fond + 1) % len(images_fond)], (LARGEUR - decalage_x, 0))
    decalage_x += VITESSE * direction_defilement
    if direction_defilement > 0 and decalage_x >= LARGEUR:
        decalage_x = 0
        indice_fond = (indice_fond + 1) % len(images_fond)
    elif direction_defilement < 0 and decalage_x <= 0:
        decalage_x = LARGEUR
        indice_fond = (indice_fond - 1) % len(images_fond)

def process_spawn_queue(current_time):
    """
    Traite la file de spawn et fait apparaître les rats (petits ou grands)
    en jouant le son correspondant sur un canal dédié.
    """
    global file_spawn
    i = 0
    while i < len(file_spawn):
        temps_spawn, est_grand, pos_x = file_spawn[i]
        if current_time >= temps_spawn:
            rat = Rat(est_grand)
            rat.rect.x = pos_x
            if est_grand:
                canal = pygame.mixer.find_channel(force=True)
                if canal:
                    canal.play(son_spawn_rat_grand, loops=-1)
                    rat.canal_spawn = canal
            else:
                canal = pygame.mixer.find_channel(force=True)
                if canal:
                    canal.play(son_spawn_rat_petit, loops=-1)
                    rat.canal_spawn = canal
            ennemis.append(rat)
            file_spawn.pop(i)
        else:
            i += 1

def game_over_screen():
    """
    Affiche l'écran de Game Over avec une animation de sliding,
    et attend que l'utilisateur choisisse de redémarrer ou quitter.
    """
    pygame.mixer.stop()
    clock = pygame.time.Clock()
    background = images_fond[0]
    game_over_bg_alpha = image_game_over_bg.copy()
    game_over_bg_alpha.set_alpha(215)
    slide_y = -HAUTEUR
    vitesse_animation = 25  # Vitesse plus lente pour le sliding

    while slide_y < 0:
        ecran.blit(background, (0, 0))
        ecran.blit(game_over_bg_alpha, (0, slide_y))
        ecran.blit(image_game_over_fg, (0, slide_y))
        pygame.display.update()
        slide_y += vitesse_animation
        clock.tick(60)

    largeur_bouton, hauteur_bouton = 200, 50
    rect_restart = pygame.Rect(LARGEUR / 2 - largeur_bouton - 20, HAUTEUR / 2, largeur_bouton, hauteur_bouton)
    rect_quit = pygame.Rect(LARGEUR / 2 + 20, HAUTEUR / 2, largeur_bouton, hauteur_bouton)
    police_petite = pygame.font.Font(None, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos_souris = pygame.mouse.get_pos()
                if rect_restart.collidepoint(pos_souris):
                    return "restart"
                elif rect_quit.collidepoint(pos_souris):
                    return "quit"
        ecran.blit(background, (0, 0))
        ecran.blit(game_over_bg_alpha, (0, 0))
        ecran.blit(image_game_over_fg, (0, 0))
        pygame.draw.rect(ecran, (255, 255, 255), rect_restart)
        pygame.draw.rect(ecran, (255, 255, 255), rect_quit)
        texte_restart = police_petite.render("Restart", True, (0, 0, 0))
        texte_quit = police_petite.render("Quit", True, (0, 0, 0))
        ecran.blit(texte_restart, (rect_restart.x + (largeur_bouton - texte_restart.get_width()) / 2,
                                    rect_restart.y + (hauteur_bouton - texte_restart.get_height()) / 2))
        ecran.blit(texte_quit, (rect_quit.x + (largeur_bouton - texte_quit.get_width()) / 2,
                                 rect_quit.y + (hauteur_bouton - texte_quit.get_height()) / 2))
        pygame.display.update()
        clock.tick(60)

def main():
    """
    Boucle principale du jeu :
    - Gestion des événements
    - Mise à jour du joueur et des rats
    - Défilement du fond et gestion des spawns
    - Affichage du Game Over et redémarrage ou sortie du jeu.
    """
    global decalage_x, indice_fond, direction_defilement, transition_finale_lancee, progression_transition_finale
    global debut_anim_attaque_gauche, debut_anim_attaque_droite, dernier_temps_attaque_gauche, dernier_temps_attaque_droite
    global attaque_droite_speciale_jouee, file_spawn, ennemis, animations_mort, player

    decalage_x = 0
    indice_fond = 0
    direction_defilement = 0
    transition_finale_lancee = False
    progression_transition_finale = 0
    debut_anim_attaque_gauche = None
    debut_anim_attaque_droite = None
    dernier_temps_attaque_gauche = 0
    dernier_temps_attaque_droite = 0
    attaque_droite_speciale_jouee = False
    file_spawn = []
    ennemis = []
    animations_mort = []

    player = Player(LARGEUR // 3, HAUTEUR - 100)

    dernier_spawn_petit = pygame.time.get_ticks()
    dernier_spawn_grand = pygame.time.get_ticks()
    temps_depart = pygame.time.get_ticks()
    temps_arret_spawn = temps_depart + DUREE_NIVEAU * 1000 - 4300

    clock = pygame.time.Clock()
    en_cours = True

    while en_cours:
        temps_actuel = pygame.time.get_ticks()
        temps_ecoule = (temps_actuel - temps_depart) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Attaque gauche (bouton 1)
                if event.button == 1:
                    if temps_actuel - dernier_temps_attaque_gauche >= delai_attaque_gauche:
                        canal = pygame.mixer.find_channel()  # Recherche d'un canal libre
                        if canal:
                            canal.play(son_attaque_gauche)
                        touche = False
                        for ennemi in ennemis[:]:
                            if (not ennemi.est_grand) and abs(ennemi.rect.centerx - player.rect.centerx) <= 350:
                                ennemi.take_damage("clic_gauche")
                                touche = True
                        dernier_temps_attaque_gauche = temps_actuel
                        if touche:
                            debut_anim_attaque_gauche = temps_actuel

                # Attaque droite (bouton 3)
                elif event.button == 3:
                    if temps_actuel - dernier_temps_attaque_droite >= delai_attaque_droite:
                        canal = pygame.mixer.find_channel()
                        if canal:
                            if (not attaque_droite_speciale_jouee) and (random.random() < 0.2):
                                canal.play(son_attaque_droite_special)
                                attaque_droite_speciale_jouee = True
                            else:
                                canal.play(son_attaque_droite_defaut)
                        touche = False
                        for ennemi in ennemis[:]:
                            portee_attaque = 170
                            if ennemi.est_grand:
                                portee_attaque += (TAILLE_RAT_GRAND - TAILLE_RAT_PETIT) // 2
                            if abs(ennemi.rect.centerx - player.rect.centerx) <= portee_attaque:
                                ennemi.take_damage("clic_droite")
                                touche = True
                        dernier_temps_attaque_droite = temps_actuel
                        if touche:
                            debut_anim_attaque_droite = temps_actuel

        touches = pygame.key.get_pressed()
        # Gestion du son de déplacement
        if player.au_sol and touches[pygame.K_d]:
            if not canal_pas.get_busy():
                canal_pas.play(son_pas)
        else:
            if canal_pas.get_busy():
                canal_pas.stop()

        # Gestion du défilement du fond ou de la transition finale
        if temps_ecoule < DUREE_NIVEAU:
            if touches[pygame.K_d]:
                direction_defilement = 1
            elif touches[pygame.K_q]:
                direction_defilement = -1
            else:
                direction_defilement = 0

            if direction_defilement != 0:
                scroll_background()
            else:
                ecran.blit(images_fond[indice_fond], (-decalage_x, 0))
                ecran.blit(images_fond[(indice_fond + 1) % len(images_fond)], (LARGEUR - decalage_x, 0))
        else:
            if not transition_finale_lancee:
                transition_finale_lancee = True
                progression_transition_finale = 0
            if progression_transition_finale < 3840 - LARGEUR:
                ecran.blit(image_fond_combine, (-progression_transition_finale, 0))
                progression_transition_finale += VITESSE
            else:
                ecran.blit(image_fond_final, (0, 0))

        ecran.blit(image_sol, (0, SOL_Y))
        player.jump(touches)
        player.apply_gravity()
        # Mise à jour de l'état du joueur en fonction des touches pour gérer l'animation et l'orientation
        if touches[pygame.K_d]:
            player.action = 'walk'
            player.direction = 'droite'
        elif touches[pygame.K_q]:
            player.action = 'walk'
            player.direction = 'gauche'
        else:
            player.action = 'idle'

        player.update()   # Actualise l'animation
        player.display()  # Affiche le sprite animé du player
        player.display_hp()
        display_attack_icons()

        # Animation d'attaque gauche (fade-out)
        if debut_anim_attaque_gauche is not None:
            ecart = temps_actuel - debut_anim_attaque_gauche
            if ecart < duree_anim_attaque:
                alpha = int(255 * (1 - ecart / duree_anim_attaque))
                image_temp = anim_attaque_gauche.copy()
                image_temp.set_alpha(alpha)
                pos_anim = (player.rect.centerx + 50, player.rect.centery - 95)
                ecran.blit(image_temp, pos_anim)
            else:
                debut_anim_attaque_gauche = None

        # Animation d'attaque droite (fade-out)
        if debut_anim_attaque_droite is not None:
            ecart = temps_actuel - debut_anim_attaque_droite
            if ecart < duree_anim_attaque:
                alpha = int(255 * (1 - ecart / duree_anim_attaque))
                image_temp = anim_attaque_droite.copy()
                image_temp.set_alpha(alpha)
                pos_anim = (player.rect.centerx + 75, player.rect.centery - 95)
                ecran.blit(image_temp, pos_anim)
            else:
                debut_anim_attaque_droite = None

        # Mise à jour des animations de mort (tête et queue)
        for anim in animations_mort[:]:
            anim["pos"][1] += anim["vitesse"]
            ecran.blit(anim["image"], anim["pos"])
            if anim["pos"][1] > HAUTEUR:
                animations_mort.remove(anim)

        # Gestion des spawns
        if temps_actuel < temps_arret_spawn:
            if temps_ecoule >= 10:
                intervalle_spawn_petit = random.randint(INTERVALLE_MIN_SPAWN, INTERVALLE_MAX_SPAWN)
                if temps_actuel - dernier_spawn_petit > intervalle_spawn_petit:
                    nb_spawn = random.randint(1, 4)
                    pos_base_x = LARGEUR
                    distance_separation = 100
                    for i in range(nb_spawn):
                        file_spawn.append((temps_actuel + i * 1000, False, pos_base_x + i * distance_separation))
                    dernier_spawn_petit = temps_actuel

            if 45 <= temps_ecoule < 70:
                intervalle_spawn_grand = random.randint(3000, 5000)
                if temps_actuel - dernier_spawn_grand > intervalle_spawn_grand:
                    nb_spawn = random.randint(1, 3)
                    pos_base_x = LARGEUR
                    distance_separation = 2000
                    for i in range(nb_spawn):
                        file_spawn.append((temps_actuel + i * 1000, True, pos_base_x + i * distance_separation))
                    dernier_spawn_grand = temps_actuel

            if temps_ecoule >= DUREE_NIVEAU - 30:
                intervalle_chaos = random.randint(1000, 3000)
                if temps_actuel - dernier_spawn_petit > intervalle_chaos:
                    nb_spawn = random.randint(1, 4)
                    pos_base_x = LARGEUR
                    distance_separation = 100
                    for i in range(nb_spawn):
                        file_spawn.append((temps_actuel + i * 1000, False, pos_base_x + i * distance_separation))
                    dernier_spawn_petit = temps_actuel

                if temps_actuel - dernier_spawn_grand > intervalle_chaos:
                    nb_spawn = random.randint(1, 2)
                    pos_base_x = LARGEUR
                    distance_separation = 100
                    for i in range(nb_spawn):
                        file_spawn.append((temps_actuel + i * 1000, True, pos_base_x + i * distance_separation))
                    dernier_spawn_grand = temps_actuel

        process_spawn_queue(temps_actuel)

        for ennemi in ennemis[:]:
            ennemi.move(temps_actuel)
        for ennemi in ennemis:
            if not ennemi.est_grand:
                ennemi.display(temps_actuel)
        for ennemi in ennemis:
            if ennemi.est_grand:
                ennemi.display(temps_actuel)

        pygame.display.update()
        clock.tick(60)

        if player.pv <= 0:
            en_cours = False

    choix = game_over_screen()
    if choix == "restart":
        main()  # Redémarrage
    else:
        pygame.quit()
        sys.exit()

main()
