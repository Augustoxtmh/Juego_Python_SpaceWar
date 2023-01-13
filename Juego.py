import pygame, time, sqlite3 as sql, sys,random
from pygame.locals import *


def texto(txt, color, dim):
    fuente = pygame.font.SysFont('Corbel', dim)
    return fuente.render(txt, True, color)


def actualizar_bd(d):
    cursor.execute(f"insert into puntuaciones(puntos) values ({d})")
    bor = cursor.execute("select id, puntos from puntuaciones order by puntos desc limit 7, 1")
    bor = cursor.fetchall()
    for i in range(len(bor)):
        id_p = bor[i]
        cursor.execute(f"delete from puntuaciones where id = {id_p[0]}")
    conexion.commit()


def cambio_musica(musica_est):
    if musica_est == "Desact. Musica":
        n_musica_est = "Activar Musica"
        pygame.mixer.music.pause()

    else:
        n_musica_est = "Desact. Musica"
        pygame.mixer.music.unpause()

    return n_musica_est

def vidaextra(jugador):
    if 99 < (random.randint(0, 100)) and jugador.vidas != 6:
        jugador.vidas += 1
        return True


def punt_pantalla():
    x = 50
    for i in range(7):
        pantalla.blit(texto(puestos[i], (200, 200, 200), 50), (100, x))
        x += 50


def p_puntos(y, t):
        pantalla.blit(texto(t, (200, 200, 200), 40), (320, y))


