import heapq
import random
import tkinter as tk

# =========================
# Configuracao da simulacao
# =========================
LINHAS = 12
COLUNAS = 16
TAMANHO_CELULA = 45
MARGEM = 30
ATRASO_MS = 470
RAIO_REVELACAO_PARCIAL = 2

CUSTOS_POSSIVEIS = [1, 2, 3]

COR_FUNDO = "#F6F7FB"
COR_GRID = "#D4D8E8"
COR_TEXTO = "#1F2430"
COR_ROBO = "#0D47A1"
COR_INICIO = "#2E7D32"
COR_FIM = "#C62828"
COR_CAMINHO = "#F6F7FB"
COR_DESCONHECIDO = "#ECEFF4"

CORES_TERRENO = {
    1: "#C8E6C9",  # baixo custo
    2: "#FFE8A3",  # custo medio
    3: "#FFCCBC",  # alto custo
}

DIRECOES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def em_limites(posicao):
    linha, coluna = posicao
    return 0 <= linha < LINHAS and 0 <= coluna < COLUNAS


def vizinhos(posicao):
    linha, coluna = posicao
    for dl, dc in DIRECOES:
        prox = (linha + dl, coluna + dc)
        if em_limites(prox):
            yield prox


def gerar_custos_terreno():
    return {
        (linha, coluna): random.choice(CUSTOS_POSSIVEIS)
        for linha in range(LINHAS)
        for coluna in range(COLUNAS)
    }


def escolher_inicio_fim():
    todas = [(linha, coluna) for linha in range(LINHAS) for coluna in range(COLUNAS)]
    return random.sample(todas, 2)


def reconstruir_caminho(pais, inicio, fim):
    if fim not in pais:
        return None

    caminho = []
    atual = fim
    while atual is not None:
        caminho.append(atual)
        atual = pais[atual]
    caminho.reverse()

    if not caminho or caminho[0] != inicio:
        return None
    return caminho


def custo_total_caminho(custos, caminho):
    # Considera custo de ENTRADA: nao cobra a celula inicial.
    if not caminho or len(caminho) == 1:
        return 0
    return sum(custos[pos] for pos in caminho[1:])


def dijkstra_totalmente_observavel(custos, inicio, fim):
    fronteira = [(0, inicio)]
    dist = {inicio: 0}
    pais = {inicio: None}
    explorados = []

    while fronteira:
        custo_atual, atual = heapq.heappop(fronteira)
        if custo_atual != dist[atual]:
            continue

        explorados.append(atual)
        if atual == fim:
            break

        for viz in vizinhos(atual):
            novo_custo = custo_atual + custos[viz]
            if viz not in dist or novo_custo < dist[viz]:
                dist[viz] = novo_custo
                pais[viz] = atual
                heapq.heappush(fronteira, (novo_custo, viz))

    caminho = reconstruir_caminho(pais, inicio, fim)
    return caminho, dist.get(fim), set(custos.keys()), explorados


def dijkstra_parcialmente_observavel(custos_reais, inicio, fim):
    """
    Custos sao revelados apenas quando o algoritmo explora vizinhos.
    Ainda assim, encontra caminho de menor custo global.
    """
    conhecidos = {inicio: custos_reais[inicio]}

    fronteira = [(0, inicio)]
    dist = {inicio: 0}
    pais = {inicio: None}
    explorados = []

    while fronteira:
        custo_atual, atual = heapq.heappop(fronteira)
        if custo_atual != dist[atual]:
            continue

        explorados.append(atual)
        if atual == fim:
            break

        for viz in vizinhos(atual):
            if viz not in conhecidos:
                conhecidos[viz] = custos_reais[viz]

            novo_custo = custo_atual + conhecidos[viz]
            if viz not in dist or novo_custo < dist[viz]:
                dist[viz] = novo_custo
                pais[viz] = atual
                heapq.heappush(fronteira, (novo_custo, viz))

    caminho = reconstruir_caminho(pais, inicio, fim)
    return caminho, dist.get(fim), conhecidos, explorados


