import pygame
import pgzrun
import random
import math

WIDTH = 800
HEIGHT = 600
TITLE = "Hero Quest - Vidas e Desafio"

# --- Função Utilitária para Redimensionar ---
def redimensionar(ator, altura):
    escala = altura / ator.height
    novo = pygame.transform.smoothscale(
        ator._orig_surf, (int(ator.width * escala), altura)
    )
    ator._orig_surf = ator._surf = novo
    ator._update_pos()


heroi = Actor("heroi", (100, 100))
redimensionar(heroi, 70)  # Reduzido ligeiramente para facilitar a navegação nos corredores

moeda = Actor("moeda", (400, 300))
redimensionar(moeda, 35)

inimigo = Actor("heroi", (650, 450))
redimensionar(inimigo, 70)

# --- Obstáculos Finos e Funcionais (Corredores Livres) ---
paredes = [
    Rect((380, 80), (20, 180)),   # Parede vertical superior (fina)
    Rect((200, 360), (220, 20)),  # Parede horizontal central (fina)
    Rect((600, 200), (20, 180))   # Parede vertical direita (fina)
]

# --- Rota de Patrulha (Waypoints) ---
waypoints = [
    (650, 450),
    (650, 120),
    (480, 120),
    (480, 450)
]
waypoint_atual = 0

# --- Configurações e Variáveis de Estado ---
PONTOS_VITORIA = 100
VIDAS_INICIAIS = 3
VELOCIDADE_HEROI = 3
VELOCIDADE_BASE_INIMIGO = 1.2

pontos = 0
vidas = 3
estado_jogo = "JOGANDO"  
moedas = []

# --- Configurações de Raycasting ---
PASSO_RAIO = 10 
RAIO_VISAO_INIMIGO = 220

def tem_linha_de_visao(origem, destino, obstaculos=[], alcance_maximo=None):
    dx = destino.x - origem.x
    dy = destino.y - origem.y
    distancia = math.hypot(dx, dy)
    
    
    if alcance_maximo is not None and distancia > alcance_maximo:
        return False

    if distancia == 0:
        return True
        
    dir_x = dx / distancia
    dir_y = dy / distancia
    
    passos = int(distancia / PASSO_RAIO)
    
    for d in range(1, passos):
        ponto_x = origem.x + dir_x * (d * PASSO_RAIO)
        ponto_y = origem.y + dir_y * (d * PASSO_RAIO)
        
        for obs in obstaculos:
            if obs.collidepoint((ponto_x, ponto_y)):
                return False
                
    return True


def reiniciar_jogo():
    global pontos, vidas, estado_jogo, waypoint_atual, moedas
    pontos = 0
    vidas = 3
    heroi.pos = (100, 100)
    moeda.pos = (400, 300)
    inimigo.pos = (650, 450)
    waypoint_atual = 0
    moedas = []
    estado_jogo = "JOGANDO"


