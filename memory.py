# coding: utf-8
from tkinter import *
from PIL import Image, ImageTk
from tkinter.ttk import *
from time import gmtime, strftime
import time as Time
from datetime import date
import random
import pickle
from prettytable import PrettyTable

# Création de la fenêtre
window = Tk()
# window.attributes('-fullscreen', 1)
window.geometry("1366x768+0+0")
window.title("MEMORY")
window.wm_iconbitmap("images/memory.ico")
window.style = Style()
# ('clam', 'alt', 'default', 'classic')
window.style.theme_use("clam")
screenWidth = 1366  # window.winfo_screenwidth()  # largeur (px)
screenHeight = 768  # window.winfo_screenheight()  # Hauteur  (px)
top_frame = Frame(window)
top_frame.pack(side=TOP, fill=X)
canvas = Canvas(width=screenWidth, height=screenHeight)  # Canvas de la taille de l'écran

# Déclaration de toutes les images
IMAGES_GAME = ["Images/osx.png",
               "Images/linux.png",
               "Images/windows.png",
               "Images/python.png",
               "Images/computer.png",
               "Images/database.png",
               "Images/cloud.png",
               "Images/android.png"]
GAMES_BOARD_IMAGES = []
GAMES_BOARD_IMAGES_TK = []
IMAGES = ["Images/gameTitle.png",
          "Images/Card.png",
          "Images/quit.png",
          "Images/play.png",
          "Images/home.png",
          "Images/history.png",
          "Images/winner.png",
          "Images/pending.png",
          "Images/success.png",
          "Images/error.png"]
IMAGES_TK = []
for image in IMAGES:
    IMAGES_TK.append(ImageTk.PhotoImage(Image.open(image)))

GAME_BOARD_ID = []
returned_card = []
score = {
    'temps_total': 0,
    'nombre_de_partie': 0,
    'historique': [
    ]
}
home_button = None
start_time = 0.0
end_time = 0.0
game_time = 0.0
win_image = None
move_count_text = None
click_count_text = None
game_time_text = None
total_play_time_text = None
game_number_text = None
score_moyen_text = None
result_image = None
stat_title = None
line_stat = None
rect_stat = None
line_history = None
rect_history = None
history_title = None
history_table = None
cards_equal = False
click_count = 0
win = 0
move = 0

# Mode 4x4
GRID_LINE = 4
GRID_COLUMN = 4
x = screenWidth/2-286
y = screenHeight/2-286


# Sérialization des données
def dump_pickle(data, name):
    with open(name, 'wb') as dump_file:
        pickle.dump(data, dump_file, protocol=pickle.HIGHEST_PROTOCOL)


# Désérialization des donénes
def load_pickle(name):
    with open(name, 'rb') as data:
        return pickle.load(data)


# Calcul du score moyen pour l'affichage dans le menu Historique
def calculate_score_moyen():
    somme = 0
    for game in score['historique']:
        somme += game['score']
    return int(0 if score['nombre_de_partie'] == 0 else somme/score['nombre_de_partie'])


# Fonction à utiliser pour réinitialiser le score et l'historique des parties
def reset_score():
    return {
        'temps_total': 0,
        'nombre_de_partie': 0,
        'historique': [
        ]
    }


# Enregitrement des données avant de fermer le jeu (réinitialisation si besoin)
def quit_game():
    # score = reset_score()
    dump_pickle(score, "Data/data")
    window.destroy()


