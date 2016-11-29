#! /usr/bin/env python -B

from gwidget import run_app
from PyQt4.QtGui import *
from PyQt4.QtCore import *

block_size = 16             # Dimensione in pixel di un blocchetto
frames_droppiece = 60       # Numero frames per caduta del pezzo
           
# Dizionario dei colori
colors = { 'r': QColor(255,128,128), 'g': QColor(128,255,128),
		   'b': QColor(128,128,255), 'c': QColor(128,255,255),
		   'm': QColor(255,128,255), 'y': QColor(255,255,128), 
		   'o': QColor(255,128,0) }

pieces = [    # Lista delle matrici delle forme dei pezzi 
		   [ ['c','c'], ['c',''], ['c',''] ],
		   [ ['','r'], ['r','r'], ['r',''] ],
		   [ ['o','o'], ['','o'], ['','o'] ],
		   [ ['g',''], ['g','g'], ['','g'] ],
		   [ ['b'], ['b'], ['b'], ['b'] ],
		   [ ['m','m'], ['m','m'] ],
		   [ ['y',''], ['y','y'], ['y',''] ] ]

board_w, board_h = 10, 22          # Dimensioni matrice di gioco
board = []                         # Matrice di gioco, inizializzata
for _ in range(board_h):           # vuota, cioe' senza pezzi
	board.append( ['']*board_w )               

piece = pieces[0]                  # Forma del pezzo corrente
piece_w = len(piece[0])            # Larghezza della forma del pezzo corrente
piece_h = len(piece)               # Altezza della forma del pezzo corrente
piece_x, piece_y = board_w/2, 0    # Posizione pezzo corrente
frame_count = 0                    # Conteggio frames per la caduta del pezzo



def hit():
    '''Ritorna True se il pezzo corrente collide'''
    if not (0 <= piece_x <= board_w-piece_w):    # Collisione bordi verticali
        return True
    if not (0 <= piece_y <= board_h-piece_h):    # Collisione bordi orizzontali
        return True
    for j in range(piece_h):    # Controlla se collide coi pezzi gia' caduti
        for i in range(piece_w):
            if board[j+piece_y][i+piece_x] and piece[j][i]:
                return True
    return False

def resolveboard():
    '''Aggiorna la matrice di gioco aggiungendo il pezzo corrente, che
    e' arrivato, ed elimina le eventuali righe piene.'''
    for j in range(piece_h):    # Aggiungi il pezzo alla matrice di gioco
        for i in range(piece_w):
            if piece[j][i]:
                board[j+piece_y][i+piece_x] = piece[j][i]        
	for j in range(board_h):    # Cerca se ci sono righe piene da eliminare
		if all(board[j]):                 # Se la riga j e' piena,
			for jj in range(j,0,-1):      # fai cadere le righe superiori
				for ii in range(board_w):
					board[jj][ii] = board[jj-1][ii]
			for ii in range(board_w):     # e vuota la prima riga
				board[0][ii] = ''

def newpiece():
    '''Crea un nuovo pezzo'''
    global piece, piece_x, piece_y, piece_w, piece_h
    from random import choice
    piece = choice(pieces)             # Scegli in modo random la forma del nuovo pezzo           
    piece_x, piece_y = board_w/2, 0    # Imposta la posizione iniziale del pezzo
    piece_w, piece_h = len(piece[0]), len(piece)
    
def start():
    '''Inizializza la matrice di gioco vuota e crea un nuovo pezzo'''
    for j in range(board_h):
        for i in range(board_w):
            board[j][i] = ''
    newpiece()

def rotater():
    '''Ruota a destra il pezzo corrente'''
    global piece, piece_w, piece_h
    newp = []                  # Crea e inizializza vuota la matrice 
    for _ in range(piece_w):   # per il pezzo ruotato
        newp.append( ['']*piece_h )
    for j in range(piece_h):      # Riempi la matrice con i valori
        for i in range(piece_w):  # della matrice ruotata
            newp[i][j] = piece[piece_h-1-j][i]
    piece_w, piece_h = piece_h, piece_w
    piece = newp