def mover_inimigo():
    global waypoint_atual
    vel = VELOCIDADE_BASE_INIMIGO + (pontos // 20) * 0.4
    
    # Checa se enxerga o Herói via Raycasting
    vendo_heroi = tem_linha_de_visao(inimigo, heroi, paredes, RAIO_VISAO_INIMIGO)
    
    if vendo_heroi:
        alvo_x, alvo_y = heroi.x, heroi.y
        
        alvo_x = heroi.x
        alvo_y = heroi.y
    else:
        alvo_x, alvo_y = waypoints[waypoint_atual]
        dist_waypoint = math.hypot(alvo_x - inimigo.x, alvo_y - inimigo.y)
        if dist_waypoint < 10:
            waypoint_atual = (waypoint_atual + 1) % len(waypoints)
            alvo_x, alvo_y = waypoints[waypoint_atual]

    dx = alvo_x - inimigo.x
    dy = alvo_y - inimigo.y
    dist = math.hypot(dx, dy)
    
    if dist > 0:
        inimigo.x += (dx / dist) * vel
        inimigo.y += (dy / dist) * vel


def sortear_posicao_valida():
    """Sorteia uma posição sem entrar em loop infinito."""
    for _ in range(20):  # Limite seguro de tentativas
        px = random.randint(60, WIDTH - 60)
        py = random.randint(60, HEIGHT - 60)
        temp_rect = Rect((px - 15, py - 15), (30, 30))
        if not any(temp_rect.colliderect(p) for p in paredes):
            return px, py
    return 100, 500  # Posição reserva segura se falhar em todas as tentativas


def spawn_moeda():
    if estado_jogo != "JOGANDO" or len(moedas) >= 4:
        return
    
    pos_x, pos_y = sortear_posicao_valida()
    m = Actor("moeda", (pos_x, pos_y))
    redimensionar(m, 30)
    moedas.append(m)

clock.schedule_interval(spawn_moeda, 4)


def draw():
    global pontos
    screen.fill((25, 30, 45))

    if estado_jogo == "JOGANDO":
        # Desenha Paredes
        for parede in paredes:
            screen.draw.filled_rect(parede, (90, 100, 120))
            screen.draw.rect(parede, "cyan")

        # Desenha os Waypoints e Rotas de Patrulha
        for i, wp in enumerate(waypoints):
            screen.draw.filled_circle(wp, 3, "gold")
            prox_wp = waypoints[(i + 1) % len(waypoints)]
            screen.draw.line(wp, prox_wp, (50, 60, 80))

        # Raio de Alcance
        screen.draw.circle(inimigo.pos, RAIO_VISAO_INIMIGO, (255, 0, 0))
        
        # Linha de Visão Direta
        if tem_linha_de_visao(inimigo, heroi, paredes, RAIO_VISAO_INIMIGO):
            screen.draw.line(inimigo.pos, heroi.pos, "red")
            
        heroi.draw()
        moeda.draw()
        inimigo.draw()
        
        for m in moedas:
            m.draw()

        # HUD
        screen.draw.text(f"Pontos: {pontos}/{PONTOS_VITORIA}", topleft=(20, 20), fontsize=30, color="gold", shadow=(1, 1), scolor="black")
        cor_vida = "lime" if vidas > 1 else "red"
        screen.draw.text(f"Vidas: {'♥  ' * vidas}", topright=(WIDTH - 20, 20), fontsize=26, color=cor_vida, shadow=(1, 1), scolor="black")
        nivel = (pontos // 20) + 1
        screen.draw.text(f"Nível de Ameaça: {nivel}", midbottom=(WIDTH // 2, HEIGHT - 15), fontsize=20, color="lightgray")
    
    elif estado_jogo == "VITORIA":
        screen.draw.text("PARABÉNS, VOCÊ VENCEU!", center=(WIDTH // 2, 220), fontsize=50, color="lightgreen", shadow=(2, 2), scolor="black")
        screen.draw.text(f"Pontuação Final: {pontos}", center=(WIDTH // 2, 300), fontsize=30, color="white")
        screen.draw.text("Pressione [R] para Jogar Novamente", center=(WIDTH // 2, 400), fontsize=24, color="yellow")

    elif estado_jogo == "GAMEOVER":
        screen.draw.text("GAME OVER", center=(WIDTH // 2, 220), fontsize=60, color="crimson", shadow=(2, 2), scolor="black")
        screen.draw.text("Pressione [R] para Tentar Novamente", center=(WIDTH // 2, 350), fontsize=24, color="yellow")


def update():
    global pontos, vidas, estado_jogo
    
    if estado_jogo in ["VITORIA", "GAMEOVER"]:
        if keyboard.r:
            reiniciar_jogo()
        return
    
    # Salva posição para tratar colisão
    pos_ant_x, pos_ant_y = heroi.x, heroi.y

    # Movimentação do Herói
    if keyboard.right and heroi.right < WIDTH:
        heroi.x += VELOCIDADE_HEROI
    if keyboard.left and heroi.left > 0:
        heroi.x -= VELOCIDADE_HEROI
    if keyboard.up and heroi.top > 0:
        heroi.y -= VELOCIDADE_HEROI
    if keyboard.down and heroi.bottom < HEIGHT:
        heroi.y += VELOCIDADE_HEROI

    # Colisão com Paredes (Impede Atravessar)
    for p in paredes:
        if heroi.colliderect(p):
            heroi.x, heroi.y = pos_ant_x, pos_ant_y

    mover_inimigo()

    # Coleta da Moeda Principal
    if heroi.colliderect(moeda):
        pontos += 10
        px, py = sortear_posicao_valida()
        moeda.pos = (px, py)
        if pontos >= PONTOS_VITORIA:
            estado_jogo = "VITORIA"

    # Coleta das Moedas Secundárias
    for m in moedas[:]:
        if heroi.colliderect(m):
            pontos += 5
            moedas.remove(m)
            if pontos >= PONTOS_VITORIA:
                estado_jogo = "VITORIA"

    # Dano / Colisão com Inimigo
    if heroi.colliderect(inimigo):
        vidas -= 1
        if vidas <= 0:
            estado_jogo = "GAMEOVER"
        else:
            inimigo.x = random.choice([60, WIDTH - 60])
            inimigo.y = random.choice([60, HEIGHT - 60])

pgzrun.go()