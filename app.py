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

MESES_ORDEM = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

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
    /* Oculta barra superior do GitHub, rodapé padrão e badges de criador do Streamlit */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    [data-testid="manage-app-button"] {visibility: hidden !important; display: none !important;}
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
        "serie_anual": load_csv("dashboard_serie_anual_precos_dolar.csv", filter_soja=True),
        "volatilidade_anual": load_csv("dashboard_volatilidade_anual.csv", filter_soja=True),
        "sazonalidade": load_csv("dashboard_sazonalidade_mensal.csv", filter_soja=True),
        "ranking_meses": load_csv("dashboard_ranking_meses.csv", filter_soja=True),
        "extremos": load_csv("dashboard_extremos_precos.csv", filter_soja=True),
        "base100": load_csv("dashboard_comparativo_preco_dolar_base100.csv", filter_soja=True),
        "stl": load_csv("dashboard_decomposicao_stl.csv", filter_soja=True),
        "comp_mensal_fontes": load_csv("dashboard_comparacao_mensal_deral_cepea.csv", filter_soja=True),
        "reg_linear_hist": load_csv("dashboard_regressao_linear_historica.csv", filter_soja=True),
        "resumo_reg_linear": load_csv("dashboard_resumo_regressao_linear.csv", filter_soja=True),
        "previsoes_25_26": load_csv("dashboard_previsoes_tendencia_2025_2026.csv", filter_soja=True),
        "soja_correlacoes": load_csv("dashboard_soja_correlacoes.csv"),
        "soja_matriz_conf": load_csv("dashboard_soja_matriz_confusao.csv"),
        "soja_mercado_mensal": load_csv("dashboard_soja_mercado_mensal.csv"),
        "soja_metricas_modelos": load_csv("dashboard_soja_metricas_modelos.csv"),
        "soja_modelo_dir_teste": load_csv("dashboard_soja_modelo_direcional_teste.csv"),
        "soja_modelo_preco_teste": load_csv("dashboard_soja_modelo_preco_teste.csv"),
        "soja_resumo_anual": load_csv("dashboard_soja_resumo_anual.csv"),
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
    "2. Análise Sem Pandemia",
    "3. Sazonalidade e STL",
    "4. Câmbio e Mercado Internacional (CBOT)",
    "5. DERAL vs. CEPEA e Tendência",
    "6. Modelagem Preditiva (2022–2024)",
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
# PÁGINA 1: VISÃO GERAL E EVOLUÇÃO
# ==============================================================================
if pagina_atual == "1. Visão Geral e Evolução":
    df_s_filt = filtrar_df(df_serie).sort_values("data")
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
    vis_op = st.segmented_control(
        "Escolha a visualização principal:",
        options=[
            "📈 Série Mensal Real vs. Dólar",
            "📊 Preço Médio e Volatilidade Anual",
            "🏆 Extremos Históricos (Top 5 Picos e Vales)",
        ],
        default="📈 Série Mensal Real vs. Dólar",
    )

    if vis_op == "📊 Preço Médio e Volatilidade Anual":
        df_anual_f = filtrar_df(DATA["serie_anual"]).sort_values("ano")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_anual_f["ano"],
                y=df_anual_f["preco_maximo_anual"],
                mode="lines",
                name="Máximo Real no Ano",
                line=dict(color="#86efac", width=1.5, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_anual_f["ano"],
                y=df_anual_f["preco_minimo_anual"],
                mode="lines",
                name="Mínimo Real no Ano",
                fill="tonexty",
                fillcolor="rgba(21, 128, 61, 0.12)",
                line=dict(color="#86efac", width=1.5, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_anual_f["ano"],
                y=df_anual_f["preco_medio_anual"],
                mode="lines+markers",
                name="Preço Médio Anual (R$/60 kg)",
                line=dict(color=COLORS["Soja"], width=3.5),
                marker=dict(size=9),
            )
        )
        fig.add_trace(
            go.Bar(
                x=df_anual_f["ano"],
                y=df_anual_f["coeficiente_variacao_anual"],
                name="Volatilidade — CV Anual (%)",
                yaxis="y2",
                marker_color="rgba(180, 83, 9, 0.35)",
            )
        )
        fig.update_layout(
            title="Preço Médio Real Anual da Soja (com Banda Mín–Máx) e Coeficiente de Variação Anual (%)",
            xaxis=dict(title="Ano", dtick=1),
            yaxis=dict(title="Preço Real da Soja (R$/60 kg)"),
            yaxis2=dict(title="Coeficiente de Variação Anual (%)", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    elif vis_op == "🏆 Extremos Históricos (Top 5 Picos e Vales)":
        df_ext = DATA["extremos"].copy()
        df_ext["rotulo"] = df_ext["nome_mes"] + "/" + df_ext["ano"].astype(str)
        maiores = df_ext[df_ext["tipo_extremo"].str.contains("Maior", case=False, na=False)]
        menores = df_ext[df_ext["tipo_extremo"].str.contains("Menor", case=False, na=False)]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=maiores["rotulo"],
                y=maiores["preco_real_dez_2024"],
                name="5 Maiores Preços Reais (Picos)",
                marker_color=COLORS["Soja"],
                text=[fmt_brl(v) for v in maiores["preco_real_dez_2024"]],
                textposition="outside",
            )
        )
        fig.add_trace(
            go.Bar(
                x=menores["rotulo"],
                y=menores["preco_real_dez_2024"],
                name="5 Menores Preços Reais (Vales)",
                marker_color="#dc2626",
                text=[fmt_brl(v) for v in menores["preco_real_dez_2024"]],
                textposition="outside",
            )
        )
        fig.update_layout(
            title="Top 5 Maiores Picos e 5 Menores Vales Históricos da Soja (R$/60 kg — IPCA Dez/2024)",
            xaxis_title="Mês/Ano",
            yaxis=dict(title="Preço Real (R$/60 kg)", range=[0, 245]),
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    else:
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
                x=df_s_filt["data"],
                y=df_s_filt["dolar_medio_mensal"],
                mode="lines",
                name="Taxa de Câmbio Média Mensal (R$/US$)",
                yaxis="y2",
                line=dict(color=COLORS["Dolar"], width=2.4, dash="dot"),
            )
        )
        fig.update_layout(
            title="Evolução Mensal do Preço Real da Soja (DERAL) vs. Taxa de Câmbio (BCB)",
            xaxis_title="Data",
            yaxis=dict(title="Preço Real da Soja (R$/60 kg)"),
            yaxis2=dict(title="Taxa de Câmbio (R$/US$)", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")


# ==============================================================================
# PÁGINA 2: ANÁLISE DO PERÍODO SEM A PANDEMIA
# ==============================================================================
elif pagina_atual == "2. Análise Sem Pandemia":
    render_note(
        "<strong>Por que analisar o período sem a pandemia?</strong> Entre 2020 e 2022, choques logísticos globais, forte desvalorização cambial e demanda aquecida elevaram a soja a patamares atípicos (acima de R$ 214/saca em valores reais). "
        "Isolar esse choque permite enxergar o comportamento estrutural do mercado em condições normais."
    )

    recorte_pandemia = st.radio(
        "Selecione o recorte para isolar o efeito da pandemia:",
        options=[
            "Período Pré-Pandemia (2007–2019 — 156 meses)",
            "Série Excluindo o Choque da Pandemia (Sem 2020–2022 — 180 meses)",
        ],
        horizontal=True,
    )

    df_full = df_serie.sort_values("data").copy()
    df_cbot_full = DATA["soja_mercado_mensal"].sort_values("data").copy()

    if "Pré-Pandemia" in recorte_pandemia:
        mask_sem = df_full["ano"] <= 2019
        mask_cbot_sem = df_cbot_full["ano"] <= 2019
        titulo_recorte = "Pré-Pandemia (2007–2019)"
    else:
        mask_sem = ~df_full["ano"].isin([2020, 2021, 2022])
        mask_cbot_sem = ~df_cbot_full["ano"].isin([2020, 2021, 2022])
        titulo_recorte = "Sem os Anos de Pandemia (Excluindo 2020–2022)"

    df_sem = df_full[mask_sem].copy()
    df_pand = df_full[df_full["ano"].isin([2020, 2021, 2022])].copy()
    df_cbot_sem = df_cbot_full[mask_cbot_sem].copy()

    media_total = df_full["preco_real_dez_2024"].mean()
    media_sem = df_sem["preco_real_dez_2024"].mean()
    media_pand = df_pand["preco_real_dez_2024"].mean()
    max_sem = df_sem["preco_real_dez_2024"].max()
    cv_sem = df_sem["preco_real_dez_2024"].std(ddof=1) / media_sem * 100
    cv_total = df_full["preco_real_dez_2024"].std(ddof=1) / media_total * 100

    # Correlações sem pandemia vs com pandemia
    corr_dolar_sem = df_sem["preco_real_dez_2024"].corr(df_sem["dolar_medio_mensal"])
    corr_dolar_tot = df_full["preco_real_dez_2024"].corr(df_full["dolar_medio_mensal"])
    corr_cbot_sem = df_cbot_sem["preco_deral_nominal"].corr(df_cbot_sem["cbot_brl_60kg_sem_premio"])
    corr_cbot_tot = df_cbot_full["preco_deral_nominal"].corr(df_cbot_full["cbot_brl_60kg_sem_premio"])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi(f"Preço Médio ({titulo_recorte[:12]})", fmt_brl(media_sem), f"Série completa: {fmt_brl(media_total)}")
    with k2:
        render_kpi("Preço Médio na Pandemia (2020–22)", fmt_brl(media_pand), f"+{fmt_pct((media_pand/media_sem - 1)*100, 1)} acima do período sem pandemia")
    with k3:
        render_kpi("Volatilidade (CV Sem Pandemia)", fmt_pct(cv_sem), f"Série completa: {fmt_pct(cv_total)} (redução expressiva)")
    with k4:
        render_kpi("Correlação DERAL x CBOT (R$)", f"r = {fmt_num(corr_cbot_sem, 3)}", f"Dólar x Preço Real: r = {fmt_num(corr_dolar_sem, 3)}")

    st.write("")
    aba_p = st.segmented_control(
        "Escolha o gráfico de análise sem pandemia:",
        options=[
            "📉 Trajetória do Preço Real Sem Pandemia",
            "📊 Comparativo de Médias, Máximos e Volatilidade",
        ],
        default="📉 Trajetória do Preço Real Sem Pandemia",
    )

    if aba_p == "📊 Comparativo de Médias, Máximos e Volatilidade":
        comp_df = pd.DataFrame({
            "Período": [titulo_recorte, "Série Completa (2007–2024)", "Apenas Pandemia (2020–2022)"],
            "Preço Médio Real": [media_sem, media_total, media_pand],
            "Preço Máximo Real": [max_sem, df_full["preco_real_dez_2024"].max(), df_pand["preco_real_dez_2024"].max()],
        })
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=comp_df["Período"],
                y=comp_df["Preço Médio Real"],
                name="Preço Médio Real (R$/60 kg)",
                marker_color=COLORS["Soja"],
                text=[fmt_brl(v) for v in comp_df["Preço Médio Real"]],
                textposition="outside",
            )
        )
        fig.add_trace(
            go.Bar(
                x=comp_df["Período"],
                y=comp_df["Preço Máximo Real"],
                name="Preço Máximo Real (R$/60 kg)",
                marker_color=COLORS["CBOT_BRL"],
                text=[fmt_brl(v) for v in comp_df["Preço Máximo Real"]],
                textposition="outside",
            )
        )
        fig.update_layout(
            barmode="group",
            title="Comparação de Patamar de Preço Real: Sem Pandemia vs. Série Completa vs. Auge da Pandemia",
            yaxis=dict(title="R$/60 kg (IPCA Dez/2024)", range=[0, 245]),
            xaxis_title="Recorte Analítico",
        )
        st.plotly_chart(apply_plotly_style(fig, height=560), width="stretch")

    else:
        fig = go.Figure()
        if "Pré-Pandemia" in recorte_pandemia:
            fig.add_trace(
                go.Scatter(
                    x=df_sem["data"],
                    y=df_sem["preco_real_dez_2024"],
                    mode="lines",
                    name="Preço Real da Soja — Pré-Pandemia (2007–2019)",
                    line=dict(color=COLORS["Soja"], width=3.2),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_sem["data"],
                    y=df_sem["dolar_medio_mensal"],
                    mode="lines",
                    name="Dólar Médio Mensal (R$/US$)",
                    yaxis="y2",
                    line=dict(color=COLORS["Dolar"], width=2.2, dash="dot"),
                )
            )
            fig.add_hline(
                y=media_sem,
                line_dash="dash",
                line_color=COLORS["Soja"],
                annotation_text=f"Média Pré-Pandemia: {fmt_brl(media_sem)}",
                annotation_position="top left",
            )
        else:
            pre = df_full[df_full["ano"] <= 2019]
            pos = df_full[df_full["ano"] >= 2023]
            fig.add_trace(
                go.Scatter(
                    x=df_full["data"],
                    y=df_full["preco_real_dez_2024"],
                    mode="lines",
                    name="Choque Pandemia (2020–2022 — Excluído do cálculo)",
                    line=dict(color="#cbd5e1", width=2, dash="dot"),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=pre["data"],
                    y=pre["preco_real_dez_2024"],
                    mode="lines",
                    name="Soja Real — Pré-Pandemia (2007–2019)",
                    line=dict(color=COLORS["Soja"], width=3.2),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=pos["data"],
                    y=pos["preco_real_dez_2024"],
                    mode="lines",
                    name="Soja Real — Pós-Pandemia (2023–2024)",
                    line=dict(color=COLORS["CEPEA"], width=3.2),
                )
            )
            fig.add_vrect(
                x0="2020-01-01",
                x1="2022-12-01",
                fillcolor="rgba(220, 38, 38, 0.08)",
                line_width=0,
                annotation_text="Choque Pandemia (2020–2022)",
                annotation_position="top left",
            )
            fig.add_hline(
                y=media_sem,
                line_dash="dash",
                line_color=COLORS["Soja"],
                annotation_text=f"Média Sem Pandemia: {fmt_brl(media_sem)}",
                annotation_position="bottom right",
            )

        fig.update_layout(
            title=f"Comportamento do Preço Real da Soja — {titulo_recorte}",
            xaxis_title="Data",
            yaxis=dict(title="Preço Real da Soja (R$/60 kg — IPCA Dez/2024)"),
            yaxis2=dict(title="Dólar (R$/US$)", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(apply_plotly_style(fig, height=560), width="stretch")


# ==============================================================================
# PÁGINA 3: SAZONALIDADE E DECOMPOSIÇÃO STL
# ==============================================================================
elif pagina_atual == "3. Sazonalidade e STL":
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi("Meses de Alta Sazonal", "Outubro e Novembro", "Entressafra (Índices: 103,2 e 104,0)")
    with c2:
        render_kpi("Meses de Pressão de Safra", "Fevereiro a Maio", "Entrada da colheita (Índices < 99,5)")
    with c3:
        render_kpi("Método de Decomposição", "STL (Loess)", "Separa Tendência, Sazonalidade e Resíduo")

    st.write("")
    op_stl = st.segmented_control(
        "Selecione o gráfico:",
        options=[
            "📅 Curva de Índice Sazonal Mensal (100 = Média)",
            "🔍 Decomposição STL (Tendência, Sazonalidade e Resíduo)",
        ],
        default="📅 Curva de Índice Sazonal Mensal (100 = Média)",
    )

    if op_stl == "📅 Curva de Índice Sazonal Mensal (100 = Média)":
        df_saz = DATA["sazonalidade"].sort_values("mes")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_saz["nome_mes"],
                y=df_saz["indice_sazonal"],
                mode="lines+markers+text",
                name="Índice Sazonal da Soja",
                line=dict(color=COLORS["Soja"], width=3.5),
                marker=dict(
                    size=11,
                    color=["#15803d" if v >= 100 else "#d97706" for v in df_saz["indice_sazonal"]],
                ),
                text=[f"{fmt_num(v, 1)}<br>({fmt_brl(p)})" for v, p in zip(df_saz["indice_sazonal"], df_saz["media_preco_mes"])],
                textposition="top center",
            )
        )
        fig.add_hline(y=100, line_dash="dash", line_color="#64748b", annotation_text="Média Histórica = 100")
        fig.update_layout(
            title="Índice Sazonal e Preço Médio Real por Mês do Ano (2007–2024)",
            xaxis=dict(title="Mês", categoryorder="array", categoryarray=MESES_ORDEM),
            yaxis=dict(title="Índice Sazonal (100 = média da cultura)", range=[94, 106.5]),
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    else:
        comp_sel = st.radio(
            "Componente da decomposição STL:",
            options=["Visão Integrada (Tendência + Sazonal + Resíduo)", "Apenas Tendência", "Apenas Sazonalidade", "Apenas Resíduo (Choques)"],
            horizontal=True,
        )
        df_stl_f = filtrar_df(DATA["stl"]).sort_values("data")
        fig = go.Figure()
        if comp_sel == "Apenas Tendência":
            fig.add_trace(go.Scatter(x=df_stl_f["data"], y=df_stl_f["tendencia"], mode="lines", name="Tendência STL (R$/60 kg)", line=dict(color=COLORS["Soja"], width=3.2)))
        elif comp_sel == "Apenas Sazonalidade":
            fig.add_trace(go.Scatter(x=df_stl_f["data"], y=df_stl_f["sazonal"], mode="lines", name="Componente Sazonal (R$/60 kg)", line=dict(color=COLORS["CEPEA"], width=2.8)))
            fig.add_hline(y=0, line_dash="dot", line_color="#64748b")
        elif comp_sel == "Apenas Resíduo (Choques)":
            fig.add_trace(go.Bar(x=df_stl_f["data"], y=df_stl_f["residuo"], name="Resíduo / Choques de Curto Prazo (R$/60 kg)", marker_color=COLORS["CBOT_BRL"]))
            fig.add_hline(y=0, line_dash="dot", line_color="#64748b")
        else:
            fig.add_trace(go.Scatter(x=df_stl_f["data"], y=df_stl_f["tendencia"], mode="lines", name="Tendência (Longo Prazo)", line=dict(color=COLORS["Soja"], width=3.2)))
            fig.add_trace(go.Scatter(x=df_stl_f["data"], y=df_stl_f["sazonal"], mode="lines", name="Componente Sazonal", line=dict(color=COLORS["CEPEA"], width=2)))
            fig.add_trace(go.Scatter(x=df_stl_f["data"], y=df_stl_f["residuo"], mode="lines", name="Resíduo (Choques)", line=dict(color=COLORS["CBOT_BRL"], width=1.8, dash="dot")))
            fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8")

        fig.update_layout(
            title=f"Decomposição STL da Série Real da Soja — {comp_sel}",
            xaxis_title="Data",
            yaxis_title="R$/60 kg",
        )
        st.plotly_chart(apply_plotly_style(fig, height=560), width="stretch")


# ==============================================================================
# PÁGINA 4: CÂMBIO E MERCADO INTERNACIONAL (CBOT / USDA-ERS)
# ==============================================================================
elif pagina_atual == "4. Câmbio e Mercado Internacional (CBOT)":
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("DERAL x CBOT em R$ (Níveis)", "r = 0,988", "Spearman ρ = 0,983 (Forte co-movimento)")
    with k2:
        render_kpi("DERAL x CBOT em R$ (Var. Mensal)", "r = 0,730", "Spearman ρ = 0,742 (Curto prazo)")
    with k3:
        render_kpi("DERAL Real x Dólar (Níveis)", "r = 0,691", "Longo prazo acompanha o câmbio")
    with k4:
        render_kpi("DERAL Real x Dólar (Var. Mensal)", "r = 0,224", "Câmbio sozinho não explica o mês a mês")

    st.write("")
    op_cbot = st.segmented_control(
        "Escolha o gráfico para apresentar:",
        options=[
            "🌎 Preço DERAL vs. CBOT Convertida (R$/60 kg) e CBOT (US$/bu)",
            "📊 Correlações de Pearson e Spearman (Níveis vs. Variações Mensais)",
            "📈 Comparativo em Índice Base 100 (Jan/2007 = 100)",
        ],
        default="🌎 Preço DERAL vs. CBOT Convertida (R$/60 kg) e CBOT (US$/bu)",
    )

    df_soja_m = filtrar_df(DATA["soja_mercado_mensal"]).sort_values("data")

    if op_cbot == "📊 Correlações de Pearson e Spearman (Níveis vs. Variações Mensais)":
        df_scorr = DATA["soja_correlacoes"]
        fig = px.bar(
            df_scorr,
            x="comparacao",
            y="correlacao",
            color="metodo",
            facet_col="tipo_serie",
            barmode="group",
            text=df_scorr["correlacao"].apply(lambda v: fmt_num(v, 3)),
            color_discrete_sequence=[COLORS["Soja"], COLORS["CEPEA"]],
            labels={"comparacao": "Par de Variáveis Analisado", "correlacao": "Coeficiente de Correlação", "metodo": "Método"},
        )
        fig.update_traces(textposition="outside")
        fig.update_yaxes(range=[0, 1.15])
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#0f172a", size=14),
            title="Contraste de Correlações da Soja: Níveis Mensais vs. Variações Mensais",
            height=600,
            margin=dict(t=95, l=85, r=85, b=95),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=14, color="#0f172a")))
        st.plotly_chart(fig, width="stretch")

    elif op_cbot == "📈 Comparativo em Índice Base 100 (Jan/2007 = 100)":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_deral_100"], mode="lines", name="Soja DERAL Nominal (Base 100)", line=dict(color=COLORS["Soja"], width=3.2)))
        fig.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_cbot_convertida_100"], mode="lines", name="CBOT Convertida em R$ (Base 100)", line=dict(color=COLORS["CBOT_BRL"], width=2.6, dash="dash")))
        fig.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_dolar_100"], mode="lines", name="Dólar Comercial (Base 100)", line=dict(color=COLORS["Dolar"], width=2.2, dash="dot")))
        fig.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_cbot_100"], mode="lines", name="CBOT em US$/bushel (Base 100)", line=dict(color=COLORS["CBOT"], width=2)))
        fig.add_hline(y=100, line_dash="dot", line_color="#64748b")
        fig.update_layout(
            title="Evolução Relativa em Índice Base 100 (Janeiro/2007 = 100)",
            xaxis_title="Data",
            yaxis_title="Índice Base 100",
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    else:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_soja_m["data"],
                y=df_soja_m["preco_deral_nominal"],
                mode="lines",
                name="Preço Físico DERAL Nominal (R$/60 kg)",
                line=dict(color=COLORS["Soja"], width=3.2),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_soja_m["data"],
                y=df_soja_m["cbot_brl_60kg_sem_premio"],
                mode="lines",
                name="CBOT Convertida pelo Dólar s/ Prêmio (R$/60 kg)",
                line=dict(color=COLORS["CBOT_BRL"], width=2.8, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_soja_m["data"],
                y=df_soja_m["cbot_usd_bushel"],
                mode="lines",
                name="Cotação Futuros CBOT (US$/bushel)",
                yaxis="y2",
                line=dict(color=COLORS["CBOT"], width=2, dash="dot"),
            )
        )
        fig.update_layout(
            title="Co-movimento entre Preço Físico no Paraná (DERAL) e Referência Internacional (CBOT Convertida em R$/60 kg)",
            xaxis_title="Data",
            yaxis=dict(title="Preço em R$/60 kg"),
            yaxis2=dict(title="CBOT Original (US$/bushel)", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")


# ==============================================================================
# PÁGINA 5: DERAL vs. CEPEA E TENDÊNCIA LINEAR
# ==============================================================================
elif pagina_atual == "5. DERAL vs. CEPEA e Tendência":
    df_res_reg = DATA["resumo_reg_linear"].iloc[0]
    df_prev = DATA["previsoes_25_26"].sort_values("ano")
    prev_deral_26 = df_prev[(df_prev["fonte"] == "DERAL") & (df_prev["ano"] == 2026)]["preco_estimado_tendencia"].iloc[0]
    prev_cepea_26 = df_prev[(df_prev["fonte"] == "CEPEA") & (df_prev["ano"] == 2026)]["preco_estimado_tendencia"].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Média Observada (Ambas Fontes)", fmt_brl(df_res_reg["media_preco_observado"]), "Preços reais (IPCA dez/2024)")
    with c2:
        render_kpi("Erro da Reta Temporal (MAE)", fmt_brl(df_res_reg["erro_medio_absoluto"]), f"RMSE: {fmt_brl(df_res_reg['rmse'])}")
    with c3:
        render_kpi("Tendência DERAL (2026)", fmt_brl(prev_deral_26), "Projeção linear inercial")
    with c4:
        render_kpi("Tendência CEPEA (2026)", fmt_brl(prev_cepea_26), "Projeção linear inercial")

    st.write("")
    op_f = st.segmented_control(
        "Escolha o gráfico:",
        options=[
            "🔄 Comparação Mensal: DERAL/PR vs. CEPEA/ESALQ",
            "📐 Regressão Linear Histórica (2007–2024) e Projeção (2025–2026)",
        ],
        default="🔄 Comparação Mensal: DERAL/PR vs. CEPEA/ESALQ",
    )

    if op_f == "🔄 Comparação Mensal: DERAL/PR vs. CEPEA/ESALQ":
        df_cm = filtrar_df(DATA["comp_mensal_fontes"]).sort_values("data")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_cm["data"],
                y=df_cm["CEPEA"],
                mode="lines",
                name="CEPEA/ESALQ (Indicador de Mercado — R$/60 kg real)",
                line=dict(color=COLORS["CEPEA"], width=2.8),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_cm["data"],
                y=df_cm["DERAL"],
                mode="lines",
                name="DERAL/PR (Preço Recebido pelo Produtor — R$/60 kg real)",
                line=dict(color=COLORS["DERAL"], width=2.8),
            )
        )
        fig.add_trace(
            go.Bar(
                x=df_cm["data"],
                y=df_cm["diferenca_cepea_menos_deral"],
                name="Diferença (CEPEA - DERAL)",
                marker_color="rgba(29, 78, 216, 0.28)",
            )
        )
        fig.update_layout(
            title="Comparação de Preços Reais da Soja: CEPEA/ESALQ vs. DERAL/PR (R$/60 kg — Base Dez/2024)",
            xaxis_title="Data",
            yaxis_title="R$/60 kg (IPCA Dez/2024)",
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")

    else:
        df_rh = filtrar_df(DATA["reg_linear_hist"]).sort_values("ano")
        fig = go.Figure()
        for f_nome, cor in [("CEPEA", COLORS["CEPEA"]), ("DERAL", COLORS["DERAL"])]:
            sub = df_rh[df_rh["fonte"] == f_nome].sort_values("ano")
            sub_p = df_prev[df_prev["fonte"] == f_nome].sort_values("ano")
            fig.add_trace(
                go.Scatter(
                    x=sub["ano"],
                    y=sub["preco_observado"],
                    mode="lines+markers",
                    name=f"Média Anual Observada · {f_nome}",
                    line=dict(color=cor, width=3.2),
                    marker=dict(size=8),
                )
            )
            anos_t = sub["ano"].tolist() + sub_p["ano"].tolist()
            est_t = sub["preco_estimado"].tolist() + sub_p["preco_estimado_tendencia"].tolist()
            fig.add_trace(
                go.Scatter(
                    x=anos_t,
                    y=est_t,
                    mode="lines+markers",
                    name=f"Reta de Tendência Linear (c/ 2025–2026) · {f_nome}",
                    line=dict(color=cor, width=2.2, dash="dash"),
                )
            )
        fig.update_layout(
            title="Tendência Linear Histórica (2007–2024) e Projeção Inercial (2025–2026)",
            xaxis=dict(title="Ano", dtick=1),
            yaxis_title="Preço Real da Soja (R$/60 kg)",
        )
        st.plotly_chart(apply_plotly_style(fig, height=580), width="stretch")


# ==============================================================================
# PÁGINA 6: MODELAGEM PREDITIVA DA SOJA (TESTE 2022–2024) — LIMPA E VISUAL
# ==============================================================================
elif pagina_atual == "6. Modelagem Preditiva (2022–2024)":
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
