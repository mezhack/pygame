import pygame
import pgzrun
import random
import math

WIDTH = 800
HEIGHT = 600
TITLE = "Hero Quest - Fuga da Masmorra"

# --- Função Utilitária para Redimensionar ---
def redimensionar(ator, altura):
    escala = altura / ator.height
    novo = pygame.transform.smoothscale(
        ator._orig_surf, (int(ator.width * escala), altura)
    )
    ator._orig_surf = ator._surf = novo
    ator._update_pos()

# --- Atores principais ---
heroi = Actor("heroi", (100, 500))
redimensionar(heroi, 70)

guarda = Actor("heroi", (400, 100))  # Sprite do guarda/inimigo
redimensionar(guarda, 80)

chave = Actor("moeda", (700, 100))    # Representando a chave/item de acesso
redimensionar(chave, 40)

porta = Actor("moeda", (700, 500))    # Representando o portão de saída
redimensionar(porta, 60)

# --- Variáveis de Estado e Mecânicas de Escapada ---
VELOCIDADE_HEROI = 3
VELOCIDADE_GUARDA_PATRULHA = 1.5
VELOCIDADE_GUARDA_PERSEGUICAO = 2.0
RAIO_DE_VISAO_QD = 180 ** 2  # Distância ao quadrado (180px)

# Rota de Patrulha do Guarda (Waypoints)
rota_patrulha = [(100, 100), (600, 100)]
indice_rota = 0

# Inventário e Fechadura
tem_chave = False
estado_jogo = "JOGANDO"  # Estados: "JOGANDO", "VITORIA", "GAMEOVER"
estado_guarda = "PATRULHA" # Estados do Guarda: "PATRULHA", "PERSEGUICAO"

def reiniciar_jogo():
    global estado_jogo, estado_guarda, indice_rota, tem_chave
    tem_chave = False
    estado_jogo = "JOGANDO"
    estado_guarda = "PATRULHA"
    indice_rota = 0
    heroi.pos = (100, 500)
    guarda.pos = (400, 100)

def atualizar_ia_guarda():
    global estado_guarda, indice_rota, estado_jogo

    # 1. Define o alvo com base no estado atual
    if estado_guarda == "PERSEGUICAO":
        alvo_x, alvo_y = heroi.x, heroi.y
    else:
        alvo_x, alvo_y = rota_patrulha[indice_rota]

    # 2. Movimentação e cálculo de direção (para a lanterna/cone)
    dx = alvo_x - guarda.x
    dy = alvo_y - guarda.y
    dist = math.hypot(dx, dy)

    vel = VELOCIDADE_GUARDA_PERSEGUICAO if estado_guarda == "PERSEGUICAO" else VELOCIDADE_GUARDA_PATRULHA

    if dist > 1:
        guarda.x += (dx / dist) * vel
        guarda.y += (dy / dist) * vel
        # Guarda o ângulo para desenhar o cone de visão na direção correta
        guarda.angulo_visao = math.atan2(dy, dx)

    # 3. Transição de Estados baseada em Distância e Ângulo (Cone de Visão)
    dist_heroi_qd = (heroi.x - guarda.x)**2 + (heroi.y - guarda.y)**2
    
    if dist_heroi_qd <= RAIO_DE_VISAO_QD:
        # Verifica se o herói está dentro do ângulo frontal de visão (cone de ~90 graus)
        angulo_para_heroi = math.atan2(heroi.y - guarda.y, heroi.x - guarda.x)
        diff_angulo = (angulo_para_heroi - getattr(guarda, 'angulo_visao', 0) + math.pi) % (2 * math.pi) - math.pi
        
        # Se estiver na frente do guarda (dentro de 45 graus para cada lado)
        if abs(diff_angulo) < math.radians(45):
            estado_guarda = "PERSEGUICAO"
    else:
        if estado_guarda == "PERSEGUICAO" and dist_heroi_qd > RAIO_DE_VISAO_QD * 1.5:
            estado_guarda = "PATRULHA"

    # 4. Troca de Waypoint na Patrulha
    if estado_guarda == "PATRULHA" and dist < 10:
        indice_rota = (indice_rota + 1) % len(rota_patrulha)

