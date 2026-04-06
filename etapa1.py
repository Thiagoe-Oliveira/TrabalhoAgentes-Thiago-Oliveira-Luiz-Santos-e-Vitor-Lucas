import random
import tkinter as tk

# =========================
# Configuracao da simulacao
# =========================
LINHAS = 8
COLUNAS = 10
TAMANHO_CELULA = 45
MARGEM = 30
ATRASO_MS = 100

COR_FUNDO = "#F6F7FB"
COR_GRID = "#D4D8E8"
COR_ROBO = "#1E88E5"
COR_TEXTO = "#1F2430"

DIRECOES = {
    "cima": (-1, 0),
    "baixo": (1, 0),
    "esquerda": (0, -1),
    "direita": (0, 1),
}


# =========================
# Logica do agente (sem memoria)
# =========================
def perceber_ambiente(posicao):
    """Percepcao local: apenas bordas na posicao atual."""
    linha, coluna = posicao

    fronteiras = {
        "topo": linha == 0,
        "base": linha == LINHAS - 1,
        "esquerda": coluna == 0,
        "direita": coluna == COLUNAS - 1,
    }

    movimentos_possiveis = []
    if not fronteiras["topo"]:
        movimentos_possiveis.append("cima")
    if not fronteiras["base"]:
        movimentos_possiveis.append("baixo")
    if not fronteiras["esquerda"]:
        movimentos_possiveis.append("esquerda")
    if not fronteiras["direita"]:
        movimentos_possiveis.append("direita")

    return {
        "fronteiras": fronteiras,
        "movimentos_possiveis": movimentos_possiveis,
    }


def decidir_movimento(percepcao_atual):
    """Agente reativo: decide apenas com base na percepcao atual."""
    return random.choice(percepcao_atual["movimentos_possiveis"])


def mover(posicao, direcao):
    dl, dc = DIRECOES[direcao]
    return posicao[0] + dl, posicao[1] + dc


# =========================
# Funcoes da interface
# =========================
def atualizar_fronteiras(state, percepcao):
    fr = percepcao["fronteiras"]
    if fr["topo"]:
        state["fronteiras_alcancadas"].add("topo")
    if fr["base"]:
        state["fronteiras_alcancadas"].add("base")
    if fr["esquerda"]:
        state["fronteiras_alcancadas"].add("esquerda")
    if fr["direita"]:
        state["fronteiras_alcancadas"].add("direita")


def desenhar_tela(state):
    canvas = state["canvas"]
    canvas.delete("all")

    x0 = MARGEM
    y0 = MARGEM
    x1 = x0 + COLUNAS * TAMANHO_CELULA
    y1 = y0 + LINHAS * TAMANHO_CELULA

    # Grade
    for i in range(LINHAS + 1):
        y = y0 + i * TAMANHO_CELULA
        canvas.create_line(x0, y, x1, y, fill=COR_GRID)
    for j in range(COLUNAS + 1):
        x = x0 + j * TAMANHO_CELULA
        canvas.create_line(x, y0, x, y1, fill=COR_GRID)

    # Borda externa
    canvas.create_rectangle(x0, y0, x1, y1, outline="#6D7B99", width=2)

    # Robo (boneco simples)
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

    ordem = ["topo", "base", "esquerda", "direita"]
    status_txt = []
    for nome in ordem:
        marca = "OK" if nome in state["fronteiras_alcancadas"] else "pendente"
        status_txt.append(f"{nome}: {marca}")

    if state["finalizado"]:
        msg = "Objetivo concluido: as 4 fronteiras foram alcancadas!"
    else:
        msg = "Objetivo: alcancar topo, base, esquerda e direita sem memoria."

    state["label_info"].config(
        text=(
            f"Passos: {state['passos']}\n"
            f"Fronteiras: {', '.join(status_txt)}\n"
            f"{msg}"
        )
    )


def loop_simulacao(state):
    if not state["executando"] or state["finalizado"]:
        state["job"] = None
        return

    percepcao = perceber_ambiente(state["posicao"])
    direcao = decidir_movimento(percepcao)
    state["posicao"] = mover(state["posicao"], direcao)
    state["passos"] += 1

    nova_percepcao = perceber_ambiente(state["posicao"])
    atualizar_fronteiras(state, nova_percepcao)

    if len(state["fronteiras_alcancadas"]) == 4:
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

    state["posicao"] = (random.randint(0, LINHAS - 1), random.randint(0, COLUNAS - 1))
    state["passos"] = 0
    state["fronteiras_alcancadas"] = set()
    state["finalizado"] = False
    state["executando"] = True
    state["btn_pause"].config(text="Pausar")

    atualizar_fronteiras(state, perceber_ambiente(state["posicao"]))
    desenhar_tela(state)
    loop_simulacao(state)


def main():
    root = tk.Tk()
    root.title("Etapa 1 - Agente Reativo Sem Memoria")
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
        "fronteiras_alcancadas": set(),
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

    state["btn_pause"] = btn_pause
    state["btn_reiniciar"] = btn_reiniciar

    reiniciar(state)
    root.mainloop()


if __name__ == "__main__":
    main()
