import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (TEMA CLARO / FUNDO BRANCO LIMPO)
# ==============================================================================
st.set_page_config(
    page_title="Monitor de Preços da Soja no Paraná (2007–2024)",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de cores de alto contraste para fundo branco (Apresentação)
COLORS = {
    "Soja": "#15803d",          # Verde forte
    "DERAL": "#15803d",
    "CEPEA": "#1d4ed8",         # Azul royal
    "Dolar": "#b45309",         # Âmbar escuro
    "CBOT": "#6d28d9",          # Roxo escuro
    "CBOT_BRL": "#d97706",      # Laranja/Âmbar
    "Modelo": "#ea580c",        # Laranja vivo (Figura 1)
    "Observado_Teste": "#0d9488", # Verde-azulado (Figura 1)
    "Pandemia": "#dc2626",      # Vermelho alerta
}

# Estilo Clean (Fundo Branco, Cards Claros e Tipografia Grande para Apresentação)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
    }
    .main-header {
        background: linear-gradient(135deg, #14532d, #166534);
        color: #ffffff;
        padding: 18px 26px;
        border-radius: 12px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.65rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    .main-header p {
        margin: 4px 0 0 0;
        font-size: 0.95rem;
        color: #dcfce7;
    }
    .kpi-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 16px 18px;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #15803d;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        height: 100%;
    }
    .kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        color: #475569;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #15803d;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #64748b;
        margin-top: 4px;
    }
    .exp-box {
        background-color: #f0fdf4;
        border-left: 4px solid #15803d;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        color: #1e293b;
        font-size: 0.96rem;
        margin-bottom: 16px;
    }
    .footer-box {
        text-align: center;
        font-size: 0.82rem;
        color: #64748b;
        padding: 20px 10px 10px 10px;
        border-top: 1px solid #e2e8f0;
        margin-top: 36px;
    }
    /* Deixa os botões de navegação lateral mais destacados */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    /* Oculta menu superior do GitHub, rodapé padrão e badges de criador do Streamlit, mantendo o botão da barra lateral visível */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbarActions"] {visibility: hidden !important; display: none !important;}
    [data-testid="stAppDeployButton"] {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    [data-testid="manage-app-button"] {visibility: hidden !important; display: none !important;}
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background-color: #f0fdf4 !important;
        border: 1px solid #15803d !important;
        border-radius: 8px !important;
        color: #15803d !important;
    }
    a[href*="streamlit.io/cloud"] {visibility: hidden !important; display: none !important;}
    div[class*=" profileContainer"],
    div[class*="_profileContainer_"],
    div[class*="_profilePreview_"],
    div[class*="_container_gzau3_"],
    div[class*="_viewerBadge_"],
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    .styles_viewerBadge__CvC9N,
    [class^="viewerBadge_"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# CARREGAMENTO DOS DADOS (EXCLUSIVO SOJA)
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_csv(filename: str, filter_soja: bool = False) -> pd.DataFrame:
    path = os.path.join(BASE_DIR, filename)
    df = pd.read_csv(path)
    if filter_soja and "cultura" in df.columns:
        df = df[df["cultura"] == "Soja"].copy()
    return df


@st.cache_data
def load_all_data():
    return {
        "serie_mensal": load_csv("dashboard_serie_mensal_precos_dolar.csv", filter_soja=True),
        "soja_matriz_conf": load_csv("dashboard_soja_matriz_confusao.csv"),
        "soja_mercado_mensal": load_csv("dashboard_soja_mercado_mensal.csv"),
        "soja_metricas_modelos": load_csv("dashboard_soja_metricas_modelos.csv"),
        "soja_modelo_dir_teste": load_csv("dashboard_soja_modelo_direcional_teste.csv"),
        "soja_modelo_preco_teste": load_csv("dashboard_soja_modelo_preco_teste.csv"),
    }


def fmt_brl(val, decimals=2):
    if pd.isna(val):
        return "N/D"
    return f"R$ {val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_usd(val, decimals=2):
    if pd.isna(val):
        return "N/D"
    return f"US$ {val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_num(val, decimals=2):
    if pd.isna(val):
        return "N/D"
    return f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(val, decimals=2):
    if pd.isna(val):
        return "N/D"
    return f"{val:,.{decimals}f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def render_kpi(label: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_note(html_text: str):
    st.markdown(f'<div class="exp-box">{html_text}</div>', unsafe_allow_html=True)


def apply_plotly_style(fig: go.Figure, height: int = 600) -> go.Figure:
    """Estiliza todos os gráficos com fundo branco limpo, sem sobreposição de título/legenda/eixos."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#0f172a", size=14),
        title=dict(
            font=dict(color="#0f172a", size=19, weight="bold"),
            x=0.0,
            xanchor="left",
            y=0.96,
            yanchor="top",
            pad=dict(b=15),
        ),
        height=height,
        margin=dict(t=85, l=85, r=85, b=95),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=13, color="#0f172a"),
            bgcolor="rgba(255,255,255,0.9)",
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
        linecolor="#cbd5e1",
        tickfont=dict(color="#334155", size=12),
        title_font=dict(color="#0f172a", size=14),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
        linecolor="#cbd5e1",
        tickfont=dict(color="#334155", size=12),
        title_font=dict(color="#0f172a", size=14),
        automargin=True,
    )
    if "yaxis2" in fig.layout:
        fig.layout.yaxis2.update(
            tickfont=dict(color="#334155", size=12),
            title_font=dict(color="#0f172a", size=14),
            automargin=True,
        )
    return fig


# ==============================================================================
# NAVEGAÇÃO LATERAL ESQUERDA (PÁGINAS SELECIONÁVEIS + FILTRO DE PERÍODO)
# ==============================================================================
DATA = load_all_data()
df_serie = DATA["serie_mensal"]
anos_disponiveis = sorted(df_serie["ano"].unique().tolist())
ano_min, ano_max = int(min(anos_disponiveis)), int(max(anos_disponiveis))

PAGINAS = [
    "1. Visão Geral e Evolução",
    "2. Modelagem Preditiva (2022–2024)",
]

with st.sidebar:
    st.markdown("## 🌱 Navegação")
    pagina_atual = st.radio(
        "Selecione a página da apresentação:",
        options=PAGINAS,
        index=0,
    )

    st.divider()
    st.markdown("### 📅 Filtro de Período")

    if "intervalo_anos" not in st.session_state:
        st.session_state["intervalo_anos"] = (ano_min, ano_max)

    def reset_filters():
        st.session_state["intervalo_anos"] = (ano_min, ano_max)

    intervalo_anos = st.slider(
        "Anos considerados:",
        min_value=ano_min,
        max_value=ano_max,
        step=1,
        key="intervalo_anos",
    )
    start_year, end_year = intervalo_anos

    st.button("🔄 Resetar (2007–2024)", on_click=reset_filters, width="stretch")

    st.divider()
    st.caption(
        "**IX SIEPE — UNICENTRO (2026)**\n\n"
        "Fontes: DERAL/PR · CEPEA/ESALQ · IPCA/IBGE · BCB · USDA/ERS (CBOT)"
    )


def filtrar_df(df: pd.DataFrame, col_ano="ano") -> pd.DataFrame:
    out = df.copy()
    if col_ano and col_ano in out.columns:
        out = out[(out[col_ano] >= start_year) & (out[col_ano] <= end_year)]
    elif "data" in out.columns:
        anos = pd.to_datetime(out["data"]).dt.year
        out = out[(anos >= start_year) & (anos <= end_year)]
    return out


# ==============================================================================
# CABEÇALHO PRINCIPAL
# ==============================================================================
st.markdown(
    """
    <div class="main-header">
        <h1>🌱 Monitor de Preços da Soja no Paraná (2007–2024)</h1>
        <p>Inflação (IPCA dez/2024), Câmbio (BCB) e Mercado Internacional (CBOT / USDA-ERS)</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# PÁGINA 1: VISÃO GERAL E EVOLUÇÃO (SÉRIE MENSAL REAL vs. DÓLAR E CBOT)
# ==============================================================================
if pagina_atual == "1. Visão Geral e Evolução":
    df_s_filt = filtrar_df(df_serie).sort_values("data")
    df_soja_m = filtrar_df(DATA["soja_mercado_mensal"]).sort_values("data")
    vals = df_s_filt["preco_real_dez_2024"].dropna()
    first_row = df_s_filt.iloc[0]
    last_row = df_s_filt.iloc[-1]
    media_real = vals.mean()
    min_real = vals.min()
    max_real = vals.max()
    cv_real = (vals.std(ddof=1) / media_real * 100) if len(vals) > 1 and media_real else 0.0
    var_total = ((last_row["preco_real_dez_2024"] / first_row["preco_real_dez_2024"]) - 1) * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Preço Médio Real", fmt_brl(media_real), f"Base IPCA dez/2024 ({len(df_s_filt)} meses)")
    with c2:
        render_kpi("Mínimo e Máximo Real", f"{fmt_brl(min_real)} – {fmt_brl(max_real)}", "Pico histórico em mar/2022")
    with c3:
        render_kpi("Fechamento (Dez/2024)", fmt_brl(last_row["preco_real_dez_2024"]), f"Acumulado: {fmt_pct(var_total)}")
    with c4:
        render_kpi("Volatilidade (CV)", fmt_pct(cv_real), f"Dólar Dez/2024: {fmt_brl(last_row['dolar_medio_mensal'], 2)}")

    st.write("")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_s_filt["data"],
            y=df_s_filt["preco_real_dez_2024"],
            mode="lines",
            name="Preço Real da Soja DERAL (R$/60 kg — IPCA dez/2024)",
            line=dict(color=COLORS["Soja"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_soja_m["data"],
            y=df_soja_m["cbot_brl_60kg_sem_premio"],
            mode="lines",
            name="Cotação CBOT Convertida (R$/60 kg)",
            line=dict(color=COLORS["CBOT"], width=2.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_s_filt["data"],
            y=df_s_filt["dolar_medio_mensal"],
            mode="lines",
            name="Taxa de Câmbio Média Mensal (R$/US$)",
            yaxis="y2",
            line=dict(color=COLORS["Dolar"], width=2.4, dash="dot"),
        )
    )
    fig.update_layout(
        title="Evolução Mensal do Preço da Soja (DERAL e CBOT em R$/60 kg) vs. Taxa de Câmbio (BCB)",
        xaxis_title="Data",
        yaxis=dict(title="Preço da Soja — DERAL e CBOT (R$/60 kg)"),
        yaxis2=dict(title="Taxa de Câmbio (R$/US$)", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")


# ==============================================================================
# PÁGINA 2: MODELAGEM PREDITIVA DA SOJA (TESTE 2022–2024) — LIMPA E VISUAL
# ==============================================================================
elif pagina_atual == "2. Modelagem Preditiva (2022–2024)":
    # 4 cards essenciais e diretos ao ponto para explicar em < 3 minutos
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("R² Modelo de Preço", "0,757", "Treino: 2007–2021 | Teste: 2022–2024")
    with k2:
        render_kpi("Erro do Modelo de Preço", "MAPE: 8,09%", "MAE: R$ 10,58 | RMSE: R$ 12,35 / 60 kg")
    with k3:
        render_kpi("Acurácia Direcional", "69,44%", "Ganho de +27,78 p.p. sobre o baseline (41,67%)")
    with k4:
        render_kpi("Acurácia Balanceada", "66,19%", "Especificidade: 85,71% | Sensibilidade: 46,67%")

    st.write("")
    op_mod = st.segmented_control(
        "Selecione o resultado do modelo para apresentar em tela cheia:",
        options=[
            "📈 1. Modelo de Preço — Figura 1 (Observado vs. Estimado)",
            "🎯 2. Modelo Direcional Logístico — Probabilidades Mensais (Corte 0,67)",
            "📊 3. Desempenho Direcional vs. Baseline e Matriz de Confusão",
        ],
        default="📈 1. Modelo de Preço — Figura 1 (Observado vs. Estimado)",
    )

    df_sp_teste = DATA["soja_modelo_preco_teste"].sort_values("data")
    df_sdir = DATA["soja_modelo_dir_teste"].sort_values("data")

    if op_mod == "📈 1. Modelo de Preço — Figura 1 (Observado vs. Estimado)":
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_sp_teste["data"],
                y=df_sp_teste["preco_estimado_modelo"],
                mode="lines+markers",
                name="Preço estimado pelo modelo (baseado na CBOT em R$)",
                line=dict(color=COLORS["Modelo"], width=3.5),
                marker=dict(size=9),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_sp_teste["data"],
                y=df_sp_teste["preco_deral_nominal"],
                mode="lines+markers",
                name="Preço observado DERAL",
                line=dict(color=COLORS["Observado_Teste"], width=3.5),
                marker=dict(size=9),
            )
        )
        fig.update_layout(
            title="Figura 1 — Preço Observado da Soja no DERAL vs. Preço Estimado pelo Modelo no Período de Teste (2022–2024)",
            xaxis_title="Mês/Ano (Período de Teste Independente: 2022–2024)",
            yaxis_title="Preço da soja (R$/60 kg)",
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    elif op_mod == "🎯 2. Modelo Direcional Logístico — Probabilidades Mensais (Corte 0,67)":
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_sdir["data"],
                y=df_sdir["probabilidade_alta"],
                mode="lines+markers",
                name="Probabilidade Estimada de Alta (Preditores: Var. t-1 CBOT, Dólar e DERAL)",
                line=dict(color="#334155", width=2.8),
                marker=dict(
                    size=12,
                    color=[
                        "#16a34a" if o == p else "#dc2626"
                        for o, p in zip(df_sdir["classe_observada_texto"], df_sdir["classe_prevista_texto"])
                    ],
                    line=dict(width=1.5, color="#ffffff"),
                ),
                text=[
                    f"Observado: {o} | Previsto: {p}"
                    for o, p in zip(df_sdir["classe_observada_texto"], df_sdir["classe_prevista_texto"])
                ],
            )
        )
        fig.add_hline(
            y=0.67,
            line_dash="dash",
            line_color="#d97706",
            line_width=2.5,
            annotation_text="Corte de probabilidade selecionado na validação (2019–2021) = 0,67",
            annotation_position="top left",
        )
        fig.update_layout(
            title="Probabilidade Mensal de Alta no Teste (2022–2024) — Ponto Verde = Acerto (25/36) | Ponto Vermelho = Erro (11/36)",
            xaxis_title="Data (Período de Teste: 2022–2024)",
            yaxis=dict(title="Probabilidade Estimada de Alta", range=[0.15, 0.95]),
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    else:
        col_m1, col_m2 = st.columns([1.25, 1])
        with col_m1:
            metricas_nomes = [
                "Baseline (Classe Majoritária)",
                "Acurácia do Modelo",
                "Acurácia Balanceada",
                "Especificidade (Não Alta)",
                "Sensibilidade (Alta)",
            ]
            metricas_vals = [41.67, 69.44, 66.19, 85.71, 46.67]
            cores_barras = ["#94a3b8", "#15803d", "#0d9488", "#1d4ed8", "#d97706"]

            fig_b = go.Figure()
            fig_b.add_trace(
                go.Bar(
                    x=metricas_nomes,
                    y=metricas_vals,
                    marker_color=cores_barras,
                    text=[fmt_pct(v) for v in metricas_vals],
                    textposition="outside",
                )
            )
            fig_b.update_layout(
                title="Métricas do Modelo Direcional vs. Baseline (Teste 2022–2024)",
                yaxis=dict(title="Percentual (%)", range=[0, 100]),
                xaxis_title="Métrica",
            )
            st.plotly_chart(apply_plotly_style(fig_b, height=540), width="stretch")

        with col_m2:
            df_smc = DATA["soja_matriz_conf"]
            pivot_mc = df_smc.pivot(index="observado", columns="previsto", values="quantidade").fillna(0)
            fig_mc = px.imshow(
                pivot_mc,
                text_auto=True,
                color_continuous_scale="Greens",
                labels=dict(x="Previsto pelo Modelo", y="Observado no DERAL", color="Meses"),
                title="Matriz de Confusão (2022–2024, n = 36 meses)",
            )
            fig_mc.update_traces(textfont=dict(size=20))
            fig_mc.update_layout(
                template="plotly_white",
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#0f172a", size=14),
                height=540,
                margin=dict(t=60, l=50, r=40, b=50),
            )
            st.plotly_chart(fig_mc, width="stretch")


# ==============================================================================
# RODAPÉ
# ==============================================================================
st.markdown(
    """
    <div class="footer-box">
        <strong>IX SIEPE — Semana de Integração Ensino, Pesquisa e Extensão (UNICENTRO, 2026)</strong> •
        Fontes: DERAL/SEAB-PR · CEPEA/ESALQ · IPCA/IBGE · Banco Central do Brasil (BCB) · USDA/ERS (CBOT)
    </div>
    """,
    unsafe_allow_html=True,
)