# Fonction appellé au clic sur le canvas
def clic(event):
    global returned_card, move, click_count, win, end_time, game_time, start_time, move_count_text, result_image, cards_equal
    click_x, click_y = event.x, event.y
    # structure de la variable returned_card[[index, id],[index2, id2]]

    if move < 2:
        # Récupère l'identidiant de la carte sur laquelle on vient de cliquer
        card_id = canvas.find_overlapping(click_x, click_y, click_x, click_y)
        # Si il n'y a rien sous le clique OU que c'est la première ou la deuxième carte sur laquelle j'ai déjà cliqué
        if card_id == ()\
                or (len(returned_card) == 2 and returned_card[0][0] == returned_card[1][0])\
                or (len(returned_card) == 1 and returned_card[0][1] == card_id):
            return
        move += 1
        # Je cherche l'index de cette carte dans la liste que j'ai mélangé au début
        card_id_index = GAME_BOARD_ID.index(card_id[0])
        # J'affiche (retourne) cette carte
        canvas.itemconfigure(card_id[0], image=GAMES_BOARD_IMAGES_TK[card_id_index])
        # Je l'ajoute dans les cartes retournées
        returned_card.append([card_id_index, card_id])
        click_count += 1
        if move == 2:
            # Si le nom de mes deux images sont égaux
            if GAMES_BOARD_IMAGES[returned_card[0][0]] == GAMES_BOARD_IMAGES[returned_card[1][0]]:
                cards_equal = True
                result_image = canvas.create_image(screenWidth / 2 - 16, screenHeight * 0.09, anchor=NW, image=IMAGES_TK[8], tags="result")
            else:
                result_image = canvas.create_image(screenWidth / 2 - 16, screenHeight * 0.09, anchor=NW, image=IMAGES_TK[9], tags="result")
    else:
        if cards_equal:
            canvas.delete(GAME_BOARD_ID[returned_card[0][0]])
            canvas.delete(GAME_BOARD_ID[returned_card[1][0]])
            returned_card = []
            win += 1
            cards_equal = False
        else:
            # Je retourne les cartes (affichage du ?)
            canvas.itemconfigure(GAME_BOARD_ID[returned_card[0][0]], image=IMAGES_TK[1])
            canvas.itemconfigure(GAME_BOARD_ID[returned_card[1][0]], image=IMAGES_TK[1])
            returned_card = []
        move = 0
        canvas.delete(result_image)

    canvas.itemconfigure(move_count_text, text=move)

    if win == (GRID_LINE*GRID_COLUMN)/2:
        end_time = Time.time()
        game_time = round(end_time) - round(start_time)
        end_time = 0.0
        start_time = 0.0
        winner()


# Fonction appellé au clic sur le bouton play
def play():
    global start_time, click_count, win, move, home_button, move_count_text
    GAMES_BOARD_IMAGES.clear()
    GAMES_BOARD_IMAGES_TK.clear()
    GAME_BOARD_ID.clear()

    # On remplie le plateau de jeux avec deux fois chaque images pui on le mélange
    GAMES_BOARD_IMAGES.extend(2*IMAGES_GAME)
    random.shuffle(GAMES_BOARD_IMAGES)
    # Enregistrement des identifiants des images du plateau de jeu dans une liste
    for _image in GAMES_BOARD_IMAGES:
        GAMES_BOARD_IMAGES_TK.append(ImageTk.PhotoImage(Image.open(_image)))

    play_button.destroy()
    history_button.destroy()
    click_count = 0
    win = 0
    move = 0

    # Placement des images sur le canvas
    for line in range(GRID_LINE):
        for column in range(GRID_COLUMN):
            GAME_BOARD_ID.append(canvas.create_image(150*line+x, 150*column+y, anchor=NW, image=IMAGES_TK[1], tags="cartes"))

    random.shuffle(GAME_BOARD_ID)
    move_count_text = canvas.create_text(screenWidth/2, screenHeight*0.15, text=str(move), font=('Arial','30','bold'))
    start_time = Time.time()
    home_button = Button(top_frame, image=IMAGES_TK[4], command=home)
    home_button.grid(row=0, column=2)


# Fonction appellé au clic sur le bouton de retour au menu principale (depuis l'historique ou depuis une partie)
def home():
    global history_button, play_button
    home_button.destroy()
    canvas.delete(total_play_time_text, game_number_text, score_moyen_text, stat_title, line_stat, rect_stat, line_history, rect_history, history_title, history_table)
    canvas.delete(win_image, click_count_text, game_time_text)
    canvas.delete(result_image)
    canvas.delete(move_count_text)
    play_button = Button(canvas, image=IMAGES_TK[3], command=play)
    play_button.grid(row=0, column=0, padx=screenWidth / 2 - 128, pady=screenHeight / 2 - 128)
    history_button = Button(top_frame, image=IMAGES_TK[5], command=history)
    history_button.grid(row=0, column=3)
    for i in range(len(GAME_BOARD_ID)):
        canvas.delete(GAME_BOARD_ID[i])


