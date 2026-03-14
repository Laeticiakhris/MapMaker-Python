import os
import random
from fltk import *

# -----------------------------
# Tâche 1 : Lecture des fichiers de tuiles
# -----------------------------
def cree_dico(chemin):
    dico = {} #initialisation d'un dictionnaire vide qui contiendra les tuiles disponibles
    for fichier in os.listdir(chemin): #on parcourt tous les fichiers dans le dossier "chemin"
        if fichier.endswith(".png"): #on ne garde que les fichiers qui se terminent par .png
            nom = fichier[:-4] #on retire l'extension '.png' pour obtenir juste le nom de la tuile
            dico[nom] = os.path.join(chemin, fichier) #on ajoute une entrée dans le dictionnaire (clé: nom de la tuile, valeur: le chemin d’accès complet au fichier image)
    return dico #on renvoie le dictionnaire contenant toutes les tuiles trouvées

# -----------------------------
# Tâche 2 : Moteur de placement des tuiles
# -----------------------------
def get_biomes(tuile):
    return tuile[0], tuile[1], tuile[2], tuile[3] #récupère les biomes : haut, droite, bas, gauche

def biome_compatible(b1, b2):
    return b1 == b2 #deux biomes sont compatibles s'ils sont identiques

def emplacement_valide(grille, i, j, tuile): #vérifie si on peut placer la tuile à la position (i, j)
    haut, droite, bas, gauche = get_biomes(tuile)
    lignes = len(grille) #nombre de lignes de la grille 
    colonnes = len(grille[0]) #nombre de colonnes de la grille

    if i > 0 and grille[i-1][j]: #vérifier si la tuile du dessus est compatible avec le haut de la tuile actuelle
        if not biome_compatible(haut, get_biomes(grille[i-1][j])[2]): #comparaison avec le bas de la tuile du dessus
            return False
    if i < lignes - 1 and grille[i+1][j]: #vérifier si la tuile du dessous est compatible avec le bas de la tuile actuelle
        if not biome_compatible(bas, get_biomes(grille[i+1][j])[0]): #comparaison avec le haut de la tuile du dessous
            return False
    if j > 0 and grille[i][j-1]: #vérifier si la tuile à gauche est compatible avec le côté gauche de la tuile actuelle
        if not biome_compatible(gauche, get_biomes(grille[i][j-1])[1]): #comparaison avec le côté droit de la tuile de gauche
            return False
    if j < colonnes - 1 and grille[i][j+1]: #vérifier si la tuile à droite est compatible avec le côté droit de la tuile actuelle
        if not biome_compatible(droite, get_biomes(grille[i][j+1])[3]): #comparaison avec le côté gauche de la tuile de droite
            return False

    return True

def tuiles_possibles(grille, i, j, dico): #renvoie la liste de toutes les tuiles du dictionnaire qui peuvent être placées en (i, j)
    return [t for t in dico if emplacement_valide(grille, i, j, t)]

#------------------------------
# Tâche 2 : Décors
#------------------------------

#--------------------------placement_automatique--------------------------

decors = []  #liste globale contenant tous les décors placés sur la carte, chaque décor est un dictionnaire avec un nom et des coordonnées
mode_decor = False  #indique si on est en mode placement manuel de décor
decor_selectionne = None  #contiendra le nom du décor sélectionné lorsqu'on est en mode manuel


def ajouter_decor(nom, x, y): #fonction qui ajoute un décor dans la liste globale
    decor = {"nom": nom, "x": x, "y": y} #crée un dictionnaire contenant le nom du décor et sa position (x, y)
    decors.append(decor)  #ajoute le dictionnaire à la liste globale des décors

def charger_decors(): #fonction pour charger les images de décors depuis les dossiers "decors/mer" et "decors/terre"
    dico_decors = {
        "mer": {}, #dictionnaire pour stocker les décors spécifiques au biome mer
        "terre": {} #dictionnaire pour stocker les décors spécifiques au biome plaine
    }
    for biome in ["mer", "terre"]:  #parcourt les deux dossiers de décors : "mer" et "terre"
        chemin = os.path.join("decors", biome)  #construit le chemin d'accès au dossier
        for fichier in os.listdir(chemin):  #parcourt tous les fichiers du dossier
            if fichier.endswith(".png"):  #ne garde que les fichiers image au format .png
                nom = fichier[:-4]  #retire l'extension ".png" pour obtenir le nom de base
                biome_nom = "mer" if biome == "mer" else "terre"  #identifie le type de biome (au cas où on veuille adapter plus tard)
                dico_decors[biome_nom][nom] = os.path.join(chemin, fichier)  #associe le nom à son chemin d'accès
    return dico_decors  #retourne le dictionnaire complet des décors chargés

