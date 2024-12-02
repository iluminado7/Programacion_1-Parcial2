import pygame

class Fighter():
  '''
  La clase representa un luchador en el juego y gestiona su movimiento, 
   animaciones, acciones y colisiones. Cada instancia de esta clase corresponde a un personaje en el juego.
   '''
  def __init__(self, jugador, x, y, flip, data, sprite_sheet, animation_steps, sonido):
    self.jugador = jugador #indentificacion del jugador
    self.size = data[0] #size del sprite en pixeles
    self.image_scale = data[1] #escala a aplicar el sprite
    self.offset = data[2] #ajuste de posicion para alinear correctamente la imagen
    self.flip = flip #indica si el sprite debe esta volteado horizontalmente
    self.animation_list = self.cargar_imagenes(sprite_sheet, animation_steps)  #almacena las imagenes de la animacion
    self.action = 0 #accion actual del luchador= #0:neutral #1:correr #2:saltar #3:ataque1 #4: ataque2 #5:recibe ataque #6:muerte
    self.frame_index = 0 #frame de la accion
    self.image = self.animation_list[self.action][self.frame_index] #configura el primer frame de animacion para mostrarse en pantalla
    self.update_time = pygame.time.get_ticks() #registra el tiempo actual para sincronizar animaciones
    self.rect = pygame.Rect((x, y, 80, 180)) #define el area del luchador en la pantalla para detectar el posicionamiento
    self.vel_y = 0 #velocidad vertical (salto)
    self.running = False #el jugador esta corriendo
    self.jump = False #el jugador esta en el aire
    self.attacking = False #el jugador esta realizando un ataque
    self.attack_type = 0 #tipo de ataque 1 o 2
    self.attack_cooldown = 0 #tiempo de espera entre ataques
    self.attack_sonido = sonido #efecto de sonido
    self.hit = False #indica si se recibio un ataque
    self.health = 100 #salud del luchador
    self.alive = True #indica que el jugador esta vivo


  def cargar_imagenes(self, sprite_sheet, animation_steps):
    '''recorre cada animacion en animation_steps para obtener los frames correspondientes.
    Arg:
    sprite_sheet():
    animation_steps():
    
    Detalles:
    -Crea una lista vacía para almacenar todas las animaciones.
    -Itera sobre cada fila de la hoja de sprites, que representa una animacion
    -Crea una lista temporal para los frames de la animación actual
    -Itera sobre los frames de la animación actual, según el número de pasos especificado
    -Extrae cada frame de la hoja de sprites usando coordenadas basadas en el tamaño
    -Escala la imagen del frame según el factor de escala y la agrega a la lista temporal
    -Agrega la lista temporal de frames a la lista de animaciones
    -Devuelve la lista completa de animaciones cargadas
    '''
    lista_animaciones = []
    for y, animation in enumerate(animation_steps):
      lista_animaciones_temp = []
      for x in range(animation):
        temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
        lista_animaciones_temp.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      lista_animaciones.append(lista_animaciones_temp)
    return lista_animaciones


  def moverse(self, screen_width, screen_height, surface, target, round_over):
    '''
    Descripcion: Gestiona el movimiento, las acciones, y las colisiones de un personaje en el juego.
    Arg:
    screen_width (int): Ancho de la pantalla para limitar el movimiento.
    screen_height (int): Altura de la pantalla para evitar que el luchador se salga de los limites.
    surface (pygame.Surface): Superficie del juego donde se renderiza.
    target: Instancia del luchador oponente, para determinar interacciones como ataques.
    round_over (bool): Indica si la ronda ha terminado (desactiva movimientos/acciones).
    Detalles:
    Detecta entradas del teclado para mover al jugador y ejecutar acciones (correr, saltar, atacar).
    Aplica gravedad para simular caida libre.
    Restringe el movimiento a los limites de la pantalla.
    Controla la direccion en que el jugador esta mirando segun la posicion del oponente.
    Actualiza la posicion del jugador (rect) en la pantalla.
    '''
    VELOCIDAD = 10
    GRAVEDAD = 2
    dx = 0  #desplazamiento horizontal
    dy = 0 #desplazamiento vertical
    self.running = False
    self.attack_type = 0

    #agarra las teclas que se estan  presionando
    key = pygame.key.get_pressed()

    #solo puede moverse y atacar si no esta atacando
    if (self.attacking == False) and (self.alive == True) and (round_over == False):
      #controles del jugador 1
      if self.jugador == 1:
        #movimiento
        if key[pygame.K_a]:
          dx = -VELOCIDAD
          self.running = True
        if key[pygame.K_d]:
          dx = VELOCIDAD
          self.running = True
        #salto
        if key[pygame.K_w] and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #ataque
        if key[pygame.K_r] or key[pygame.K_t]:
          self.attack(target)
          #que tipo de ataque se utilizo (1 o 2)
          if key[pygame.K_r]:
            self.attack_type = 1
          if key[pygame.K_t]:
            self.attack_type = 2


      #controles del jugador 2
      if self.jugador == 2:
        #movimiento
        if key[pygame.K_LEFT]:
          dx = -VELOCIDAD
          self.running = True
        if key[pygame.K_RIGHT]:
          dx = VELOCIDAD
          self.running = True
        #salto
        if key[pygame.K_UP] and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #ataque
        if key[pygame.K_KP1] or key[pygame.K_KP2]:
          self.attack(target)
          #tipo de ataque que se utilizo (1 o 2)
          if key[pygame.K_KP1]:
            self.attack_type = 1
          if key[pygame.K_KP2]:
            self.attack_type = 2


    #aplicar gravedad
    self.vel_y += GRAVEDAD
    dy += self.vel_y

    #asegura que el jugador no se salga del limite de la pantalla
    if self.rect.left + dx < 0:
      dx = -self.rect.left
    if self.rect.right + dx > screen_width:
      dx = screen_width - self.rect.right
    if self.rect.bottom + dy > screen_height - 110:
      self.vel_y = 0 #restablece la velocidad vertical
      self.jump = False
      dy = screen_height - 110 - self.rect.bottom

    #asegura qeu los jugadores se enfrenten entre si
    if target.rect.centerx > self.rect.centerx:
      self.flip = False
    else:
      self.flip = True

    #reduce el coldown de ataque si esta activo
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1

    #actualiza la posicion del jugador 
    self.rect.x += dx
    self.rect.y += dy


  #actualizacion de animaciones
  def update(self):
    '''
    Descripción: Actualiza la animación y estado del luchador en función de su acción actual.
    Detalles:
    Determina la animacion en curso en funcion de las condiciones (salud, ataques, daño, etc.).
    Controla el avance de los cuadros (frames) de animacion segun el temporizador (animation_cooldown).

    Finaliza animaciones especificas (como muerte o ataque) y restablece el estado del luchador cuando es necesario.
    Actualiza la imagen del luchador con el cuadro actual de la animacion.
    '''
    if self.health <= 0:
      self.health = 0
      self.alive = False
      self.update_action(6)#6:muerte
    elif self.hit == True:
      self.update_action(5)#5:daño
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(3)#3:ataque1
      elif self.attack_type == 2:
        self.update_action(4)#4:ataque2
    elif self.jump == True:
      self.update_action(2)#2:salto
    elif self.running == True:
      self.update_action(1)#1:correr
    else:
      self.update_action(0)#0:neutro

    animation_cooldown = 50 #tiempo entre frames de la animacion
    #actualizar imagen del jugador
    self.image = self.animation_list[self.action][self.frame_index]
    #verificar si ha pasado el tiempo suficiente desde la actualizacion de animacion
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #verifica si la animacion ha concluido
    if self.frame_index >= len(self.animation_list[self.action]):
      #si el jugador es derrotado se termina la animacion
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1
      else:
        self.frame_index = 0
        #se fija si un ataque fue ejecutado
        if self.action == 3 or self.action == 4:
          self.attacking = False
          self.attack_cooldown = 20
        #se fija si recibe daño
        if self.action == 5:
          self.hit = False
          #si el jugador esta en medio de un ataque, luego el ataque es cancelado
          self.attacking = False
          self.attack_cooldown = 20


  def attack(self, target):
    '''
    Descripción: Ejecuta un ataque contra el luchador objetivo.
    Arg:
    target: Instancia del luchador objetivo, para aplicar daño y registrar colisiones.
    Detalles:
    Verifica si el ataque esta disponible (attack_cooldown).
    Calcula un area de impacto (attacking_rect) basada en la posicion del luchador.
    Si el area de impacto colisiona con el objetivo, reduce la salud del objetivo y lo marca como golpeado.
    '''
    if self.attack_cooldown == 0:
      #ejecuta un ataque
      self.attacking = True
      self.attack_sonido.play()
      #define el area del impacto del ataque
      attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
      if attacking_rect.colliderect(target.rect):
        target.health -= 10
        target.hit = True


  def update_action(self, accion_nueva):
    '''
    Descripcion: Cambia la acción del luchador y actualiza el estado de la animación.
    Arg:
    accion_nueva (int): Codigo numerico de la accion que debe realizar el luchador (ej. correr, saltar).
    Detalles:
    Cambia la accion actual del luchador si es distinta a la accion nueva.
    Reinicia el indice del cuadro de animacion (frame_index) y actualiza el tiempo de referencia para la animacion (update_time).
    '''
    #cambia la accion y su respectiva animacion
    if accion_nueva != self.action:
      self.action = accion_nueva
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def dibujar(self, surface):
    '''
    Descripcion: Renderiza al luchador en la superficie de juego
    Arg:
    surface (pygame.Surface): Superficie donde se dibuja al luchador
    Detalles:
    Aplica una animacion de volteo horizontal (flip) si el luchador esta mirando hacia el lado contrario
    Ajusta la posicion del luchador en pantalla considerando un desplazamiento (offset) y escala de imagen (image_scale).
    Renderiza la imagen transformada en la superficie.
    '''
    #Voltea la imagen si es necesario y la dibuja en la superficie
    img = pygame.transform.flip(self.image, self.flip, False)
    surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))