def partida(dificultad):
    

    def colision(a, jugador):
        explosion = Explosion(a)
        explosiones.add(explosion)
        sonido_explosion[random.randint(1, 2) - 1].play()
        jugador.t = True


    class Explosion(pygame.sprite.Sprite):
        c = 0

        def __init__(self, c):
            super().__init__()
            self.image = pygame.image.load("imagenes/explosión1.png")
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect()
            self.rect.center = c

        def update(self):
            self.c += 1
            if self.c > 10:
                self.kill()


    class Jugador(pygame.sprite.Sprite):
        m = False
        b = 0
        t = True
        velocidad = 1
        vidas = 3

        def __init__(self):
            super().__init__()
            self.image = pygame.image.load("imagenes/jugador.png").convert()
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect()
            self.rect.center = (400, 530)

        def disparo(self):
            bala = Bala(self.rect.centerx, self.rect.top, -15)
            balas.add(bala)
            sonido_tiro.play()

        def update(self):

            teclas = pygame.key.get_pressed()
            self.b += 1
            if (teclas[K_a] or teclas[K_LEFT]) and self.rect.x > -4:
                self.rect.x -= 4 * self.velocidad

            if (teclas[K_d] or teclas[K_RIGHT]) and self.rect.x < 755:
                self.rect.x += 4 * self.velocidad

            if teclas[K_SPACE] and self.t:
                self.disparo()
                self.t = False


    class Bala(pygame.sprite.Sprite):

        def __init__(self, x, y, d):
            super().__init__()
            self.image = pygame.image.load("imagenes/Bala.png").convert()
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.bottom = y
            self.dir = d

        def update(self):
            self.rect.y += self.dir
            if self.rect.bottom < 0:
                self.kill()
                jugador.t = True


    class EnemigoBase(pygame.sprite.Sprite):
        n = 0
        b = 0
        p = 0

        def __init__(self):
            super().__init__()
            self.image = pygame.image.load('imagenes/enemigo1.png').convert()
            self.image.set_colorkey(BLANCO)
            self.radius = 10
            self.rect = self.image.get_rect()
            self.rect.center = (xn, 20)
            self.dispara = (70 - self.n * dificultad * 10 < random.randint(0, 100))
            self.cd = random.randint(250, 990)
            self.t = True

        def disparar(self):
            bala = Bala(self.rect.centerx, self.rect.top, 14 + (self.n - 1) * dificultad)  
            balasN.add(bala)
            sonido_tiro.play()

        def r_disparo(self):
            self.dispara = (70 - self.n * 10 < random.randint(0, 100))
            self.cd = random.randint(150, 900)

        def update(self):
            self.p += 1
            self.b += 1

            if self.p >= 300 / dificultad:
                self.rect.x += 10
                self.p = 0
            if self.p == 150 / dificultad:
                self.rect.x -= 10
            if self.b >= 1000 / dificultad:
                self.rect.y += 50
                self.b = 0
                self.r_disparo()
                if self.rect.y + 50 >= 500:
                    jugador.vidas = 0
                    
            if self.b >= self.cd and self.t and self.dispara:
                self.disparar()
                self.t = False


    class Enemigo2(EnemigoBase):
        def __init__(self):
            super().__init__()
            self.image = pygame.image.load('imagenes/enemigo2.png').convert()
            self.image.set_colorkey(BLANCO)
            self.radius = 10
            self.rect = self.image.get_rect()
            self.rect.center = (xn, 70)


    class Enemigo3(EnemigoBase):
        def __init__(self, y):
            super().__init__()
            self.image = pygame.image.load('imagenes/enemigo3.png').convert()
            self.image.set_colorkey(BLANCO)
            self.radius = 10
            self.rect = self.image.get_rect()
            self.rect.center = (xn, y)


    enemigos1 = pygame.sprite.Group()
    enemigos2 = pygame.sprite.Group()
    enemigos3 = pygame.sprite.Group()
    balas = pygame.sprite.Group()
    balasN = pygame.sprite.Group()
    jugadores = pygame.sprite.Group()
    explosiones = pygame.sprite.Group()
    
    jugador = Jugador()
    jugadores.add(jugador)
    vida = pygame.transform.scale(jugador.image, (25, 22))
    tiempo = time.time()

    v = False
    a = 0
    pf = 0
    puntos = 0
    xn = 50
    jugar = True

    while jugar:

        reloj.tick(60)
        tecla = pygame.key.get_pressed()
        pantalla.blit(fondo, (0, 0))

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    actualizar_bd(puntos)
                    pygame.quit()
                    sys.exit()
                if tecla[K_ESCAPE]:
                    if 0 < puntos and puntos > min_puntos[0]:
                        actualizar_bd(puntos)
                    jugar = False

        if not jugadores:
            pantalla.blit(texto("Game Over", BLANCO, 60), (100, 100))
            pantalla.blit(texto("Pulsa R para continuar", BLANCO, 40), (150, 200))
            pantalla.blit(texto("O Esc para salir", BLANCO, 35), (150, 240))
            pantalla.blit(texto(f"Puntos Finales: {pf}", BLANCO, 40), (150, 320))
            pantalla.blit(texto(f"Tiempo jugado: {int(tiempo_m - tiempo)} segundos", BLANCO, 40), (150, 360))
            if tecla[K_r]:
                partida(dificultad)
                jugar = False

        else:

            colision1 = pygame.sprite.groupcollide(enemigos1, balas, True, True, pygame.sprite.collide_circle)
            colision2 = pygame.sprite.groupcollide(enemigos2, balas, True, True, pygame.sprite.collide_circle)
            colision3 = pygame.sprite.groupcollide(enemigos3, balas, True, True, pygame.sprite.collide_circle)
            colision4 = pygame.sprite.groupcollide(jugadores, balasN, False, True, pygame.sprite.collide_circle)
            colision5 = pygame.sprite.groupcollide(balas, balasN, True, True)

            

            for i in colision1:
                colision(i.rect.center, jugador)
                puntos += int(10 * dificultad)
                if vidaextra(jugador):
                    v = True

            for i in colision2:
                colision(i.rect.center, jugador)
                puntos += int(15 * dificultad)
                if vidaextra(jugador):
                    v = True

            for i in colision3:
                colision(i.rect.center, jugador)
                puntos += int(20 * dificultad)
                if vidaextra(jugador):
                    v = True

            for i in colision4:
                jugador.vidas -= 1

            if jugador.vidas == 0:
                jugador.velocidad = 0
                pf = puntos
                jugador.kill()
                tiempo_m = time.time()

                if 0 < puntos and puntos > min_puntos[0]:
                    actualizar_bd(puntos)
                    conexion.commit()
                    puntos = 0

            if colision5:
                jugador.t = True
                puntos += 5

            if not enemigos1 and not enemigos2 and not enemigos3:
                for i in range(15):
                    enemigos1.add(EnemigoBase())
                    enemigos2.add(Enemigo2())
                    enemigos3.add(Enemigo3(120))
                    if dificultad > 1:
                        enemigos3.add(Enemigo3(170))
                    xn += 50
                xn = 50
                EnemigoBase.n += 1

            if v:
                pantalla.blit(texto("+1 Vida", BLANCO, 22), (jugador.rect.centerx - 30, jugador.rect.top - 50 - a / 2))
                a += 1
            if a >= 50:
                a = 0
                v = False

            pantalla.blit(texto(f"{puntos}", BLANCO, 42), (670, 550))
            pantalla.blit(texto(f"Nivel: {EnemigoBase.n}", BLANCO, 30), (200, 560))

            for i in range(jugador.vidas):
                pantalla.blit(vida, (8 + i * 30, 565))

            explosiones.draw(pantalla)
            jugadores.draw(pantalla)
            enemigos1.draw(pantalla)
            enemigos2.draw(pantalla)
            enemigos3.draw(pantalla)
            balas.draw(pantalla)
            balasN.draw(pantalla)
            
            explosiones.update()
            jugador.update()
            enemigos1.update()
            enemigos2.update()
            enemigos3.update()
            balas.update()
            balasN.update()
            
        pygame.display.update()