def draw():
    screen.fill((15, 20, 30))

    if estado_jogo == "JOGANDO":
        # Desenha o facho de luz cônico do guarda usando pygame.draw.polygon
        angulo = getattr(guarda, 'angulo_visao', 0)
        abertura = math.radians(45)
        raio_luz = 180
        
        p1 = guarda.pos
        p2 = (p1[0] + math.cos(angulo - abertura) * raio_luz, p1[1] + math.sin(angulo - abertura) * raio_luz)
        p3 = (p1[0] + math.cos(angulo + abertura) * raio_luz, p1[1] + math.sin(angulo + abertura) * raio_luz)
        
        cor_cone = (255, 60, 60) if estado_guarda == "PERSEGUICAO" else (100, 150, 255)
        pygame.draw.polygon(screen.surface, cor_cone, [p1, p2, p3])

        # Desenha os Elementos
        porta.draw()
        if not tem_chave:
            chave.draw()
        heroi.draw()
        guarda.draw()

        # HUD / Interface de Fuga
        status_chave = "POSSUI CHAVE" if tem_chave else "PROCURE A CHAVE!"
        cor_chave = "gold" if tem_chave else "orange"
        screen.draw.text(f"Objetivo: Escapar pela Porta | Chave: {status_chave}", topleft=(20, 20), fontsize=26, color=cor_chave, shadow=(1, 1), scolor="black")
        
        status_alerta = "ALERTA: GUARDA TE VIU!" if estado_guarda == "PERSEGUICAO" else "Status: Oculto nas Sombras"
        screen.draw.text(status_alerta, midbottom=(WIDTH // 2, HEIGHT - 15), fontsize=22, color="crimson" if estado_guarda == "PERSEGUICAO" else "lime")

    elif estado_jogo == "VITORIA":
        screen.draw.text("VOCÊ ESCAPOU COM SUCESSO!", center=(WIDTH // 2, 250), fontsize=50, color="lightgreen", shadow=(2, 2), scolor="black")
        screen.draw.text("Pressione [R] para jogar novamente", center=(WIDTH // 2, 350), fontsize=26, color="yellow")

    elif estado_jogo == "GAMEOVER":
        screen.draw.text("VOCÊ FOI CAPTURADO!", center=(WIDTH // 2, 250), fontsize=56, color="crimson", shadow=(2, 2), scolor="black")
        screen.draw.text("Pressione [R] para tentar novamente", center=(WIDTH // 2, 350), fontsize=26, color="yellow")

def update():
    global tem_chave, estado_jogo

    if estado_jogo in ["VITORIA", "GAMEOVER"]:
        if keyboard.r:
            reiniciar_jogo()
        return

    # 1. Movimentação do Herói
    if keyboard.right and heroi.right < WIDTH:
        heroi.x += VELOCIDADE_HEROI
    if keyboard.left and heroi.left > 0:
        heroi.x -= VELOCIDADE_HEROI
    if keyboard.up and heroi.top > 0:
        heroi.y -= VELOCIDADE_HEROI
    if keyboard.down and heroi.bottom < HEIGHT:
        heroi.y += VELOCIDADE_HEROI

    # 2. Processa IA de Patrulha/Detecção do Guarda
    atualizar_ia_guarda()

    # 3. Lógica de Coleta da Chave
    if not tem_chave and heroi.colliderect(chave):
        tem_chave = True

    # 4. Lógica de Interação com a Porta de Saída
    if heroi.colliderect(porta):
        if tem_chave:
            estado_jogo = "VITORIA"

    # 5. Colisão com o Guarda (Derrota)
    if heroi.colliderect(guarda):
        estado_jogo = "GAMEOVER"

pgzrun.go()