import random
import tkinter as tk
from collections import deque

# =========================
# Configuracao da simulacao
# =========================
LINHAS = 16
COLUNAS = 20
TAMANHO_CELULA = 40
MARGEM = 30
ATRASO_MS = 230
PERCENTUAL_OBSTACULOS = 0.30
MAX_TENTATIVAS_MAPA = 150

COR_FUNDO = "#F6F7FB"
COR_GRID = "#E8D4D4"
COR_TEXTO = "#1F2430"
COR_ROBO = "#1565C0"
COR_OBSTACULO = "#616A7D"
COR_INICIO = "#2E7D32"
COR_FIM = "#C62828"
COR_PERCORRIDO = "#DCEBFA"
COR_CAMINHO = "#F9D976"

DIRECOES = {
    "cima": (-1, 0),
    "baixo": (1, 0),
    "esquerda": (0, -1),
    "direita": (0, 1),
}


def mover(posicao, direcao):
    dl, dc = DIRECOES[direcao]
    return posicao[0] + dl, posicao[1] + dc


def em_limites(posicao):
    linha, coluna = posicao
    return 0 <= linha < LINHAS and 0 <= coluna < COLUNAS


def vizinhos_validos(posicao, obstaculos):
    validos = []
    for direcao in DIRECOES:
        prox = mover(posicao, direcao)
        if em_limites(prox) and prox not in obstaculos:
            validos.append(prox)
    return validos


def gerar_obstaculos(usar_obstaculos):
    if not usar_obstaculos:
        return set()

    total = LINHAS * COLUNAS
    qtd = max(1, int(total * PERCENTUAL_OBSTACULOS))
    qtd = min(qtd, total - 2)
    todas = [(l, c) for l in range(LINHAS) for c in range(COLUNAS)]
    return set(random.sample(todas, qtd))


def escolher_inicio_fim(obstaculos):
    livres = [(l, c) for l in range(LINHAS) for c in range(COLUNAS) if (l, c) not in obstaculos]
    inicio, fim = random.sample(livres, 2)
    return inicio, fim


def buscar_caminho(inicio, fim, obstaculos):
    """
    Busca em largura (BFS) para encontrar um caminho valido
    do inicio ao fim respeitando as restricoes do ambiente.
    """
    fila = deque([inicio])
    pais = {inicio: None}

    while fila:
        atual = fila.popleft()

        if atual == fim:
            break

        for vizinho in vizinhos_validos(atual, obstaculos):
            if vizinho not in pais:
                pais[vizinho] = atual
                fila.append(vizinho)

    if fim not in pais:
        return None

    caminho = []
    atual = fim
    while atual is not None:
        caminho.append(atual)
        atual = pais[atual]
    caminho.reverse()
    return caminho


def criar_cenario_valido(usar_obstaculos):
    """
    Gera mapa, inicio e fim aleatorios para cada execucao.
    Tenta encontrar um cenario com caminho valido.
    """
    for _ in range(MAX_TENTATIVAS_MAPA):
        obstaculos = gerar_obstaculos(usar_obstaculos)
        inicio, fim = escolher_inicio_fim(obstaculos)
        caminho = buscar_caminho(inicio, fim, obstaculos)
        if caminho is not None:
            return obstaculos, inicio, fim, caminho

    # Fallback seguro: sem obstaculos, sempre existe caminho.
    obstaculos = set()
    inicio, fim = escolher_inicio_fim(obstaculos)
    caminho = buscar_caminho(inicio, fim, obstaculos)
    return obstaculos, inicio, fim, caminho