dico_decors = charger_decors() #appelle immédiatement la fonction pour charger les décors au lancement du programme
        

def decor_automatique():
    decors.clear()  #supprime tous les décors précédents (réinitialise l'affichage)
    deja_place = set()  #ensemble pour éviter de placer deux fois un décor au même endroit

    for i in range(DIM):  #parcourt toutes les lignes de la grille
        for j in range(DIM):  #parcourt toutes les colonnes de la grille
            tuile = grille[i][j]  #récupère la tuile à la position (i, j)
            if tuile is None or not isinstance(tuile, str):  #ignore les cases vides ou non valides
                continue

            biomes = get_biomes(tuile)  #récupère les 4 biomes de la tuile (haut, droite, bas, gauche)
            directions = ['haut', 'droite', 'bas', 'gauche']  #étiquettes (pas utilisées ici mais utiles pour lecture)
            dx_dy = [ (0, -1), (1, 0), (0, 1), (-1, 0) ]  #offsets pour se déplacer dans la grille selon chaque direction
            offsets_pixels = [
                (TAILLE_CASE//2, 0),   #coordonnées pour placer le décor en haut de la tuile
                (TAILLE_CASE, TAILLE_CASE//2),  #à droite de la tuile
                (TAILLE_CASE//2, TAILLE_CASE),  #en bas
                (0, TAILLE_CASE//2)   #à gauche
            ]

            for idx, biome in enumerate(biomes):  #parcourt chaque côté de la tuile
                if biome not in ['S', 'P']:  #on ne place des décors que pour les biomes 'S' ou 'P'
                    continue

                dir_x, dir_y = dx_dy[idx]  #direction vers la tuile voisine (gauche, droite, haut, bas)
                ni, nj = i + dir_y, j + dir_x  #coordonnées de la tuile voisine
                x0, y0 = j * TAILLE_CASE, i * TAILLE_CASE  #coordonnées en pixels du coin supérieur gauche de la tuile actuelle

                #coordonnée par défaut pour placer le décor sur le bord de la tuile
                px, py = x0 + offsets_pixels[idx][0], y0 + offsets_pixels[idx][1]

                biome_match = False  #indique si le biome est prolongé dans la tuile voisine
                if 0 <= ni < DIM and 0 <= nj < DIM:  #vérifie que la tuile voisine est dans les limites
                    voisin = grille[ni][nj]  #récupère la tuile voisine
                    if voisin:
                        biome_voisin = get_biomes(voisin)[(idx + 2) % 4]  #récupère le biome opposé dans la tuile voisine
                        if biome_voisin == biome:  #si les deux tuiles ont un biome continu
                            biome_match = True

                if biome_match:
                    #place le décor au centre entre les deux tuiles (fusion visuelle)
                    px = (j + nj) * TAILLE_CASE // 2 + TAILLE_CASE // 2
                    py = (i + ni) * TAILLE_CASE // 2 + TAILLE_CASE // 2

                nom_decor = None  #nom du décor à placer
                if biome == 'S' and dico_decors["mer"]:  #si c’est de l’eau, on pioche un décor marin
                    nom_decor = random.choice(list(dico_decors["mer"].keys()))
                elif biome == 'P' and dico_decors["terre"]:  #si c’est une plaine, on pioche un décor terrestre
                    nom_decor = random.choice(list(dico_decors["terre"].keys()))

                if nom_decor:
                    cle = (i, j, idx)  #identifie de façon unique ce bord de tuile
                    if 0 <= ni < DIM and 0 <= nj < DIM:  #vérifie que la position du décor est bien dans la grille
                        if cle not in deja_place:  #évite les doublons de placement
                            ajouter_decor(nom_decor, px, py)  #ajoute le décor à la position calculée
                            deja_place.add(cle)  #marque cette position comme déjà utilisée

                        
 #--------------------------placement_manuel--------------------------                       
def detecte_bord_et_biome(i, j, x, y):
    
    cx = j * TAILLE_CASE + TAILLE_CASE // 2 #calcule la coordonnée x le centre de la tuile en pixels
    cy = i * TAILLE_CASE + TAILLE_CASE // 2 #calcule la coordonnée y le centre de la tuile en pixels
    dx = x - cx  #différence horizontale entre le clic et le centre de la tuile
    dy = y - cy  #différence verticale entre le clic et le centre de la tuile
 

    if abs(dx) > abs(dy): #détermine si le clic est plutôt horizontal ou vertical
        if dx > 0: #clic à droite de la tuile
            direction = (0, 1)
            biome = get_biomes(grille[i][j])[1]  # droite
        else: #clic à gauche de la tuile
            direction = (0, -1)
            biome = get_biomes(grille[i][j])[3]  # gauche
    else:
        if dy > 0: #clic en bas de la tuile
            direction = (1, 0)
            biome = get_biomes(grille[i][j])[2]  # bas
        else: #clic en haut de la tuile
            direction = (-1, 0)
            biome = get_biomes(grille[i][j])[0]  # haut

    di, dj = direction #calcule la position où placer le décor, entre la tuile actuelle et sa voisine dans la direction
    decor_x = (j + dj / 2 + 0.5) * TAILLE_CASE  #position x du décor à mi-chemin entre la tuile et sa voisine
    decor_y = (i + di / 2 + 0.5) * TAILLE_CASE  #position y du décor à mi-chemin entre la tuile et sa voisine
    return biome, decor_x, decor_y #retourne le biome sélectionné et la position idéale du décor

def menu_selection_decor(liste):
    if not liste: #si la liste est vide, on ne propose rien
        return None

    colonnes = 5 #le nombre de colonnes pour afficher les décors
    lignes = (len(liste) + colonnes - 1) // colonnes # Calcule le nombre de lignes nécessaires selon le nombre de décors
    taille = 48 #taille d'affichage de chaque case dans le menu
    x0 = (largeur_fenetre() - colonnes * taille) // 2 #position de départ horizontale pour centrer le menu
    y0 = (hauteur_fenetre() - lignes * taille) // 2   #position de départ verticale pour centrer le menu

    positions = {}  #dictionnaire pour associer chaque zone à un décor
    objets = []     #liste des objets graphiques créés, pour pouvoir les effacer ensuite

    for idx, decor in enumerate(liste): #parcourt tous les décors à afficher
        i, j = divmod(idx, colonnes) #convertit l'index en coordonnées ligne/colonne
        x = x0 + j * taille  #calcule la position x du décor
        y = y0 + i * taille  #calcule la position y du décor

        rect = rectangle(x, y, x + taille, y + taille, couleur="black", remplissage="black") #dessine un rectangle de sélection
        objets.append(rect)

        #affiche l'image du décor selon son biome
        if decor in dico_decors["mer"]:
            img = image(x, y, dico_decors["mer"][decor], largeur=45, hauteur=45, ancrage="nw")
            objets.append(img)
        elif decor in dico_decors["terre"]:
            img = image(x, y, dico_decors["terre"][decor], largeur=45, hauteur=45, ancrage="nw")
            objets.append(img)

        positions[(x, y, x + taille, y + taille)] = decor #enregistre la position de la zone cliquable liée à ce décor

    mise_a_jour()

    while True: #boucle d'attente d'un clic utilisateur
        ev = donne_ev() #récupère un évenement
        if ev and type_ev(ev) == "ClicGauche":
            x, y = abscisse(ev), ordonnee(ev) #coordonnées du clic
            for (x1, y1, x2, y2), decor in positions.items(): #vérifie si l'utilisateur a cliqué sur une zone contenant un décor
                if x1 <= x <= x2 and y1 <= y <= y2:
                    for obj in objets: #supprime tous les objets du menu
                        efface(obj)
                    mise_a_jour()
                    return decor #retourne le décor sélectionné
        elif ev and type_ev(ev) == "Touche" and touche(ev) == "Escape": #si l'utilisateur appuie sur Échap, on annule le menu
            for obj in objets:
                efface(obj)
            mise_a_jour()
            return None
        mise_a_jour()

def clic_decor_manuel(x, y):
    #convertit les coordonnées pixel en indices de la grille
    j = x // TAILLE_CASE
    i = y // TAILLE_CASE

    if 0 <= i < DIM and 0 <= j < DIM and grille[i][j]: #vérifie que la position est dans les limites de la grille et qu'une tuile y est placée
        biome, dx, dy = detecte_bord_et_biome(i, j, x, y) #détecte sur quel bord de la tuile on a cliqué, et récupère le biome correspondant + position du décor
        #vérifie que le décor ne sort pas de la carte (bord droit ou bas)
        cx = j * TAILLE_CASE + TAILLE_CASE // 2
        cy = i * TAILLE_CASE + TAILLE_CASE // 2
        dx_rel = x - cx
        dy_rel = y - cy
        if abs(dx_rel) > abs(dy_rel): #si le clic est plus éloigné sur l’axe horizontal que sur l’axe vertical
            if dx_rel > 0 and j == DIM - 1: #si on a cliqué à droite de la tuile ET qu'on est à la dernière colonne (bord droit de la grille)
                return #ne pas placer de décor
            if dx_rel < 0 and j == 0: #si on a cliqué à gauche de la tuile ET qu'on est à la première colonne (bord gauche)
                return #ne pas placer de décor
        else:
            if dy_rel > 0 and i == DIM - 1: #si on a cliqué en bas de la tuile ET qu'on est à la dernière ligne (bord bas)
                return #ne pas placer de décor
            if dy_rel < 0 and i == 0: #si on a cliqué en haut de la tuile ET qu'on est à la première ligne (bord haut)
                return #ne pas placer de décor
        if biome == "S": #selon le biome détecté, on récupère la liste des décors compatibles
            liste = list(dico_decors["mer"].keys())
        elif biome == "P":
            liste = list(dico_decors["terre"].keys())
        else: #si le biome n'est ni mer ni plaine, on affiche un message et on arrête
            print("Aucun décor ne peut être posé ici")
            return

        choix = menu_selection_decor(liste) #affiche le menu de sélection de décor à partir de la liste
        if choix: #si un décor a été sélectionné, on l’ajoute à la position calculée
            ajouter_decor(choix, dx, dy) #ajoute le décor à la liste globale
            dessiner_grille() #rafraîchit l’affichage pour inclure le nouveau décor
            print(f"Décor {choix} ajouté en ({dx}, {dy})")
        else:
            print("Aucun décor sélectionné.")
    else:
        print("Tuile invalide") #si clic en dehors de la grille ou sur une case vide


# -----------------------------
# Tâche 3 : Interface graphique FLTK
# -----------------------------
TAILLE_CASE = 70  #taille (en pixels) d'une case dans la grille
DIM = 10          #dimension de la grille : 10x10 cases

grille = [[None for _ in range(DIM)] for _ in range(DIM)] #initialise une grille vide
dico_tuiles = cree_dico("tuiles") #crée un dictionnaire contenant les chemins des fichiers image des tuiles

def dessiner_grille():
    efface_tout()  #efface tout le contenu de la fenêtre pour redessiner à zéro
    for i in range(DIM):  #parcours chaque ligne
        for j in range(DIM):  #parcours chaque colonne
            x, y = j * TAILLE_CASE, i * TAILLE_CASE  #coordonnées (en pixels) de la case
            #dessine un carré vide pour représenter la case (bord noir, fond beige)
            rectangle(x, y, x + TAILLE_CASE, y + TAILLE_CASE, couleur='black',
                      remplissage='#F5F5DC', epaisseur=1)
            tuile = grille[i][j]  #récupère le nom de la tuile présente à cette case (ou None)
            if isinstance(tuile, str) and tuile in dico_tuiles: #si une tuile est présente et son nom est reconnu dans le dictionnaire
                #affiche l'image de la tuile dans la case
                image(x, y, dico_tuiles[tuile], hauteur=70, largeur=70, ancrage='nw')

    #affichage des décors par-dessus les tuiles
    for decor in decors:  #parcourt tous les décors placés
        nom = decor["nom"]       #nom du décor
        x, y = decor["x"], decor["y"]  #position du décor en pixels
        if nom in dico_decors["mer"]: #si le décor appartient au biome mer on l'affiche avec l'image correspondante
            image(x, y, dico_decors["mer"][nom], largeur=25, hauteur=25, ancrage='center')
        elif nom in dico_decors["terre"]: #sinon s’il appartient au biome terre
            image(x, y, dico_decors["terre"][nom], largeur=20, hauteur=20, ancrage='center')

    mise_a_jour()  #rafraîchit l'affichage complet de la fenêtre

def afficher_tuiles(tuiles, dico_tuiles, x_offset, y_offset, colonnes, taille, espacement):
    positions = {}  #dictionnaire pour mémoriser les zones cliquables associées à chaque tuile
    for idx, tuile in enumerate(tuiles):  #parcourt chaque tuile à afficher
        i = idx // colonnes  #ligne dans la grille d'affichage
        j = idx % colonnes   #colonne dans la grille d'affichage
        x = x_offset + j * (taille + espacement)  #coordonnée X du coin supérieur gauche
        y = y_offset + i * (taille + espacement)  #coordonnée Y du coin supérieur gauche
        rectangle(x, y, x + 50, y + 50, couleur='black', remplissage='white', epaisseur=1)  #cadre de la tuile
        if tuile in dico_tuiles:  #si la tuile existe dans le dictionnaire, on affiche son image
            image(x, y, dico_tuiles[tuile], largeur=50, hauteur=50, ancrage='nw')
        else:  #sinon, on affiche juste son nom (utile pour le debug ou les tuiles textuelles)
            texte(x + taille // 2, y + taille // 2, tuile, ancrage='center')
        positions[(x, y, x + taille, y + taille)] = tuile #enregistre la zone cliquable correspondant à cette tuile
    return positions  #retourne les positions cliquables pour pouvoir les détecter ensuite



def afficher_boutons_pagination(page, total_pages, largeur, hauteur):
    fleche_gauche = fleche_droite = None  #variables pour contenir les objets des flèches (texte)
    bouton_hauteur = 40  #taille des boutons de pagination
    bouton_largeur = 40
    y_bouton = hauteur // 2 - bouton_hauteur // 2  #position Y centrée verticalement

    if page > 0:  #si on n'est pas à la première page, on affiche la flèche gauche
        x_gauche = 20
        rectangle(x_gauche, y_bouton, x_gauche + bouton_largeur, y_bouton + bouton_hauteur,
                  remplissage='gray', couleur='white')
        fleche_gauche = texte(x_gauche + bouton_largeur // 2, y_bouton + bouton_hauteur // 2,
                              "<", ancrage='center', couleur='white', taille=20)

    if page < total_pages - 1:  #si on n'est pas à la dernière page, on affiche la flèche droite
        x_droite = largeur - bouton_largeur - 20
        rectangle(x_droite, y_bouton, x_droite + bouton_largeur, y_bouton + bouton_hauteur,
                  remplissage='gray', couleur='white')
        fleche_droite = texte(x_droite + bouton_largeur // 2, y_bouton + bouton_hauteur // 2,
                              ">", ancrage='center', couleur='white', taille=20)

    return fleche_gauche, fleche_droite  #retourne les objets flèches pour détection de clic


def detecter_navigation(fleche_gauche, fleche_droite, page, total_pages):
    if fleche_gauche and est_objet_survole(fleche_gauche):  #si la souris est sur la flèche gauche
        return page - 1  #on demande à aller à la page précédente
    if fleche_droite and est_objet_survole(fleche_droite):  #si la souris est sur la flèche droite
        return page + 1  #on demande à aller à la page suivante
    return page  #sinon, on reste sur la même page


def detecter_clic_tuile(positions, x_click, y_click):
    for (x1, y1, x2, y2), tuile in positions.items():  #parcourt toutes les zones cliquables
        if x1 <= x_click <= x2 and y1 <= y_click <= y2:  #si le clic est dans la zone d’une tuile
            return tuile  #on retourne la tuile sélectionnée
    return None  #si le clic ne correspond à aucune tuile, on retourne rien


def menu_selection_tuile(possibles):
    TAILLE_CASE_MENU = 48  #taille d'une case dans le menu de sélection
    marge_bordure = 10  #marge autour du menu
    espacement_interne = 10  #espacement entre les tuiles dans le menu
    colonnes = 5  #nombre de colonnes dans le menu
    lignes_max_affichees = 6  #nombre max de lignes visibles à la fois
    tuiles_par_page = colonnes * lignes_max_affichees  #nombre total de tuiles affichables par page

    page = 0  #page actuelle
    total_pages = (len(possibles) + tuiles_par_page - 1) // tuiles_par_page  #nombre total de pages nécessaires

    while True:  #boucle d'affichage de la page courante
        efface_tout()  #efface tout l'écran
        dessiner_grille()  #redessine la grille de tuiles derrière

        debut = page * tuiles_par_page  #index de la première tuile à afficher dans cette page
        fin = min(debut + tuiles_par_page, len(possibles))  #index de la dernière tuile (non inclus)
        sous_liste = possibles[debut:fin]  #liste des tuiles à afficher sur cette page

        lignes = (len(sous_liste) + colonnes - 1) // colonnes  #nombre de lignes nécessaires pour cette page
        largeur_menu = colonnes * (TAILLE_CASE_MENU + espacement_interne) - espacement_interne  #largeur totale du menu
        hauteur_menu = lignes * (TAILLE_CASE_MENU + espacement_interne) - espacement_interne  #hauteur totale du menu
        x_offset = 800  #décalage horizontal pour positionner le menu à droite
        y_offset = (hauteur_fenetre() - hauteur_menu) // 2  #décalage vertical pour centrer le menu
        #dessine le fond du menu
        rectangle(x_offset - 10, y_offset - 10,
                  x_offset + largeur_menu + 10,
                  y_offset + hauteur_menu + 10,
                  couleur='black', remplissage='brown', epaisseur=4)

        #affiche les tuiles de la page actuelle
        positions = afficher_tuiles(sous_liste, dico_tuiles, x_offset, y_offset, colonnes,
                                    TAILLE_CASE_MENU, espacement_interne)

        #affiche les boutons de navigation (flèches)
        fleche_gauche, fleche_droite = afficher_boutons_pagination(
            page, total_pages, largeur_fenetre(), hauteur_fenetre()
        )

        mise_a_jour() #rafraîchit l'affichage

        while True: #boucle d'attente d'interaction utilisateur (clic ou touche)
            ev = donne_ev() #attend un événement
            if ev:
                tev = type_ev(ev) #type de l’événement
                if tev == 'ClicGauche':  #si clic gauche
                    x_click, y_click = abscisse_souris(), ordonnee_souris()  #coordonnées du clic

                    new_page = detecter_navigation(fleche_gauche, fleche_droite, page, total_pages) #vérifie si l'utilisateur a cliqué sur une flèche de navigation
                    if new_page != page:
                        page = new_page  #change de page
                        break  #recommence une nouvelle boucle avec la nouvelle page

                    tuile = detecter_clic_tuile(positions, x_click, y_click) #vérifie si l'utilisateur a cliqué sur une tuile
                    if tuile:
                        return tuile #retourne la tuile sélectionnée

                elif tev == 'Touche' and touche(ev) == 'Escape': #si l'utilisateur appuie sur Échap
                    return None  #annule la sélection
            mise_a_jour()  #rafraîchit l'affichage en continu



def clic_gauche(x, y):
    j = x // TAILLE_CASE  #convertit la coordonnée x (pixels) en indice de colonne
    i = y // TAILLE_CASE  #convertit la coordonnée y (pixels) en indice de ligne

    if 0 <= i < DIM and 0 <= j < DIM:  #vérifie que la case cliquée est bien dans la grille
        global mode_decor, decor_selectionne  #on accède aux variables globales
        if mode_decor and decor_selectionne: #si on est en mode décor (clic décor direct depuis menu simple)
            ajouter_decor(decor_selectionne, x, y)  #ajoute le décor à la position du clic
            dessiner_grille()  #met à jour l’affichage
            mode_decor = False  #désactive le mode décor
            decor_selectionne = None  #réinitialise le décor sélectionné
            return  #sort de la fonction (pas de placement de tuile dans ce cas)
        
        if grille[i][j] is not None: #si une tuile est déjà placée ici, on ne fait rien
            print(f"Case ({i},{j}) déjà remplie.")
            return

        possibles = tuiles_possibles(grille, i, j, dico_tuiles.keys()) #cherche toutes les tuiles compatibles à cette position
        if not possibles: #aucune tuile compatible
            print(f"Pas de tuile compatible pour ({i},{j})")
            return

        tuile_choisie = menu_selection_tuile(possibles) #ouvre le menu de sélection parmi les tuiles compatibles
        if tuile_choisie:
            grille[i][j] = tuile_choisie #place la tuile sélectionnée dans la grille
            print(f"Tuile placée : {tuile_choisie} en ({i},{j})")
        else:
            print("Aucune tuile sélectionnée.")

    dessiner_grille()

def clic_droit(x, y):
    j = x // TAILLE_CASE  #convertit x (pixels) en indice colonne
    i = y // TAILLE_CASE  #convertit y (pixels) en indice ligne
    if 0 <= i < DIM and 0 <= j < DIM:  #vérifie que la case est bien dans la grille
        grille[i][j] = None  #supprime la tuile de cette case
        print(f"Tuile supprimée en ({i},{j})")
        dessiner_grille()  #met à jour l’affichage


def gestion_clic(tev):
    x, y = abscisse_souris(), ordonnee_souris()  #récupère les coordonnées du clic
    if tev == 'ClicGauche':
        clic_gauche(x, y)  #gère un clic gauche
    elif tev == 'ClicDroit':
        clic_droit(x, y)  #gère un clic droit

# -----------------------------
# Tâche 4: Solveur 
# -----------------------------
def get_biomes(tuile):
    return tuile[0], tuile[1], tuile[2], tuile[3] #récupère les biomes : haut, droite, bas, gauche

def biomes_compatibles(b1, b2):
    return b1 == b2 #deux biomes sont compatibles s'ils sont identiques

def est_compatible(grille, i, j, tuile):
    # Récupère les biomes de la tuile à placer (ordre : haut, droite, bas, gauche)
    haut, droite, bas, gauche = get_biomes(tuile)

    # Vérifie si on peut comparer avec la tuile au-dessus (ligne précédente)
    if i > 0 and grille[i-1][j]:# Récupère le biome du bas de la tuile voisine du dessus
        bas_voisin = get_biomes(grille[i-1][j])[2]# Récupère le biome du bas de la tuile voisine du dessus
        if not biomes_compatibles(haut, bas_voisin):# Si le biome du haut de la tuile actuelle n'est pas compatible avec le bas du voisin du dessus
            return False  # Incompatibilité détectée

    # Vérifie si on peut comparer avec la tuile en dessous (ligne suivante)
    if i < DIM - 1 and grille[i+1][j]:
        haut_voisin = get_biomes(grille[i+1][j])[0]# Récupère le biome du haut de la tuile voisine du dessous
        if not biomes_compatibles(bas, haut_voisin):# Si le biome du bas de la tuile actuelle n'est pas compatible avec le haut du voisin du dessous
            return False  # Incompatibilité détectée

    # Vérifie si on peut comparer avec la tuile à gauche (colonne précédente)
    if j > 0 and grille[i][j-1]:
        droite_voisin = get_biomes(grille[i][j-1])[1]# Récupère le biome de droite de la tuile voisine de gauche
        if not biomes_compatibles(gauche, droite_voisin):# Si le biome de gauche de la tuile actuelle n'est pas compatible avec la droite du voisin de gauche
            return False  # Incompatibilité détectée

    # Vérifie si on peut comparer avec la tuile à droite (colonne suivante)
    if j < DIM - 1 and grille[i][j+1]:
        gauche_voisin = get_biomes(grille[i][j+1])[3] # Récupère le biome de gauche de la tuile voisine de droite
        if not biomes_compatibles(droite, gauche_voisin):# Si le biome de droite de la tuile actuelle n'est pas compatible avec la gauche du voisin de droite

            return False  # Incompatibilité détectée

    
    return True # Aucune incompatibilité détectée avec les tuiles voisines : la tuile peut être placée


def trouver_case_vide(grille):
    for i in range(DIM): #parcourt toute la grille pour trouver la première case vide (None)
        for j in range(DIM):
            if grille[i][j] is None:
                return i, j  #retourne les coordonnées de la première case vide trouvée
    return None  #si aucune case vide n’est trouvée, la grille est considérée comme complète

def solveur(grille, dico_tuiles):
    case = trouver_case_vide(grille)  #cherche une case vide à remplir
    if not case:
        return True  #si aucune case vide, la grille est entièrement remplie : succès

    i, j = case  #coordonnées de la case vide à remplir
    tuiles_compatibles = [t for t in dico_tuiles if est_compatible(grille, i, j, t)] #récupère toutes les tuiles du dictionnaire qui sont compatibles avec cette position
    random.shuffle(tuiles_compatibles)  #mélange les tuiles pour varier les solutions et éviter les boucles

    for tuile in tuiles_compatibles:
        grille[i][j] = tuile  #place une tuile candidate dans la case
        dessiner_grille()     #affiche la grille après placement (utile pour visualiser l’algorithme)
        if solveur(grille, dico_tuiles):
            return True  #si la suite fonctionne, on garde la tuile (fin de récursion réussie)
        grille[i][j] = None  #sinon, on annule le placement (backtracking) et on essaie une autre tuile

    return False  #si aucune tuile ne fonctionne à cette case, on revient en arrière dans l’algorithme




# -----------------------------
# Sauvegarde et chargement
# -----------------------------

def sauvegarder_grille(nom_fichier="sauvegarde.txt"):
    with open(nom_fichier, 'w') as f: #ouvre (ou crée) le fichier spécifié en mode écriture
        for i in range(DIM):  #parcourt toutes les lignes de la grille
            ligne = []  #initialise une nouvelle ligne vide
            for j in range(DIM):  #parcourt toutes les colonnes
                tuile = grille[i][j]  #récupère la tuile à la position (i, j)
                if tuile is None:
                    ligne.append("vide")  #si la case est vide, on note "vide"
                else:
                    ligne.append(tuile)  #sinon, on ajoute le nom de la tuile
            f.write(';'.join(ligne) + '\n')  #écrit la ligne dans le fichier, séparée par des points-virgules
    print(f"Sauvegarde terminée dans {nom_fichier}.")  #message de confirmation

def charger_grille(nom_fichier="sauvegarde.txt"):
    if not os.path.exists(nom_fichier): #vérifie que le fichier existe
        print(f"Fichier {nom_fichier} introuvable.")
        return

    with open(nom_fichier, 'r') as f: #ouvre le fichier en mode lecture
        lignes = f.readlines()  #lit toutes les lignes du fichier
        for i, ligne in enumerate(lignes):  #parcourt chaque ligne du fichier
            cases = ligne.strip().split(';')  #supprime le \n et découpe selon les points-virgules
            for j, case in enumerate(cases):
                grille[i][j] = None if case == "vide" else case  #reconstruit la grille None ou nom de tuile
    print(f"Grille chargée depuis {nom_fichier}.")  #message de confirmation
    dessiner_grille()  #met à jour l’affichage de la grille à l’écran

# -----------------------------
# Boucle principale
# -----------------------------
cree_fenetre(DIM * TAILLE_CASE +600, DIM * TAILLE_CASE) #création de la fenêtre avec une largeur supplémentaire (+600) pour afficher les menus à droite
dessiner_grille() #affiche la grille initialement (vide ou déjà chargée)

while True: #boucle principale du programme
    ev = donne_ev() #récupère un événement utilisateur
    if ev is not None:
        tev = type_ev(ev) #récupère le type de l’événement (clic, touche...)
        if tev == 'Quitte':
            break #ferme le programme si l’utilisateur clique sur la croix
        if tev in ['ClicGauche', 'ClicDroit']: #gère le clic gauche (pose de tuile ou décor) ou droit (suppression)
            gestion_clic(tev)
        if tev == 'Touche':
            t = touche(ev) #récupère la touche appuyée
            if t == 's' or t=='S':
                sauvegarder_grille() #sauvegarde la grille actuelle dans un fichier
            elif t == 'l' or t=='L':
                charger_grille() #recharge une grille depuis un fichier
            elif t == 'c' or t=='C': #lance le solveur automatique de tuiles
                if solveur(grille, dico_tuiles):
                    print("Complétion réussie !")
                else:
                    print("Échec : la carte ne peut pas être complétée.")
            elif t == 'a'or t == 'A': #lance le placement automatique des décors
                decor_automatique()
                dessiner_grille()
            elif t == 'm' or t == 'M': #récupère la postion de la souris et lance le placement manuel
                x, y = abscisse_souris(), ordonnee_souris()
                clic_decor_manuel(x, y)
    mise_a_jour() #met à jour l'affichage graphique après chaque interaction