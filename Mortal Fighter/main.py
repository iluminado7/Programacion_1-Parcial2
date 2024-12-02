import pygame
import pygame.mixer as mixer
from fighter import Fighter


pygame.init()
mixer.init()
#Pantalla
PANTALLA_WIDTH = 1000
PANTALLA_HEIGHT = 600
screen = pygame.display.set_mode((PANTALLA_WIDTH, PANTALLA_HEIGHT))
pygame.display.set_caption("Mortal Fighter")

#Define la velocidad a la que corre el juego
clock = pygame.time.Clock()   #para controlar la velocidad
FPS = 80   #80 cuadros por segundo

#Colores
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
BLANCO = (255, 255, 255)

#Define las variables para el desarrollo de la partida
intro_count = 4   #los segundos antes de iniciar la pelea
last_count_update = pygame.time.get_ticks()
score = [0, 0]#puntaje de los jugadores. [P1, P2]
round_over = False #bandera de la finalizacion de round
ROUND_OVER_COOLDOWN = 2000 #tiempo de espera en milisegundos

#Define las variables del guerrero
WARRIOR_SIZE = 162 #tamaño del guerrero
WARRIOR_SCALE = 4 #escala 
WARRIOR_OFFSET = [72, 47] #ajusta el sprite para alinearlo correctamente con el mago
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]  #agrupo los datos anteriores en una lista
WIZARD_SIZE = 250 #tamaño del mago
WIZARD_SCALE = 3 #escala
WIZARD_OFFSET = [112, 98] #ajusta el sprite para alinearlo correctamente con el guerrero
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET] #agrupo los datos en una lista

#Musica y sonidos
pygame.mixer.music.load("assets/audio/music2.mp3") #carga la musica de fondo
pygame.mixer.music.set_volume(0.5) #ajusta el volumen al 50%
pygame.mixer.music.play(-1, 0.0, 5000) #reproduce un bucle con desvanecimiento de 5 segundos
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav") #carga sonido de la espada
sword_fx.set_volume(0.75) 
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav") #carga sonido del hechizo 
magic_fx.set_volume(0.90)

#Carga imagen de fondo
escenario = pygame.image.load("assets/imagenes/background/bg3.jpg").convert_alpha() #carga la imagen de fondo con transparencia (convert_alpha

# Carga las spritesheets de los personajes
warrior_sheet = pygame.image.load("assets/imagenes/warrior/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/imagenes/wizard/Sprites/wizard.png").convert_alpha()

#Icono de victoria
victory_img = pygame.image.load("assets/imagenes/icons/victory.png").convert_alpha()

#define la cantidad de fotogramas para cada animacion 
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

#define las fuentes
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80) #Fuente grande para el contador.
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30) #Fuente chica para el puntaje.

#funcion para dibujar texto
def dibujar_texto(text, font, text_col, x, y):
  """    
  Args:
      text (str): El texto que se desea mostrar
      font (pygame.font.Font): Objeto de fuente que define el estilo y tamaño del texto
      text_col (tuple): Color del texto en formato RGB
      x (int): Coordenada x donde se posiciona el texto
      y (int): Coordenada y donde se posiciona el texto

  Detalles:
      - Utiliza el metodo render del objeto fuente para crear una imagen del texto
      - La imagen del texto se dibuja en la pantalla utilizando blit
      - Se puede usar para mostrar elementos como puntajes, temporizadores, y mensajes durante el juego
    """
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#funcion para dibujar el background (fondo)
def dibujar_fondo():
  """
   Detalles:
      - Utiliza la funcion "pygame.transform.scale" para ajustar la imagen de fondo 
      al tamaño de la pantalla definido por "PANTALLA_WIDTH" y "PANTALLA_HEIGHT"
      - La imagen escalada se dibuja en las coordenadas (0, 0), ocupando toda la pantalla
      - Ideal para mostrar fondos dinamicos o estaticos que mejoren la estetica del juego
  """
  escalar_bg = pygame.transform.scale(escenario, (PANTALLA_WIDTH, PANTALLA_HEIGHT))
  screen.blit(escalar_bg, (0, 0))

#dibuja la barra de vida 
def dibujar_barra_de_vida(health, x, y):
  """
    Args:
        health (int): El nivel de salud actual del jugador, en un rango de 0 a 100
        x (int): La coordenada x de la esquina superior izquierda de la barra de salud
        y (int): La coordenada y de la esquina superior izquierda de la barra de salud

    Detalles:
        - La barra de salud consta de tres componentes:
            1. Un marco blanco que rodea la barra
            2. Una barra roja que representa la salud maxima
            3. Una barra amarilla proporcional al nivel de salud actual
        - El ancho de la barra es de 400 pixeles, y la altura es de 30 pixeles
        - El "ratio" se calcula dividiendo la salud actual por 100, para determinar el porcentaje de la barra amarilla visible
    """
  ratio = health / 100
  pygame.draw.rect(screen, BLANCO, (x - 2, y - 2, 404, 34))
  pygame.draw.rect(screen, ROJO, (x, y, 400, 30))
  pygame.draw.rect(screen, AMARILLO, (x, y, 400 * ratio, 30))