def puntuaciones():
    m = cursor.execute("select puntos from puntuaciones order by puntos desc")
    m = cursor.fetchall()

    try:
        min_puntos = m[6]
    except IndexError:
        min_puntos = [0]
    pantalla.blit(fondo, (0, 0))
    pantalla.blit(texto("Salir", (200, 200, 200), 50), (355, 520))
    y = 5

    for i in range(len(m)):
        punto = m[i]
        try:
            y += 50
            p_puntos(y, str(punto[0]))
        except (IndexError, UnboundLocalError):
            pass
    punt_pantalla()

    jugar = True
    while jugar:
        reloj.tick(30)
        mouse = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= mouse[0] <= 800 and 490 <= mouse[1] <= 600:
                    jugar = False

        tecla = pygame.key.get_pressed()

        if tecla[K_ESCAPE]:
            jugar = False
        pygame.display.update()


def dificultades():

    dificultad = 1
    jugar = True

    while jugar:
        tecla = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        reloj.tick(60)
        pantalla.blit(fondo, (0, 0))
        if dificultad == 0.75:
            pygame.draw.rect(pantalla, (0, 50, 100), pygame.Rect(20, 130, 210, 170))
        if dificultad == 1:
            pygame.draw.rect(pantalla, (0, 100, 50), pygame.Rect(280, 130, 240, 170))
        if dificultad == 1.25:
            pygame.draw.rect(pantalla, (100, 0, 50), pygame.Rect(580, 130, 200, 170))

        pantalla.blit(texto("Elija dificultad", BLANCO, 70), (205, 30))
        pantalla.blit(texto("Fácil", BLANCO, 50), (70, 140))
        pantalla.blit(texto("Menos puntos", BLANCO, 28), (30, 200))
        pantalla.blit(texto("Menos velocidad", BLANCO, 28), (30, 230))
        pantalla.blit(texto("Normal", BLANCO, 50), (305, 140))
        pantalla.blit(texto("Puntos normales", BLANCO, 28), (290, 200))
        pantalla.blit(texto("Enemigos normales", BLANCO, 28), (290, 230))
        pantalla.blit(texto("Difícil", BLANCO, 50), (610, 140))
        pantalla.blit(texto("Más puntos", BLANCO, 28), (600, 200))
        pantalla.blit(texto("Más enemigos", BLANCO, 28), (600, 230))
        pantalla.blit(texto("Más velocidad", BLANCO, 28), (600, 260))
        pantalla.blit(texto("Presione A o <- para moverte a la izquierda,", BLANCO, 28), (30, 330))
        pantalla.blit(texto("D o -> para moverte a la derecha,", BLANCO, 28), (30, 360))
        pantalla.blit(texto("y espacio para disparar, suerte.", BLANCO, 28), (30, 390))
        pantalla.blit(texto("Volver al menu", BLANCO, 45), (30, 540))
        pantalla.blit(texto("Jugar", BLANCO, 50), (660, 535))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 20 <= mouse[0] <= 230 and 130 <= mouse[1] <= 300:
                    dificultad = 0.75
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 280 <= mouse[0] <= 520 and 130 <= mouse[1] <= 300:
                    dificultad = 1
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 580 <= mouse[0] <= 780 and 130 <= mouse[1] <= 300:
                    dificultad = 1.25
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 20 <= mouse[0] <= 300 and 530 <= mouse[1] <= 590:
                    jugar = False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 650 <= mouse[0] <= 770 and 530 <= mouse[1] <= 590:
                    jugar = False
                    partida(dificultad)
            if tecla[K_ESCAPE]:
                jugar = False
        pygame.display.update()


