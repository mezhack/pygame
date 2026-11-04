# --- SUBSTITUA a função 'atualizar_ia_guarda' atual por esta ---
def atualizar_ia_guarda():
    global estado_guarda, indice_rota, estado_jogo

    # 1. Pega a posição alvo atual (Waypoints ou Herói)
    if estado_guarda == "PERSEGUICAO":
        alvo_x, alvo_y = heroi.x, heroi.y
    else:
        alvo_x, alvo_y = rota_patrulha[indice_rota]

    # 2. Movimentação suave e cálculo de direção (para a lanterna/cone)
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


# --- SUBSTITUA a parte de desenho do guarda dentro da função 'draw()' por esta ---
    # No lugar da linha antiga do círculo, adicione:
    if estado_jogo == "JOGANDO":
        # Desenha o facho de luz cônico do guarda
        angulo = getattr(guarda, 'angulo_visao', 0)
        abertura = math.radians(45)
        raio_luz = 180
        
        p1 = guarda.pos
        p2 = (p1[0] + math.cos(angulo - abertura) * raio_luz, p1[1] + math.sin(angulo - abertura) * raio_luz)
        p3 = (p1[0] + math.cos(angulo + abertura) * raio_luz, p1[1] + math.sin(angulo + abertura) * raio_luz)
        
        cor_visao = (255, 60, 60, 100) if estado_guarda == "PERSEGUICAO" else (100, 150, 255, 100)
        screen.draw.filled_polygon([p1, p2, p3], cor_visao if len(cor_visao)==3 else (100, 150, 255))