#crea a los luchadores en base a la clase Fighter del modulo fighter
fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)  #guerrero
fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)  #mago

# Variable para controlar el estado del juego (True: en pantalla de los controles, False: juego principal).
pantalla_inicial = True

button_font = pygame.font.Font("assets/fonts/turok.ttf", 50)  
button_text = "CLICK PARA EMPEZAR"
button_color = (255, 0, 0)  # Rojo para resaltar
button_hover_color = (200, 0, 0)  # Color al pasar el mouse
button_rect = pygame.Rect(250, 400, 500, 60)  

def mostrar_pantalla_inicial(screen):
    screen.fill((0, 0, 0))  # Rellena la pantalla de negro

    # Tutorial de controles 
    controles_p1 = (
        "Jugador 1 Controles:",
        "Moverse Izq,Der: A D",
        "Saltar: W",
        "Ataque 1: R",
        "Ataque 2: T",
    )
    controles_p2 = (
        "Jugador 2 Controles:",
        "Moverse Izq,Der: Flechas IZQ/DER",
        "Saltar: Flecha Arriba",
        "Ataque 1: Teclado Numerico 1",
        "Ataque 2: Teclado Numerico 2",
    )

    # Renderizar controles
    y_controles_j1 = 100  # Altura inicial para controles del Jugador 1
    for text in controles_p1:
      manual_text = score_font.render(text, True, (255, 255, 255))
      screen.blit(manual_text, (50, y_controles_j1))  
      y_controles_j1 += 40  # Incrementar el desplazamiento vertical

    y_controles_j2 = 100  # Altura inicial para controles del Jugador 2
    for text in controles_p2:
      manual_text = score_font.render(text, True, (255, 255, 255))
      screen.blit(manual_text, (550, y_controles_j2))  
      y_controles_j2 += 40  # Incrementar el desplazamiento vertical
      
    # Cambia el color si el mouse esta sobre el boton
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, button_rect)
    else:
        pygame.draw.rect(screen, button_color, button_rect)

    # Renderizar texto del boton
    button_label = button_font.render(button_text, True, (255, 255, 255))
    screen.blit(button_label, (300, 400))
    return button_rect


#Bucle del juego
run = True  
while run:
  clock.tick(FPS)  
  # Pantalla del tutorial
  if pantalla_inicial:
      boton_empezar_rect = mostrar_pantalla_inicial(screen)  # Muestra la pantalla inicial.
        
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  
            if boton_empezar_rect.collidepoint(event.pos):  # Si clic en el boton.
              pantalla_inicial = False  # Cambia al estado de juego principal.
  else:
      # Pantalla de juego principal.
      dibujar_fondo()

        # Muestra las estadisticas de los jugadores.
      dibujar_barra_de_vida(fighter_1.health, 20, 20)
      dibujar_barra_de_vida(fighter_2.health, 580, 20)
      dibujar_texto("P1: " + str(score[0]), score_font, ROJO, 20, 60)
      dibujar_texto("P2: " + str(score[1]), score_font, ROJO, 580, 60)

        # Inicio del combate.
      if intro_count <= 0:  # Si finaliza el contador, el combate arranca.
          # Mover a los luchadores.
          fighter_1.moverse(PANTALLA_WIDTH, PANTALLA_HEIGHT, screen, fighter_2, round_over)
          fighter_2.moverse(PANTALLA_WIDTH, PANTALLA_HEIGHT, screen, fighter_1, round_over)
      else:
          dibujar_texto(str(intro_count), count_font, ROJO, PANTALLA_WIDTH / 2, PANTALLA_HEIGHT / 3)
          if (pygame.time.get_ticks() - last_count_update) >= 1000:
              intro_count -= 1
              last_count_update = pygame.time.get_ticks()

        # Actualiza y renderiza a los luchadores.
      fighter_1.update()
      fighter_2.update()
      fighter_1.dibujar(screen)
      fighter_2.dibujar(screen)

        # Verifica el game over y actualiza el marcador para el ganador.
      if round_over == False:
          if fighter_1.alive == False:
              score[1] += 1
              round_over = True
              round_over_time = pygame.time.get_ticks()
          elif fighter_2.alive == False:
              score[0] += 1
              round_over = True
              round_over_time = pygame.time.get_ticks()
      else:
          screen.blit(victory_img, (360, 150))
          if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
              round_over = False
              intro_count = 3
              fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
              fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

        # Detecta eventos para cerrar la ventana.
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
            run = False

    # Actualiza la pantalla.
  pygame.display.update()

#cierra pygame
pygame.quit()