# Fonction pour afficher le score et temps de la partie + enregistrement dans la variable score
def winner():
    global win_image, click_count_text, game_time_text
    win_image = canvas.create_image(screenWidth/2-128, 100, image=IMAGES_TK[6], anchor=NW)
    click_count_text = canvas.create_text(screenWidth/2+20, screenHeight/2, text="Score : "+str(click_count)+" cliques", font=('Arial', '14', 'bold'))
    game_time_text = canvas.create_text(screenWidth/2+30, screenHeight/2+50, text="Temps : "+str(game_time)+" secondes", font=('Arial', '14', 'bold'))
    score['nombre_de_partie'] += 1
    score['temps_total'] += game_time
    today = date.today()
    score['historique'].append({'date': today.strftime("%d/%m/%Y"), 'score': click_count, 'temps': game_time})


# Fonction pour l'affichage de tout le menu Historique et statistique de jeu
def history():
    global home_button, total_play_time_text, game_number_text, score_moyen_text, stat_title, line_stat, rect_stat, rect_history, line_history, history_title, history_table
    total_play_time_hours = strftime('%H', gmtime(score['temps_total']))
    total_play_time_minutes = strftime('%M', gmtime(score['temps_total']))
    total_play_time_secondes = strftime('%S', gmtime(score['temps_total']))
    total_play_time = total_play_time_hours + "h" + total_play_time_minutes + "m" + total_play_time_secondes + "s"
    play_button.destroy()
    history_button.destroy()

    home_button = Button(top_frame, image=IMAGES_TK[4], command=home)
    home_button.grid(row=0, column=2)

    rect_stat = canvas.create_rectangle(screenWidth / 1.8, screenHeight / 10, screenWidth / 1.05, screenHeight / 3, width=1)
    line_stat = canvas.create_line(screenWidth / 1.8, screenHeight / 7, screenWidth / 1.05, screenHeight / 7, width=1)
    stat_title = canvas.create_text(screenWidth / 1.32, screenHeight / 8.25, text="Statistiques de jeu", font=('Arial', '18', 'bold'))
    total_play_time_text = canvas.create_text(screenWidth / 1.32, screenHeight / 5.5, text="Temps de jeu total : "+str(total_play_time), font=('Arial', '14', 'bold'))
    game_number_text = canvas.create_text(screenWidth / 1.32, screenHeight / 4.5, text="Nombre de partie : "+str(score['nombre_de_partie']), font=('Arial', '14', 'bold'))
    score_moyen_text = canvas.create_text(screenWidth / 1.32, screenHeight / 3.7, text="Score moyen : "+str(calculate_score_moyen()), font=('Arial', '14', 'bold'))
    rect_history = canvas.create_rectangle(screenWidth * 0.05, screenHeight / 10, screenWidth * 0.45, screenHeight * 0.8, width=1)
    line_history = canvas.create_line(screenWidth * 0.05, screenHeight / 7, screenWidth * 0.45, screenHeight / 7, width=1)
    history_title = canvas.create_text(screenWidth * 0.25, screenHeight / 8.25, text="Historique des parties (30 dernières)", font=('Arial', '18', 'bold'))
    pretty = PrettyTable()
    pretty.field_names = ['#', 'Date', 'Score', 'Temps']
    game_list = score['historique'][-31:-1] if score['nombre_de_partie'] > 30 else score['historique']
    for i, game in enumerate(game_list):
        temps_minute = strftime('%M', gmtime(game['temps']))
        temps_seconde = strftime('%S', gmtime(game['temps']))
        temps = temps_minute + "m" + temps_seconde + "s"
        pretty.add_row([i+1, game['date'], game['score'], temps])

    history_table = canvas.create_text(screenWidth * 0.25, screenHeight / 6, text=pretty.get_string(),
                                       font=('Courier', '14', 'bold'), anchor="n")


# Affichage des premiers éléments que l'on voit sur l'interface quand on lance le jeu
score = load_pickle("Data/data")
game_title = canvas.create_image(screenWidth/2-144, 0, image=IMAGES_TK[0], anchor=NW)
canvas.bind("<ButtonRelease-1>", clic)
exit_button = Button(top_frame, image=IMAGES_TK[2], command=quit_game)
exit_button.grid(row=0, column=0)
play_button = Button(canvas, image=IMAGES_TK[3], command=play)
play_button.grid(row=0, column=0, padx=screenWidth/2-128, pady=screenHeight/2-128)
history_button = Button(top_frame, image=IMAGES_TK[5], command=history)
history_button.grid(row=0, column=3)
canvas.pack()

window.mainloop()