def menu():
    b = 0
    musica_est = "Desact. Musica"

    while True:
        
        mouse = pygame.mouse.get_pos()
        reloj.tick(60)
        tecla = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 250 <= mouse[0] <= 550 and 270 <= mouse[1] <= 380:
                    b = 0
                    dificultades()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 220 <= mouse[0] <= 580 and 400 <= mouse[1] <= 480:
                    b = 0
                    puntuaciones()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 250 <= mouse[0] <= 550 and 520 <= mouse[1] <= 590:
                    pygame.quit()
                    sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 10 <= mouse[0] <= 160 and 550 <= mouse[1] <= 590:
                    musica_est = cambio_musica(musica_est)
            if tecla[K_ESCAPE] and b > 15:
                pygame.quit()
                sys.exit()


        pantalla.blit(fondo, (0, 0))
        pantalla.blit(titulo, (100, 60))
        pantalla.blit(texto("Jugar", BLANCO, 75), (315, 300))
        pantalla.blit(texto("puntuaciónes", BLANCO, 65), (240, 410))
        pantalla.blit(texto("Salir", BLANCO, 55), (350, 530))
        pantalla.blit(texto(f"{musica_est}", BLANCO, 20), (30, 560))

        b += 1
    
        pygame.display.update()


pygame.init()
pygame.display.set_caption("Space War")
conexion = sql.connect("bd.db")
cursor = conexion.cursor()

try:
    cursor.execute("create table puntuaciones(id integer primary key AUTOINCREMENT, puntos integer)")
except sql.OperationalError:
    pass
m = cursor.execute("select id, puntos from puntuaciones order by puntos desc")
m = cursor.fetchall()

try:
    min_puntos = m[6]
except IndexError:
    min_puntos = [0]

pantalla = pygame.display.set_mode((800, 600))
reloj = pygame.time.Clock()
fondo = pygame.image.load("imagenes/fondo.png").convert()
icono = pygame.image.load("imagenes/icono.png")
titulo = pygame.image.load("Imagenes/Titulo.png").convert()
BLANCO = (255, 255, 255)

icono.set_colorkey((0, 0, 0))
titulo.set_colorkey((0, 0, 0))
pygame.display.set_icon(icono)
musica = pygame.mixer.music.load("Sonidos/Intergalactic-Odyssey.ogg")
musica = pygame.mixer.music.play(-1)
puestos = ["1er Lugar:", "2do lugar:", "3er lugar:", "4to lugar:", "5to lugar:", "6to lugar:", "7mo lugar:"]

sonido_explosion = [pygame.mixer.Sound("Sonidos/001105166_prev.ogg"),
                    pygame.mixer.Sound("Sonidos/008665665_prev.ogg")]
sonido_tiro = pygame.mixer.Sound("Sonidos/scifi002.ogg")
pygame.mixer.Sound.set_volume(sonido_explosion[0], 0.6)
pygame.mixer.Sound.set_volume(sonido_explosion[1], 0.6)
pygame.mixer.Sound.set_volume(sonido_tiro, 0.5)

menu()
conexion.commit()
conexion.close()