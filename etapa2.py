import random
import tkinter as tk
from collections import deque

# =========================
# Configuracao da simulacao
# =========================
LINHAS = 10
COLUNAS = 14
TAMANHO_CELULA = 45
MARGEM = 30
ATRASO_MS = 50
PERCENTUAL_OBSTACULOS = 0.15

COR_FUNDO = "#F6F7FB"
COR_GRID = "#D4D8E8"
COR_ROBO = "#1565C0"
COR_TEXTO = "#1F2430"
COR_VISITADA = "#DCEBFA"
COR_OBSTACULO = "#616A7D"

DIRECOES = {
    "cima": (-1, 0),
    "baixo": (1, 0),
    "esquerda": (0, -1),
    "direita": (0, 1),
}


# =========================
# Percepcao local do ambiente
# =========================
def perceber_ambiente(posicao, obstaculos):
    linha, coluna = posicao

    fronteiras = {
        "topo": linha == 0,
        "base": linha == LINHAS - 1,
        "esquerda": coluna == 0,
        "direita": coluna == COLUNAS - 1,
    }

    movimentos_possiveis = []
    if not fronteiras["topo"] and (linha - 1, coluna) not in obstaculos:
        movimentos_possiveis.append("cima")
    if not fronteiras["base"] and (linha + 1, coluna) not in obstaculos:
        movimentos_possiveis.append("baixo")
    if not fronteiras["esquerda"] and (linha, coluna - 1) not in obstaculos:
        movimentos_possiveis.append("esquerda")
    if not fronteiras["direita"] and (linha, coluna + 1) not in obstaculos:
        movimentos_possiveis.append("direita")

    return {
        "fronteiras": fronteiras,
        "movimentos_possiveis": movimentos_possiveis,
    }


def mover(posicao, direcao):
    dl, dc = DIRECOES[direcao]
    return posicao[0] + dl, posicao[1] + dc


# =========================
# Estado interno (modelo)
# =========================
def criar_modelo_interno():
    return {
        "visitadas": set(),
        "contagem_visitas": {},
    }


def registrar_visita(modelo, posicao):
    modelo["visitadas"].add(posicao)
    modelo["contagem_visitas"][posicao] = modelo["contagem_visitas"].get(posicao, 0) + 1


def gerar_obstaculos(usar_obstaculos):
    if not usar_obstaculos:
        return set()

    total_celulas = LINHAS * COLUNAS
    qtd_obstaculos = max(1, int(total_celulas * PERCENTUAL_OBSTACULOS))
    qtd_obstaculos = min(qtd_obstaculos, total_celulas - 1)

    todas = [(l, c) for l in range(LINHAS) for c in range(COLUNAS)]
    return set(random.sample(todas, qtd_obstaculos))


def escolher_posicao_inicial(obstaculos):
    livres = [(l, c) for l in range(LINHAS) for c in range(COLUNAS) if (l, c) not in obstaculos]
    return random.choice(livres)


def calcular_celulas_alcancaveis(inicio, obstaculos):
    fila = deque([inicio])
    visitadas = {inicio}

    while fila:
        atual = fila.popleft()
        percepcao = perceber_ambiente(atual, obstaculos)

        for direcao in percepcao["movimentos_possiveis"]:
            vizinho = mover(atual, direcao)
            if vizinho not in visitadas:
                visitadas.add(vizinho)
                fila.append(vizinho)

    return visitadas


def decidir_movimento_modelo(posicao, percepcao, modelo):
    """
    Agente reativo baseado em modelo:
    1) prioriza vizinhos nao visitados;
    2) se nao houver, escolhe o vizinho menos visitado.
    """
    if not percepcao["movimentos_possiveis"]:
        return None

    candidatos = []
    for direcao in percepcao["movimentos_possiveis"]:
        destino = mover(posicao, direcao)
        candidatos.append((direcao, destino))

    nao_visitados = [item for item in candidatos if item[1] not in modelo["visitadas"]]
    if nao_visitados:
        return random.choice(nao_visitados)[0]

    menor = None
    melhores = []
    for direcao, destino in candidatos:
        visitas = modelo["contagem_visitas"].get(destino, 0)
        if menor is None or visitas < menor:
            menor = visitas
            melhores = [(direcao, destino)]
        elif visitas == menor:
            melhores.append((direcao, destino))

    return random.choice(melhores)[0]