def desenhar_tela(state):
    canvas = state["canvas"]
    canvas.delete("all")

    x0 = MARGEM
    y0 = MARGEM
    x1 = x0 + COLUNAS * TAMANHO_CELULA
    y1 = y0 + LINHAS * TAMANHO_CELULA

    # Celulas do caminho planejado
    for linha, coluna in state["caminho"][1:-1]:
        cx0 = x0 + coluna * TAMANHO_CELULA
        cy0 = y0 + linha * TAMANHO_CELULA
        cx1 = cx0 + TAMANHO_CELULA
        cy1 = cy0 + TAMANHO_CELULA
        canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_CAMINHO, outline="")

    # Celulas ja percorridas
    for linha, coluna in state["percorrido"]:
        cx0 = x0 + coluna * TAMANHO_CELULA
        cy0 = y0 + linha * TAMANHO_CELULA
        cx1 = cx0 + TAMANHO_CELULA
        cy1 = cy0 + TAMANHO_CELULA
        canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_PERCORRIDO, outline="")

    # Obstaculos
    for linha, coluna in state["obstaculos"]:
        cx0 = x0 + coluna * TAMANHO_CELULA
        cy0 = y0 + linha * TAMANHO_CELULA
        cx1 = cx0 + TAMANHO_CELULA
        cy1 = cy0 + TAMANHO_CELULA
        canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_OBSTACULO, outline="")

    # Inicio e fim destacados
    li, ci = state["inicio"]
    lf, cf = state["fim"]
    canvas.create_rectangle(
        x0 + ci * TAMANHO_CELULA,
        y0 + li * TAMANHO_CELULA,
        x0 + (ci + 1) * TAMANHO_CELULA,
        y0 + (li + 1) * TAMANHO_CELULA,
        fill=COR_INICIO,
        outline="",
    )
    canvas.create_rectangle(
        x0 + cf * TAMANHO_CELULA,
        y0 + lf * TAMANHO_CELULA,
        x0 + (cf + 1) * TAMANHO_CELULA,
        y0 + (lf + 1) * TAMANHO_CELULA,
        fill=COR_FIM,
        outline="",
    )

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
    lr, cr = state["posicao"]
    cx = x0 + cr * TAMANHO_CELULA + TAMANHO_CELULA / 2
    cy = y0 + lr * TAMANHO_CELULA + TAMANHO_CELULA / 2
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

    modo = "com obstaculos" if state["usar_obstaculos_var"].get() else "sem obstaculos"
    total_passos_caminho = max(0, len(state["caminho"]) - 1)

    if state["finalizado"]:
        msg = "Objetivo concluido: caminho valido encontrado e executado."
    else:
        msg = "Objetivo: sair do inicio e alcancar o destino."

    state["label_info"].config(
        text=(
            f"Modo: {modo}\n"
            f"Obstaculos: {len(state['obstaculos'])}\n"
            f"Passos executados: {state['passos']}\n"
            f"Passos do caminho: {total_passos_caminho}\n"
            f"{msg}"
        )
    )


def loop_simulacao(state):
    if not state["executando"] or state["finalizado"]:
        state["job"] = None
        return

    if state["indice_caminho"] >= len(state["caminho"]) - 1:
        state["finalizado"] = True
        desenhar_tela(state)
        state["job"] = None
        return

    state["indice_caminho"] += 1
    state["posicao"] = state["caminho"][state["indice_caminho"]]
    state["percorrido"].add(state["posicao"])
    state["passos"] += 1

    if state["posicao"] == state["fim"]:
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
    obstaculos, inicio, fim, caminho = criar_cenario_valido(usar_obstaculos)

    state["obstaculos"] = obstaculos
    state["inicio"] = inicio
    state["fim"] = fim
    state["caminho"] = caminho

    state["posicao"] = inicio
    state["indice_caminho"] = 0
    state["percorrido"] = {inicio}
    state["passos"] = 0

    state["executando"] = True
    state["finalizado"] = False
    state["btn_pause"].config(text="Pausar")

    desenhar_tela(state)
    loop_simulacao(state)


def main():
    root = tk.Tk()
    root.title("Etapa 3 - Agente Reativo Baseado em Objetivo")
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
        "obstaculos": set(),
        "inicio": (0, 0),
        "fim": (0, 0),
        "caminho": [(0, 0)],
        "posicao": (0, 0),
        "indice_caminho": 0,
        "percorrido": set(),
        "passos": 0,
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
        text="Novo cenario",
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
