import pygame
import sys
import copy

from main import hauteur

pygame.init()
font = pygame.font.SysFont(None, 36)
nb_lignes, nb_colonnes = 7, 7
message = ""
hauteur_msg = 100

# Constantes
taille_case = 80
largeur, hauteur = 7 * taille_case, 7 * taille_case + hauteur_msg
blanc, noir, rouge, bleu = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255)

fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Isola")

# Grille et positions initiales
grille = [[1] * 7 for _ in range(7)]                # on crée la matrice
joueurs = [(0, 3), (6, 3)]                          # position initiale des joueurs [joueur_humain, IA]
joueur_actuel = 0                                   # 0 = humain, 1 = IA

def dessiner_grille():
    for y in range(7):
        for x in range(7):
            couleur = blanc if grille[y][x] else noir
            pygame.draw.rect(fenetre, couleur, (x * taille_case, y * taille_case, taille_case, taille_case))
            pygame.draw.rect(fenetre, noir, (x * taille_case, y * taille_case, taille_case, taille_case), 2)
    for i, (x, y) in enumerate(joueurs):
        couleur = rouge if i == 0 else bleu
        pygame.draw.circle(fenetre, couleur, (x * taille_case + taille_case // 2, y * taille_case + taille_case // 2), taille_case // 3)

def dessiner_zone_texte():
    texte = font.render(message, True, blanc)
    fenetre.fill(noir, (0, nb_lignes * taille_case, largeur, 50))
    fenetre.blit(texte, (10, nb_lignes * taille_case + 10))

def mouvement_valide(x, y, pos, autres_pos, grille):        # verifie si une case peut accueillir un joueur
    if 0 <= x < 7 and 0 <= y < 7 and grille[y][x] == 1 and (x, y) != autres_pos:    # limite de la carte, case blanche, pas de joueurs dessus
        x_j, y_j = pos      #position du joueur actuellement
        return abs(x - x_j) <= 1 and abs(y - y_j) <= 1      #retourne True si il y'a une seule case de diff
    return False                    #sinon false

def compter_mouvements(pos, grille, autres_pos):        #compte le nb de case accessible autour d'un joueur
    x, y = pos
    directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
    return sum(
        0 <= x+dx < 7 and 0 <= y+dy < 7 and grille[y+dy][x+dx] == 1 and (x+dx, y+dy) != autres_pos
        for dx, dy in directions
    )

def evaluation(grille, pos_ia, pos_adv):    # permet d'évaluer un état de jeu
    return compter_mouvements(pos_ia, grille, pos_adv) - compter_mouvements(pos_adv, grille, pos_ia)

def get_all_moves(pos, grille, autres_pos):
    x, y = pos
    directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
    return [(x+dx, y+dy) for dx, dy in directions if mouvement_valide(x+dx, y+dy, pos, autres_pos, grille)]

def get_all_removals(grille, pos1, pos2):
    return [(x, y) for y in range(7) for x in range(7) if grille[y][x] == 1 and (x, y) != pos1 and (x, y) != pos2]

def minmax(grille, profondeur, is_max, pos_ia, pos_adv, alpha, beta):
    if profondeur == 0 or compter_mouvements(pos_ia, grille, pos_adv) == 0:
        return evaluation(grille, pos_ia, pos_adv), None, None
    meilleurs_coups = []
    best_val = -float('inf') if is_max else float('inf')        #MAX veut maximiser ses gains donc on commence a -infini
    meilleurs_deplacement, meilleurs_suppression = None, None

    pos_joueur = pos_ia if is_max else pos_adv
    pos_autre = pos_adv if is_max else pos_ia


def partie_terminee(pos, grille, autres_pos):
    return all(
        not mouvement_valide(pos[0] + dx, pos[1] + dy, pos, autres_pos, grille)
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
    )

# Boucle de jeu
running = True
selection_phase = True

while running:
    dessiner_grille()
    dessiner_zone_texte()
    pygame.display.flip()

    if joueur_actuel == 1:  # IA
        _, move, destroy = minmax(grille, 2, True, joueurs[1], joueurs[0], -float('inf'), float('inf'))
        if move and destroy:
            joueurs[1] = move
            grille[destroy[1]][destroy[0]] = 0
        if partie_terminee(joueurs[0], grille, joueurs[1]):
            message = "Joueur 1 a perdu !"
        else:
            message = "C'est au tour de l'humain !"  # Message que l'IA a joué
        joueur_actuel = 0
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0] // taille_case, event.pos[1] // taille_case

            if selection_phase:
                if mouvement_valide(x, y, joueurs[0], joueurs[1], grille):
                    joueurs[0] = (x, y)
                    selection_phase = False
            else:
                if (x, y) != joueurs[0] and (x, y) != joueurs[1] and grille[y][x] == 1:
                    grille[y][x] = 0
                    if partie_terminee(joueurs[1], grille, joueurs[0]):
                        message = "Joueur 2 a perdu !"
                    joueur_actuel = 1
                    selection_phase = True

pygame.quit()
sys.exit()