def rotatel():
    '''Ruota a sinistra il pezzo corrente'''
    global piece, piece_w, piece_h
    newp = []                  # Crea e inizializza vuota la matrice 
    for _ in range(piece_w):   # per il pezzo ruotato
        newp.append( ['']*piece_h )
    for j in range(piece_h):      # Riempi la matrice con i valori
        for i in range(piece_w):  # della matrice ruotata
            newp[i][j] = piece[j][piece_w-1-i]
    piece_w, piece_h = piece_h, piece_w
    piece = newp

def move(key):
    '''Muovi (eventualmente) il pezzo corrente con tasto key, se possibile'''
    global piece_x, piece_y
    if key == 'a':      # A sinistra
        piece_x -= 1
        if hit(): piece_x += 1
    elif key == 'd':    # A destra
        piece_x += 1
        if hit(): piece_x -= 1
    elif key == 'w':    # In alto
        piece_y -= 1
        if hit(): piece_y += 1
    elif key == 's':    # In basso
        piece_y += 1
        if hit(): piece_y -= 1
    elif key == 'q':    # Rotazione a sinistra
        rotatel()
        if hit(): rotater()
    elif key == 'e':    # Rotazione a destra
        rotater()
        if hit(): rotatel()
    elif key == ' ':    # Caduta immediata
        while not hit(): piece_y += 1
        piece_y -= 1
    elif key == 'g':    # Inizia un nuovo gioco
        start()

def update(key):
    '''Aggiorna lo stato del gioco tenendo conto dell'eventuale tasto key'''
    if key:          # Se e' stato premuto un tasto,
        move(key)    # gestisci il tasto premuto
    global piece_x, piece_y, frame_count
    frame_count += 1               # Incrementa il conteggio dei frames
    if frame_count < frames_droppiece:  # Se non e' ancora il tempo per la caduta
        return                          # del pezzo corrente, termina aggiornamento
    piece_y += 1        # Muovi il pezzo corrente di una posizione in basso
    if hit():           # Se adesso il pezzo collide (e' arrivato),
        piece_y -= 1    # riportalo indietro
        resolveboard()  # Aggiorna la matrice di gioco
        newpiece()      # Crea un nuovo pezzo
        if hit():       # Se gia' collide, game over
            start()     # e inizia un nuovo gioco
    frame_count = 0

def paint_blocks(painter, blocks, x, y, w, h):
    '''Disegna i blocchetti della matrice blocks di dimensioni w, h,
    con l'angolo in alto a sinistra nel pixel di posizione x, y'''
    for j in range(h):
        for i in range(w):
            c = blocks[j][i]
            if c:                              # Se non e' una celletta vuota,
                painter.setBrush(colors[c])    # disegnala
                painter.drawRect((i+x)*block_size, (j+y)*block_size, block_size, block_size)

def paint(painter):    # Aggiorna un frame del gioco
    update(painter.info.key)    # Aggiorna lo stato del gioco: tasto e caduta del pezzo
    painter.info.key = ''       # Evita di leggerlo ancora se il tasto e' mantenuto premuto
    painter.setBrush(QColor(128,128,128))   # Ripulisci la finestra
    painter.drawRect(0, 0, block_size*board_w, block_size*board_h)
    paint_blocks(painter, board, 0, 0, board_w, board_h)  # Disegna i pezzi gia' caduti
    if piece:                                             # Se c'e' un pezzo corrente,
        paint_blocks(painter, piece, piece_x, piece_y, piece_w, piece_h)   # disegnalo
                     

# Crea la GUI (la finestra) e chiama la funzione paint() ad ogni frame
run_app(paint, board_w*block_size, board_h*block_size)  