# =========================
# Interface e simulacao
# =========================
def desenhar_tela(state):
    canvas = state["canvas"]
    canvas.delete("all")

    x0 = MARGEM
    y0 = MARGEM
    x1 = x0 + COLUNAS * TAMANHO_CELULA
    y1 = y0 + LINHAS * TAMANHO_CELULA

    # Pinta celulas visitadas com base no modelo interno
    for (linha, coluna) in state["modelo"]["visitadas"]:
        cx0 = x0 + coluna * TAMANHO_CELULA
        cy0 = y0 + linha * TAMANHO_CELULA
        cx1 = cx0 + TAMANHO_CELULA
        cy1 = cy0 + TAMANHO_CELULA
        canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_VISITADA, outline="")

    # Pinta obstaculos
    for (linha, coluna) in state["obstaculos"]:
        cx0 = x0 + coluna * TAMANHO_CELULA
        cy0 = y0 + linha * TAMANHO_CELULA
        cx1 = cx0 + TAMANHO_CELULA
        cy1 = cy0 + TAMANHO_CELULA
        canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_OBSTACULO, outline="")

    # Grade
    for i in range(LINHAS + 1):
        y = y0 + i * TAMANHO_CELULA
        canvas.create_line(x0, y, x1, y, fill=COR_GRID)
    for j in range(COLUNAS + 1):
        x = x0 + j * TAMANHO_CELULA
        canvas.create_line(x, y0, x, y1, fill=COR_GRID)

    # Borda externa
    canvas.create_rectangle(x0, y0, x1, y1, outline="#6D7B99", width=2)

    # Robo
    linha, coluna = state["posicao"]
    cx = x0 + coluna * TAMANHO_CELULA + TAMANHO_CELULA / 2
    cy = y0 + linha * TAMANHO_CELULA + TAMANHO_CELULA / 2
    r = TAMANHO_CELULA * 0.30

    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=COR_ROBO, outline="")
    olho_r = r * 0.12
    canvas.create_oval(
        cx - r * 0.35 - olho_r,
        cy - r * 0.15 - olho_r,
        cx - r * 0.35 + olho_r,
        cy - r * 0.15 + olho_r,
        fill="white",
        outline="",
    )
    canvas.create_oval(
        cx + r * 0.35 - olho_r,
        cy - r * 0.15 - olho_r,
        cx + r * 0.35 + olho_r,
        cy - r * 0.15 + olho_r,
        fill="white",
        outline="",
    )

    visitadas = len(state["modelo"]["visitadas"])
    total = state["meta_cobertura"]
    cobertura = (visitadas / total) * 100 if total else 100.0

    if state["finalizado"]:
        msg = "Objetivo concluido: maximo alcancavel visitado."
    else:
        msg = "Objetivo: maximizar cobertura com minimo de repeticao."

    modo = "com obstaculos" if state["usar_obstaculos_var"].get() else "sem obstaculos"
    livres = LINHAS * COLUNAS - len(state["obstaculos"])

    state["label_info"].config(
        text=(
            f"Passos: {state['passos']}\n"
            f"Modo: {modo}\n"
            f"Obstaculos: {len(state['obstaculos'])} | Livres: {livres}\n"
            f"Visitadas: {visitadas}/{total} ({cobertura:.1f}%)\n"
            f"{msg}"
        )
    )


