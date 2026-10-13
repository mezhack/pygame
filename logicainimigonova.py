import pygame
import pgzrun
import random

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
VELOCIDADE_GUARDA_PERSEGUICAO = 1.5
RAIO_DE_VISAO_QD = 180 ** 2  # Distância ao quadrado (180px) para otimização

# Rota de Patrulha do Guarda (Waypoints)
rota_patrulha = [(100, 100), (600, 100)]
indice_rota = 0

# Inventário e Fechadura
tem_chave = False
estado_jogo = "JOGANDO"  # Estados: "JOGANDO", "VITORIA", "GAMEOVER"
estado_guarda = "PATRULHA" # Estados do Guarda: "PATRULHA", "PERSEGUICAO"

def reiniciar_jogo():
    global estado_jogo, estado_guarda, indice_rota
    #tem_chave,
    #tem_chave = False
    estado_jogo = "JOGANDO"
    estado_guarda = "PATRULHA"
    indice_rota = 0
    heroi.pos = (100, 500)
    guarda.pos = (400, 100)
    #chave.pos = (700, 100)

def atualizar_ia_guarda():
    global estado_guarda, indice_rota, estado_jogo

    # 1. Calculando Distância ao Quadrado até o Herói (Teoria da Aula)
    dx = heroi.x - guarda.x
    dy = heroi.y - guarda.y
    distancia_qd = dx**2 + dy**2

    # 2. Transição de Estados da FSM do Guarda
    if distancia_qd <= RAIO_DE_VISAO_QD:
        estado_guarda = "PERSEGUICAO"
    else:
        estado_guarda = "PATRULHA"

    # 3. Execução dos Comportamentos
    if estado_guarda == "PERSEGUICAO":
        # Persegue o jogador
        if guarda.x < heroi.x: guarda.x += VELOCIDADE_GUARDA_PERSEGUICAO
        elif guarda.x > heroi.x: guarda.x -= VELOCIDADE_GUARDA_PERSEGUICAO
        
        if guarda.y < heroi.y: guarda.y += VELOCIDADE_GUARDA_PERSEGUICAO
        elif guarda.y > heroi.y: guarda.y -= VELOCIDADE_GUARDA_PERSEGUICAO

    elif estado_guarda == "PATRULHA":
        # Segue a lista de Waypoints
        alvo_x, alvo_y = rota_patrulha[indice_rota]

        if guarda.x < alvo_x: guarda.x += VELOCIDADE_GUARDA_PATRULHA
        elif guarda.x > alvo_x: guarda.x -= VELOCIDADE_GUARDA_PATRULHA

        if guarda.y < alvo_y: guarda.y += VELOCIDADE_GUARDA_PATRULHA
        elif guarda.y > alvo_y: guarda.y -= VELOCIDADE_GUARDA_PATRULHA

        # Quando chega próximo do ponto atual da rota, vai para o próximo
        if abs(guarda.x - alvo_x) < 5 and abs(guarda.y - alvo_y) < 5:
            indice_rota = (indice_rota + 1) % len(rota_patrulha)

def draw():
    screen.fill((15, 20, 30))

    if estado_jogo == "JOGANDO":
        # Desenha o Raio/Cone de Visão do Guarda (Círculo Transparente/Visual)
        
        if estado_guarda == "PERSEGUICAO":
            cor_visao = (255, 50, 50) 
        else: 
            (100, 100, 255)
        screen.draw.circle(guarda.pos, 180, cor_visao)

        # Desenha os Elementos
        porta.draw()
        if not tem_chave:
            chave.draw()
        heroi.draw()
        guarda.draw()

        # HUD / Interface de Fuga
        
        if tem_chave: 
        status_chave = "POSSUI CHAVE" 
        else 
        status_chave = "PROCURE A CHAVE!"
        cor_chave = "gold" if tem_chave else "orange"
        screen.draw.text(f"Objetivo: Escapar pela Porta | Chave: {status_chave}", topleft=(20, 20), fontsize=26, color=cor_chave, shadow=(1, 1), scolor="black")
        
         
        if estado_guarda == "PERSEGUICAO":
            status_alerta = "ALERTA: GUARDA TE VIU!" 
        else 
            status_alerta = "Status: Oculto"
        
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