def calcular_plano(state):
    modo = state["modo_var"].get()

    if modo == "observavel":
        caminho, custo, conhecidos, explorados = dijkstra_totalmente_observavel(
            state["custos_reais"], state["inicio"], state["fim"]
        )
    else:
        caminho, custo, conhecidos, explorados = dijkstra_parcialmente_observavel(
            state["custos_reais"], state["inicio"], state["fim"]
        )

    state["caminho"] = caminho if caminho else [state["inicio"]]
    state["custo_total"] = custo if custo is not None else 0
    state["custos_conhecidos"] = conhecidos
    state["explorados"] = set(explorados)


def revelar_ao_redor(state, posicao):
    linha, coluna = posicao
    for dl in range(-RAIO_REVELACAO_PARCIAL, RAIO_REVELACAO_PARCIAL + 1):
        for dc in range(-RAIO_REVELACAO_PARCIAL, RAIO_REVELACAO_PARCIAL + 1):
            # Diamante de visao (distancia Manhattan) no entorno da posicao atual.
            if abs(dl) + abs(dc) <= RAIO_REVELACAO_PARCIAL:
                nova_pos = (linha + dl, coluna + dc)
                if em_limites(nova_pos):
                    state["revelados"].add(nova_pos)


def desenhar_tela(state):
    canvas = state["canvas"]
    canvas.delete("all")

    x0 = MARGEM
    y0 = MARGEM
    x1 = x0 + COLUNAS * TAMANHO_CELULA
    y1 = y0 + LINHAS * TAMANHO_CELULA

    modo_observavel = state["modo_var"].get() == "observavel"

    # Terreno: no modo parcial, so mostra pesos ja revelados.
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            pos = (linha, coluna)
            cx0 = x0 + coluna * TAMANHO_CELULA
            cy0 = y0 + linha * TAMANHO_CELULA
            cx1 = cx0 + TAMANHO_CELULA
            cy1 = cy0 + TAMANHO_CELULA

            if modo_observavel or pos in state["revelados"]:
                custo = state["custos_reais"][pos]
                cor = CORES_TERRENO[custo]
            else:
                cor = COR_DESCONHECIDO

            canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=cor, outline="")

    # Rastro real do agente (casas por onde ele passou)
    for linha, coluna in state["rastro"]:
        cx0 = x0 + coluna * TAMANHO_CELULA
        cy0 = y0 + linha * TAMANHO_CELULA
        cx1 = cx0 + TAMANHO_CELULA
        cy1 = cy0 + TAMANHO_CELULA
        canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_CAMINHO, outline="")

    # Caminho planejado: destacar apenas no modo observavel.
    if modo_observavel:
        for linha, coluna in state["caminho"][1:-1]:
            cx0 = x0 + coluna * TAMANHO_CELULA
            cy0 = y0 + linha * TAMANHO_CELULA
            cx1 = cx0 + TAMANHO_CELULA
            cy1 = cy0 + TAMANHO_CELULA
            canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=COR_CAMINHO, outline="")

    # Inicio / fim
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

    # Numeros dos custos: no modo parcial, apenas nas celulas reveladas.
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            pos = (linha, coluna)
            cx = x0 + coluna * TAMANHO_CELULA + TAMANHO_CELULA / 2
            cy = y0 + linha * TAMANHO_CELULA + TAMANHO_CELULA / 2
            if modo_observavel or pos in state["revelados"]:
                texto = str(state["custos_reais"][pos])
            else:
                texto = "?"
            canvas.create_text(cx, cy, text=texto, font=("Segoe UI", 10, "bold"), fill="#2A3140")

    # Robo
    lr, cr = state["posicao"]
    cx = x0 + cr * TAMANHO_CELULA + TAMANHO_CELULA / 2
    cy = y0 + lr * TAMANHO_CELULA + TAMANHO_CELULA / 2
    r = TAMANHO_CELULA * 0.28

    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=COR_ROBO, outline="")
    olho_r = r * 0.12
    canvas.create_oval(
        cx - r * 0.32 - olho_r,
        cy - r * 0.15 - olho_r,
        cx - r * 0.32 + olho_r,
        cy - r * 0.15 + olho_r,
        fill="white",
        outline="",
    )
    canvas.create_oval(
        cx + r * 0.32 - olho_r,
        cy - r * 0.15 - olho_r,
        cx + r * 0.32 + olho_r,
        cy - r * 0.15 + olho_r,
        fill="white",
        outline="",
    )

    nome_modo = "Completamente observavel" if state["modo_var"].get() == "observavel" else "Parcialmente observavel"
    passos_total = max(0, len(state["caminho"]) - 1)

    if state["finalizado"]:
        msg = "Objetivo concluido: destino alcancado com menor custo."
    else:
        msg = "Objetivo: minimizar o custo total ate o destino."

    state["label_info"].config(
        text=(
            f"Modo: {nome_modo}\n"
            f"Passos executados: {state['passos']}/{passos_total}\n"
            f"Custo total do caminho: {state['custo_total']}\n"
            f"Casas reveladas: {len(state['revelados'])}/{LINHAS * COLUNAS}\n"
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
    state["passos"] += 1
    state["rastro"].add(state["posicao"])

    if state["modo_var"].get() == "parcial":
        revelar_ao_redor(state, state["posicao"])

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

    state["custos_reais"] = gerar_custos_terreno()
    inicio, fim = escolher_inicio_fim()
    state["inicio"] = inicio
    state["fim"] = fim

    calcular_plano(state)

    state["posicao"] = state["inicio"]
    state["indice_caminho"] = 0
    state["passos"] = 0
    state["rastro"] = {state["inicio"]}
    state["executando"] = True
    state["finalizado"] = False
    state["btn_pause"].config(text="Pausar")

    state["revelados"] = set()
    if state["modo_var"].get() == "observavel":
        state["revelados"] = {(linha, coluna) for linha in range(LINHAS) for coluna in range(COLUNAS)}
    else:
        revelar_ao_redor(state, state["inicio"])

    desenhar_tela(state)
    loop_simulacao(state)


def alterar_modo(state):
    reiniciar(state)


def main():
    root = tk.Tk()
    root.title("Etapa 4 - Agente Baseado em Utilidade (Menor Custo)")
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

    modo_var = tk.StringVar(value="observavel")

    state = {
        "root": root,
        "canvas": canvas,
        "label_info": label_info,
        "job": None,
        "executando": True,
        "finalizado": False,
        "modo_var": modo_var,
        "custos_reais": {},
        "custos_conhecidos": {},
        "explorados": set(),
        "revelados": set(),
        "inicio": (0, 0),
        "fim": (0, 0),
        "caminho": [(0, 0)],
        "custo_total": 0,
        "posicao": (0, 0),
        "rastro": set(),
        "indice_caminho": 0,
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

    rb_obs = tk.Radiobutton(
        frame_btn,
        text="V1 Observavel",
        variable=modo_var,
        value="observavel",
        command=lambda: alterar_modo(state),
        bg=COR_FUNDO,
        activebackground=COR_FUNDO,
    )
    rb_obs.grid(row=0, column=2, padx=8)

    rb_parcial = tk.Radiobutton(
        frame_btn,
        text="V2 Parcial",
        variable=modo_var,
        value="parcial",
        command=lambda: alterar_modo(state),
        bg=COR_FUNDO,
        activebackground=COR_FUNDO,
    )
    rb_parcial.grid(row=0, column=3, padx=8)

    state["btn_pause"] = btn_pause
    state["btn_reiniciar"] = btn_reiniciar

    reiniciar(state)
    root.mainloop()


if __name__ == "__main__":
    main()