def loop_simulacao(state):
    if not state["executando"] or state["finalizado"]:
        state["job"] = None
        return

    percepcao = perceber_ambiente(state["posicao"], state["obstaculos"])
    direcao = decidir_movimento_modelo(state["posicao"], percepcao, state["modelo"])

    if direcao is None:
        state["finalizado"] = True
        desenhar_tela(state)
        state["job"] = None
        return

    state["posicao"] = mover(state["posicao"], direcao)
    state["passos"] += 1

    registrar_visita(state["modelo"], state["posicao"])

    if len(state["modelo"]["visitadas"]) >= state["meta_cobertura"]:
        state["finalizado"] = True

    desenhar_tela(state)
    state["job"] = state["root"].after(ATRASO_MS, lambda: loop_simulacao(state))


def toggle_execucao(state):
    state["executando"] = not state["executando"]
    state["btn_pause"].config(text="Retomar" if not state["executando"] else "Pausar")

    if state["executando"] and state["job"] is None and not state["finalizado"]:
        loop_simulacao(state)


def reiniciar(state):
    if state["job"] is not None:
        state["root"].after_cancel(state["job"])
        state["job"] = None

    usar_obstaculos = bool(state["usar_obstaculos_var"].get())
    state["obstaculos"] = gerar_obstaculos(usar_obstaculos)
    state["posicao"] = escolher_posicao_inicial(state["obstaculos"])
    state["celulas_alcancaveis"] = calcular_celulas_alcancaveis(state["posicao"], state["obstaculos"])
    state["meta_cobertura"] = len(state["celulas_alcancaveis"])

    state["passos"] = 0
    state["finalizado"] = False
    state["executando"] = True
    state["modelo"] = criar_modelo_interno()

    registrar_visita(state["modelo"], state["posicao"])

    if state["meta_cobertura"] <= 1:
        state["finalizado"] = True

    state["btn_pause"].config(text="Pausar")
    desenhar_tela(state)

    if not state["finalizado"]:
        loop_simulacao(state)


def main():
    root = tk.Tk()
    root.title("Etapa 2 - Agente Reativo Baseado em Modelo")
    root.configure(bg=COR_FUNDO)

    largura = COLUNAS * TAMANHO_CELULA + 2 * MARGEM
    altura = LINHAS * TAMANHO_CELULA + 2 * MARGEM

    canvas = tk.Canvas(
        root,
        width=largura,
        height=altura,
        bg="white",
        highlightthickness=0,
    )
    canvas.pack(padx=15, pady=(15, 8))

    label_info = tk.Label(
        root,
        text="",
        font=("Segoe UI", 11),
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        justify="left",
    )
    label_info.pack(pady=(0, 10))

    frame_btn = tk.Frame(root, bg=COR_FUNDO)
    frame_btn.pack(pady=(0, 15))

    state = {
        "root": root,
        "canvas": canvas,
        "label_info": label_info,
        "job": None,
        "executando": True,
        "finalizado": False,
        "posicao": (0, 0),
        "passos": 0,
        "modelo": criar_modelo_interno(),
        "obstaculos": set(),
        "celulas_alcancaveis": set(),
        "meta_cobertura": 0,
    }

    btn_pause = tk.Button(
        frame_btn,
        text="Pausar",
        width=12,
        command=lambda: toggle_execucao(state),
    )
    btn_pause.grid(row=0, column=0, padx=6)

    btn_reiniciar = tk.Button(
        frame_btn,
        text="Reiniciar",
        width=12,
        command=lambda: reiniciar(state),
    )
    btn_reiniciar.grid(row=0, column=1, padx=6)

    usar_obstaculos_var = tk.BooleanVar(value=True)
    chk_obstaculos = tk.Checkbutton(
        frame_btn,
        text="Com obstaculos",
        variable=usar_obstaculos_var,
        bg=COR_FUNDO,
        activebackground=COR_FUNDO,
        command=lambda: reiniciar(state),
    )
    chk_obstaculos.grid(row=0, column=2, padx=8)

    state["btn_pause"] = btn_pause
    state["btn_reiniciar"] = btn_reiniciar
    state["usar_obstaculos_var"] = usar_obstaculos_var
    state["chk_obstaculos"] = chk_obstaculos

    reiniciar(state)
    root.mainloop()


if __name__ == "__main__":
    main()
