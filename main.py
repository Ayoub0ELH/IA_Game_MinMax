# Importation des modules nécessaires
import pygame       # Bibliothèque pour créer des jeux en 2D
import sys          # Pour gérer la fermeture de la fenêtre
import copy         # Pour copier profondément des structures comme la grille

# Initialisation de Pygame
pygame.init()

# Configuration de la police de texte
font = pygame.font.SysFont(None, 36)

# Définition de la taille de la grille (7x7)
nb_lignes, nb_colonnes = 7, 7

# Message affiché en bas de l'écran (victoire/défaite)
message = ""

# Constantes
taille_case = 80  # Taille d'une case en pixels
largeur, hauteur = 7 * taille_case, 7 * taille_case + 100  # Taille de la fenêtre avec zone de texte
blanc, noir, rouge, bleu = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255)  # Couleurs utiles

# Création de la fenêtre de jeu
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Isola")  # Titre de la fenêtre

# Création de la grille initiale : 1 signifie case libre, 0 signifie supprimée
grille = [[1] * 7 for _ in range(7)]

# Position initiale des joueurs : humain en haut, IA en bas
joueurs = [(0, 3), (6, 3)]
joueur_actuel = 0  # 0 = humain, 1 = IA

# Fonction qui dessine la grille et les joueurs
def dessiner_grille():
    for y in range(7):
        for x in range(7):
            couleur = blanc if grille[y][x] else noir  # Blanc si case présente, sinon noir
            pygame.draw.rect(fenetre, couleur, (x * taille_case, y * taille_case, taille_case, taille_case))
            pygame.draw.rect(fenetre, noir, (x * taille_case, y * taille_case, taille_case, taille_case), 2)
    # Dessin des joueurs
    for i, (x, y) in enumerate(joueurs):
        couleur = rouge if i == 0 else bleu  # Rouge pour humain, bleu pour IA
        pygame.draw.circle(fenetre, couleur,
                           (x * taille_case + taille_case // 2, y * taille_case + taille_case // 2),
                           taille_case // 3)

# Affiche un message texte en bas de l'écran
def dessiner_zone_texte():
    texte = font.render(message, True, blanc)
    fenetre.fill(noir, (0, nb_lignes * taille_case, largeur, 50))
    fenetre.blit(texte, (10, nb_lignes * taille_case + 10))

# retourne True si c'est valide
def mouvement_valide(x, y, pos, autres_pos, grille):
    if 0 <= x < 7 and 0 <= y < 7 and grille[y][x] == 1 and (x, y) != autres_pos:
        x_j, y_j = pos
        return abs(x - x_j) <= 1 and abs(y - y_j) <= 1  # Mouvement dans les cases voisines
    return False

# Compte le nombre de mouvements possibles autour d’une position
def compter_mouvements(pos, grille, autres_pos):
    x, y = pos
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    return sum(
        0 <= x + dx < 7 and 0 <= y + dy < 7 and grille[y + dy][x + dx] == 1 and (x + dx, y + dy) != autres_pos
        for dx, dy in directions
    )

# Fonction d’évaluation pour l’IA (différence entre les mouvements possibles)
def evaluation(grille, pos_ia, pos_adv):
    return compter_mouvements(pos_ia, grille, pos_adv) - compter_mouvements(pos_adv, grille, pos_ia)

# Retourne toutes les cases où le joueur peut se déplacer
def get_all_moves(pos, grille, autres_pos):
    x, y = pos
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    return [(x + dx, y + dy) for dx, dy in directions if mouvement_valide(x + dx, y + dy, pos, autres_pos, grille)]

# Retourne toutes les cases pouvant être détruites
def get_all_removals(grille, pos1, pos2):
    return [(x, y) for y in range(7) for x in range(7) if grille[y][x] == 1 and (x, y) != pos1 and (x, y) != pos2]

# Algorithme MinMax avec élagage alpha-bêta
def minmax(grille, profondeur, is_max, pos_ia, pos_adv, alpha, beta, profondeur_max=50):
    # Condition d’arrêt (feuille ou joueur bloqué)
    if profondeur == profondeur_max or compter_mouvements(pos_ia if is_max else pos_adv, grille,
                                                          pos_adv if is_max else pos_ia) == 0:  # fin de partie
        return evaluation(grille, pos_ia, pos_adv), None, None

    best_move = None
    best_remove = None

    if is_max:  # Tour de l’IA (maximiser)
        max_eval = -1000
        for move in get_all_moves(pos_ia, grille, pos_adv):
            for remove in get_all_removals(grille, move, pos_adv):
                grille_copy = copy.deepcopy(grille)
                grille_copy[remove[1]][remove[0]] = 0
                eval_child, _, _ = minmax(grille_copy, profondeur + 1, False, move, pos_adv, alpha, beta,
                                          profondeur_max)
                if eval_child > max_eval:
                    max_eval = eval_child
                    best_move = move
                    best_remove = remove
                alpha = max(alpha, eval_child)
                if beta <= alpha:
                    break
            if beta <= alpha:
                break
        return max_eval, best_move, best_remove

    else:  # Tour du joueur (minimiser)
        min_eval = 1000
        for move in get_all_moves(pos_adv, grille, pos_ia):
            for remove in get_all_removals(grille, move, pos_ia):
                grille_copy = copy.deepcopy(grille)
                grille_copy[remove[1]][remove[0]] = 0
                eval_child, _, _ = minmax(grille_copy, profondeur + 1, True, pos_ia, move, alpha, beta, profondeur_max)
                if eval_child < min_eval:
                    min_eval = eval_child
                    best_move = move
                    best_remove = remove
                beta = min(beta, eval_child)
                if beta <= alpha:
                    break
            if beta <= alpha:
                break
        return min_eval, best_move, best_remove

# Vérifie si un joueur est bloqué (aucun mouvement possible)
def partie_terminee(pos, grille, autres_pos):
    return all(
        not mouvement_valide(pos[0] + dx, pos[1] + dy, pos, autres_pos, grille)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    )

# === Boucle principale du jeu ===
running = True
selection_phase = True  # True si le joueur doit se déplacer, False s’il doit supprimer une case

while running:
    dessiner_grille()
    dessiner_zone_texte()
    pygame.display.flip()

    if joueur_actuel == 1:  # Tour de l'IA
        _, move, destroy = minmax(grille, 0, True, joueurs[1], joueurs[0], -1000, 1000, 3)
        if move and destroy:
            joueurs[1] = move               # Déplacement de l'IA
            grille[destroy[1]][destroy[0]] = 0  # Suppression d’une case par l'IA
        if partie_terminee(joueurs[0], grille, joueurs[1]):
            message = "Joueur 1(rouge) a perdu !"
        if partie_terminee(joueurs[1], grille, joueurs[0]):
            message = "Joueur 2(bleu) a perdu !"
        joueur_actuel = 0
        continue  # Revenir au début de la boucle

    # Gestion des événements (souris, fermeture)
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
                        message = "Joueur 2(rouge) a perdu !"
                    if partie_terminee(joueurs[0], grille, joueurs[1]):
                        message = "Joueur 1(bleu) a perdu !"
                    joueur_actuel = 1
                    selection_phase = True

# Fermeture du jeu
pygame.quit()
sys.exit()
