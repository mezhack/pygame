import pygame
import pgzrun
from random import randint

WIDTH = 800
HEIGHT = 600

VELOCIDADE = 4


def redimensionar(ator, altura):
    """Os PNGs originais têm ~1400px de altura — maiores que a tela inteira."""
    escala = altura / ator.height
    novo = pygame.transform.smoothscale(
        ator._orig_surf, (int(ator.width * escala), altura))
    ator._orig_surf = ator._surf = novo
    ator._update_pos()


heroi = Actor("heroi", (WIDTH // 2, HEIGHT // 2))
redimensionar(heroi, 100)

moeda = Actor("moeda", (200, 200))
redimensionar(moeda, 50)

pontos = 0


def draw():
    screen.fill((20, 20, 60))
    heroi.draw()
    moeda.draw()
    screen.draw.text(f"Pontos: {pontos}", (20, 20), fontsize=40, color="white")


def update():
    global pontos

    if keyboard.left:
        heroi.x -= VELOCIDADE
    if keyboard.right:
        heroi.x += VELOCIDADE
    if keyboard.up:
        heroi.y -= VELOCIDADE
    if keyboard.down:
        heroi.y += VELOCIDADE

    heroi.x = max(heroi.width // 2, min(WIDTH - heroi.width // 2, heroi.x))
    heroi.y = max(heroi.height // 2, min(HEIGHT - heroi.height // 2, heroi.y))

    if heroi.colliderect(moeda):
        pontos += 1
        sounds.coletar.play()
        moeda.x = randint(50, WIDTH - 50)
        moeda.y = randint(50, HEIGHT - 50)


def on_mouse_down(pos):
    heroi.pos = pos


pgzrun.go()
