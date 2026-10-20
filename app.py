import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA E TEMA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Interativo — Monitor de Preços da Soja no Paraná (2007–2024)",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de cores dedicada à Soja, Câmbio, Fontes e CBOT
COLORS = {
    "Soja": "#16a34a",
    "DERAL": "#16a34a",
    "CEPEA": "#2563eb",
    "Dolar": "#b45309",
    "CBOT": "#8b5cf6",
    "CBOT_BRL": "#f59e0b",
    "Modelo": "#ea580c",
    "Observado_Teste": "#0d9488",
}

MESES_ORDEM = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Estilo customizado (Dark / Emerald Theme inspirado na dashboard original)
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #064e3b, #065f46);
        color: #ffffff;
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        color: #d1fae5;
    }
    .kpi-card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 16px 18px;
        border-top: 4px solid #4d7c38;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        height: 100%;
    }
    .kpi-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        color: #a1a1aa;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #84cc16;
        margin-top: 6px;
    }
    .kpi-sub {
        font-size: 0.80rem;
        color: #d4d4d8;
        margin-top: 4px;
    }
    .exp-box {
        background-color: #27272a;
        border-left: 4px solid #65a30d;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        color: #d4d4d8;
        font-size: 0.92rem;
        margin-bottom: 14px;
    }
    .footer-box {
        text-align: center;
        font-size: 0.82rem;
        color: #a1a1aa;
        padding: 24px 10px 10px 10px;
        border-top: 1px solid #333;
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# FUNÇÕES AUXILIARES DE FORMATAÇÃO E CARREGAMENTO (APENAS SOJA)
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
        "resumo_projeto": load_csv("dashboard_resumo_projeto.csv"),
        "resumo_cultura": load_csv("dashboard_resumo_cultura.csv", filter_soja=True),
        "indicadores_finais": load_csv("dashboard_indicadores_finais.csv", filter_soja=True),
        "serie_mensal": load_csv("dashboard_serie_mensal_precos_dolar.csv", filter_soja=True),
        "serie_anual": load_csv("dashboard_serie_anual_precos_dolar.csv", filter_soja=True),
        "volatilidade_anual": load_csv("dashboard_volatilidade_anual.csv", filter_soja=True),
        "sazonalidade": load_csv("dashboard_sazonalidade_mensal.csv", filter_soja=True),
        "ranking_meses": load_csv("dashboard_ranking_meses.csv", filter_soja=True),
        "extremos": load_csv("dashboard_extremos_precos.csv", filter_soja=True),
        "base100": load_csv("dashboard_comparativo_preco_dolar_base100.csv", filter_soja=True),
        "correlacao_dolar": load_csv("dashboard_correlacao_preco_dolar.csv", filter_soja=True),
        "dolar_mensal": load_csv("dashboard_dolar_mensal.csv"),
        "ipca_tratado": load_csv("dashboard_ipca_ibge_tratado.csv"),
        "stl": load_csv("dashboard_decomposicao_stl.csv", filter_soja=True),
        "comp_mensal_fontes": load_csv("dashboard_comparacao_mensal_deral_cepea.csv", filter_soja=True),
        "base_comp_ipca": load_csv("dashboard_base_comparativa_deral_cepea_ipca.csv", filter_soja=True),
        "reg_linear_hist": load_csv("dashboard_regressao_linear_historica.csv", filter_soja=True),
        "resumo_reg_linear": load_csv("dashboard_resumo_regressao_linear.csv", filter_soja=True),
        "previsoes_25_26": load_csv("dashboard_previsoes_tendencia_2025_2026.csv", filter_soja=True),
        # Soja & CBOT (Resumo Expandido IX SIEPE 2026)
        "soja_cards_mercado": load_csv("dashboard_soja_cards_mercado.csv"),
        "soja_cards_modelos": load_csv("dashboard_soja_cards_modelos.csv"),
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


def render_exp(text: str):
    st.markdown(f'<div class="exp-box">{text}</div>', unsafe_allow_html=True)


def apply_plotly_style(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,30,30,0.6)",
        height=height,
        margin=dict(t=35, l=50, r=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    return fig


# ==============================================================================
# CARREGAMENTO DE DADOS E SIDEBAR DE CONTROLES
# ==============================================================================
DATA = load_all_data()
df_serie = DATA["serie_mensal"]
anos_disponiveis = sorted(df_serie["ano"].unique().tolist())
ano_min, ano_max = int(min(anos_disponiveis)), int(max(anos_disponiveis))

with st.sidebar:
    st.markdown("## 🌱 Filtros — Soja")
    st.caption("Ajuste o intervalo temporal para atualizar as séries históricas, estatísticas e gráficos da Soja.")

    if "intervalo_anos" not in st.session_state:
        st.session_state["intervalo_anos"] = (ano_min, ano_max)

    def reset_filters():
        st.session_state["intervalo_anos"] = (ano_min, ano_max)

    intervalo_anos = st.slider(
        "Período de análise (Anos)",
        min_value=ano_min,
        max_value=ano_max,
        step=1,
        key="intervalo_anos",
    )
    start_year, end_year = intervalo_anos

    st.button("🔄 Resetar período (2007–2024)", on_click=reset_filters, width="stretch")

    st.divider()
    st.markdown("### 📌 Resumo de Indicadores (Soja)")
    st.markdown(
        "- **Observações (DERAL):** 216 meses (2007–2024)\n"
        "- **Unidade padrão:** R$/60 kg\n"
        "- **Deflação:** IPCA (base dez/2024)\n"
        "- **Ref. Internacional:** CBOT (US$/bushel → R$/60 kg)\n"
        "- **R² Modelo de Preço:** `0,757` (Teste 2022–2024)\n"
        "- **Acurácia Direcional:** `69,44%` (Corte `0,67`)"
    )

    st.divider()
    st.markdown("### 📄 Sobre o Estudo (SIEPE 2026)")
    st.info(
        "**Autores:** Vicente F. C. dos Santos, André L. D. da Silva, Wagner H. M. Cichacz, "
        "Miguel T. Macedo, Diego B. Santi\n\n"
        "**Instituição:** UNICENTRO\n\n"
        "**Fontes:** DERAL/PR, CEPEA/ESALQ, IBGE (IPCA), BCB (PTAX) e USDA/ERS (CBOT)."
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
        <h1>🌱 Dashboard Interativo — Análise de Preços da Soja no Paraná (2007–2024)</h1>
        <p>Relações com Inflação (IPCA), Câmbio (BCB) e Mercado Internacional (CBOT / USDA-ERS) • Modelagem Preditiva de Preço e Direção Mensal</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# NAVEGAÇÃO EM ABAS (EXCLUSIVA PARA A SOJA)
# ==============================================================================
tabs = st.tabs([
    "1. Visão Geral (Soja)",
    "2. Evolução Real & Câmbio",
    "3. Anual & Volatilidade",
    "4. Sazonalidade & Decomposição STL",
    "5. Extremos Históricos",
    "6. Base 100, Câmbio & CBOT",
    "7. DERAL x CEPEA & Tendência",
    "8. Modelos Preditivos (Preço & Direção)",
])

# ------------------------------------------------------------------------------
# ABA 1: VISÃO GERAL (SOJA)
# ------------------------------------------------------------------------------
with tabs[0]:
    df_s_filt = filtrar_df(df_serie).sort_values("data")
    df_soja_m_filt = filtrar_df(DATA["soja_mercado_mensal"]).sort_values("data")
    anos_f = sorted(df_s_filt["ano"].unique().tolist())

    vals = df_s_filt["preco_real_dez_2024"].dropna()
    first_row = df_s_filt.iloc[0]
    last_row = df_s_filt.iloc[-1]
    media_real = vals.mean()
    mediana_real = vals.median()
    min_real = vals.min()
    max_real = vals.max()
    desvio_real = vals.std(ddof=1) if len(vals) > 1 else 0.0
    cv_real = (desvio_real / media_real * 100) if media_real else 0.0
    var_total_real = ((last_row["preco_real_dez_2024"] / first_row["preco_real_dez_2024"]) - 1) * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        recorte_str = f"{anos_f[0]}–{anos_f[-1]}" if anos_f else "-"
        render_kpi(
            "Período Selecionado",
            recorte_str,
            f"{len(df_s_filt)} meses analisados · 0 imputações",
        )
    with c2:
        render_kpi(
            "Preço Médio Real (Soja)",
            fmt_brl(media_real),
            f"Mediana: {fmt_brl(mediana_real)} (IPCA dez/2024)",
        )
    with c3:
        render_kpi(
            "Amplitude Real no Período",
            f"{fmt_brl(min_real)} – {fmt_brl(max_real)}",
            f"Coef. de Variação: {fmt_pct(cv_real)}",
        )
    with c4:
        render_kpi(
            "Fechamento (Dez/2024)",
            fmt_brl(last_row["preco_real_dez_2024"]),
            f"Variação acumulada: {fmt_pct(var_total_real)}",
        )

    st.write("")
    st.markdown("### Destaques de Mercado e Modelagem da Soja (Dezembro/2024 & Teste 2022–2024)")
    render_exp(
        "Resumo executivo da soja integrando o preço físico estadual (DERAL/PR), a referência internacional na bolsa de Chicago (CBOT/USDA-ERS), "
        "o dólar comercial (BCB) e o desempenho dos modelos preditivos avaliados fora da amostra (2022–2024)."
    )

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        render_kpi("DERAL Dez/2024", "R$ 130,11", "R$/60 kg no fechamento")
    with m2:
        render_kpi("CBOT Dez/2024", "US$ 9,85/bu", "Ref. internacional futuros")
    with m3:
        render_kpi("CBOT Convertida", "R$ 132,42", "R$/60 kg (sem prêmio)")
    with m4:
        render_kpi("Dólar Dez/2024", "R$ 6,0970", "Média mensal PTAX/BCB")
    with m5:
        render_kpi("Modelo de Preço", "R² = 0,757", "MAPE: 8,09% | MAE: R$ 10,58")
    with m6:
        render_kpi("Modelo Direcional", "69,44%", "Ganho: +27,78 p.p. s/ baseline")

    st.write("")
    col_t1, col_t2 = st.columns([1.25, 1])
    with col_t1:
        st.markdown("#### Estatísticas Descritivas da Soja no Recorte Selecionado (Preços Reais — Base Dez/2024)")
        df_est_soja = pd.DataFrame([
            {"Indicador": "Quantidade de meses avaliados", "Valor": f"{len(df_s_filt)} meses"},
            {"Indicador": "Preço Real Inicial (" + first_row["data"][:7] + ")", "Valor": fmt_brl(first_row["preco_real_dez_2024"])},
            {"Indicador": "Preço Real Final (" + last_row["data"][:7] + ")", "Valor": fmt_brl(last_row["preco_real_dez_2024"])},
            {"Indicador": "Preço Médio Real (R$/60 kg)", "Valor": fmt_brl(media_real)},
            {"Indicador": "Preço Mediano Real (R$/60 kg)", "Valor": fmt_brl(mediana_real)},
            {"Indicador": "Menor Preço Real Observado", "Valor": fmt_brl(min_real)},
            {"Indicador": "Maior Preço Real Observado", "Valor": fmt_brl(max_real)},
            {"Indicador": "Desvio Padrão Real", "Valor": fmt_brl(desvio_real)},
            {"Indicador": "Coeficiente de Variação (CV)", "Valor": fmt_pct(cv_real)},
            {"Indicador": "Variação Acumulada no Período", "Valor": fmt_pct(var_total_real)},
        ])
        st.dataframe(df_est_soja, width="stretch", hide_index=True)

    with col_t2:
        st.markdown("#### Distribuição dos Preços Mensais Reais da Soja (R$/60 kg)")
        fig_hist = go.Figure()
        fig_hist.add_trace(
            go.Histogram(
                x=df_s_filt["preco_real_dez_2024"],
                nbinsx=24,
                name="Frequência Mensal",
                marker_color=COLORS["Soja"],
                opacity=0.85,
            )
        )
        fig_hist.add_vline(x=media_real, line_dash="dash", line_color="#f59e0b", annotation_text=f"Média: {fmt_brl(media_real)}")
        fig_hist.add_vline(x=mediana_real, line_dash="dot", line_color="#38bdf8", annotation_text=f"Mediana: {fmt_brl(mediana_real)}")
        fig_hist.update_layout(xaxis_title="Preço Real da Soja (R$/60 kg)", yaxis_title="Quantidade de Meses")
        st.plotly_chart(apply_plotly_style(fig_hist, height=370), width="stretch")

# ------------------------------------------------------------------------------
# ABA 2: EVOLUÇÃO HISTÓRICA REAL & CÂMBIO
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### Evolução Mensal do Preço Real da Soja (DERAL) vs. Taxa de Câmbio (BCB)")
    render_exp(
        "Comparativo entre o preço mensal da soja corrigido pelo IPCA para dezembro de 2024 (R$/60 kg, eixo esquerdo) "
        "e a taxa de câmbio média mensal (R$/US$, eixo direito)."
    )

    df_s_filt = filtrar_df(df_serie).sort_values("data")
    fig_cd = go.Figure()
    fig_cd.add_trace(
        go.Scatter(
            x=df_s_filt["data"],
            y=df_s_filt["preco_real_dez_2024"],
            mode="lines",
            name="Soja Real DERAL (R$/60 kg - base dez/2024)",
            line=dict(color=COLORS["Soja"], width=2.5),
        )
    )
    fig_cd.add_trace(
        go.Scatter(
            x=df_s_filt["data"],
            y=df_s_filt["dolar_medio_mensal"],
            mode="lines",
            name="Taxa de Câmbio Média Mensal (R$/US$)",
            yaxis="y2",
            line=dict(color=COLORS["Dolar"], width=2, dash="dot"),
        )
    )
    fig_cd.update_layout(
        xaxis_title="Data",
        yaxis=dict(title="Preço Real da Soja (R$/60 kg)"),
        yaxis2=dict(title="Taxa de Câmbio (R$/US$)", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(apply_plotly_style(fig_cd, height=440), width="stretch")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("#### Variação em 12 Meses da Soja vs. Dólar (%)")
        render_exp("Valores positivos indicam cotação acima do mesmo mês do ano anterior.")
        sub_12m = df_s_filt[df_s_filt["variacao_preco_12_meses_percentual"].notna()]
        fig_12m = go.Figure()
        fig_12m.add_trace(
            go.Scatter(
                x=sub_12m["data"],
                y=sub_12m["variacao_preco_12_meses_percentual"],
                mode="lines",
                name="Var. 12m Soja Real (%)",
                line=dict(color=COLORS["Soja"], width=2.2),
            )
        )
        fig_12m.add_trace(
            go.Scatter(
                x=sub_12m["data"],
                y=sub_12m["variacao_dolar_12_meses_percentual"],
                mode="lines",
                name="Var. 12m Dólar (%)",
                line=dict(color=COLORS["Dolar"], width=1.6, dash="dot"),
            )
        )
        fig_12m.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        fig_12m.update_layout(xaxis_title="Data", yaxis_title="Variação em 12 Meses (%)")
        st.plotly_chart(apply_plotly_style(fig_12m, height=360), width="stretch")

    with col_v2:
        st.markdown("#### Variação Acumulada do Preço Real da Soja (%)")
        render_exp("Mostra o ganho ou recuo percentual acumulado do preço real da soja desde janeiro de 2007.")
        fig_acum = go.Figure()
        fig_acum.add_trace(
            go.Scatter(
                x=df_s_filt["data"],
                y=df_s_filt["variacao_preco_acumulada_percentual"],
                mode="lines",
                fill="tozeroy",
                name="Var. Acumulada Soja Real (%)",
                line=dict(color=COLORS["Soja"], width=2.2),
            )
        )
        fig_acum.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        fig_acum.update_layout(xaxis_title="Data", yaxis_title="Variação Acumulada (%)")
        st.plotly_chart(apply_plotly_style(fig_acum, height=360), width="stretch")

# ------------------------------------------------------------------------------
# ABA 3: ANUAL & VOLATILIDADE (SOJA)
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### Preço Médio Anual da Soja vs. Dólar Médio Anual")
    render_exp(
        "Evolução anual do preço médio real da soja (com faixa entre mínimo e máximo anual em R$/60 kg) e a média anual do dólar comercial (R$/US$)."
    )

    df_anual_f = filtrar_df(DATA["serie_anual"]).sort_values("ano")
    fig_anual = go.Figure()
    fig_anual.add_trace(
        go.Scatter(
            x=df_anual_f["ano"],
            y=df_anual_f["preco_maximo_anual"],
            mode="lines",
            name="Máximo Real no Ano",
            line=dict(color="#4ade80", width=1, dash="dash"),
        )
    )
    fig_anual.add_trace(
        go.Scatter(
            x=df_anual_f["ano"],
            y=df_anual_f["preco_minimo_anual"],
            mode="lines",
            name="Mínimo Real no Ano",
            fill="tonexty",
            fillcolor="rgba(22, 163, 74, 0.15)",
            line=dict(color="#4ade80", width=1, dash="dash"),
        )
    )
    fig_anual.add_trace(
        go.Scatter(
            x=df_anual_f["ano"],
            y=df_anual_f["preco_medio_anual"],
            mode="lines+markers",
            name="Preço Médio Anual da Soja (R$/60 kg)",
            line=dict(color=COLORS["Soja"], width=3),
            marker=dict(size=8),
        )
    )
    fig_anual.add_trace(
        go.Scatter(
            x=df_anual_f["ano"],
            y=df_anual_f["dolar_medio_anual"],
            mode="lines+markers",
            name="Dólar Médio Anual (R$/US$)",
            yaxis="y2",
            line=dict(color=COLORS["Dolar"], width=2.2, dash="dot"),
        )
    )
    fig_anual.update_layout(
        xaxis=dict(title="Ano", dtick=1),
        yaxis=dict(title="Preço Real da Soja (R$/60 kg)"),
        yaxis2=dict(title="Dólar (R$/US$)", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(apply_plotly_style(fig_anual, height=420), width="stretch")

    col_va1, col_va2 = st.columns([1.15, 1])
    with col_va1:
        st.markdown("#### Volatilidade Intra-anual da Soja (Coeficiente de Variação %)")
        render_exp("Barras maiores indicam anos com maior oscilação mensal de preços dentro do próprio ano.")
        df_vol_f = filtrar_df(DATA["volatilidade_anual"]).sort_values("ano")
        fig_vol = go.Figure()
        fig_vol.add_trace(
            go.Bar(
                x=df_vol_f["ano"],
                y=df_vol_f["coeficiente_variacao_anual"],
                name="CV Anual da Soja (%)",
                marker_color=COLORS["Soja"],
                text=[fmt_pct(v, 1) for v in df_vol_f["coeficiente_variacao_anual"]],
                textposition="auto",
            )
        )
        fig_vol.update_layout(
            xaxis=dict(title="Ano", dtick=1),
            yaxis=dict(title="Coeficiente de Variação Anual (%)"),
        )
        st.plotly_chart(apply_plotly_style(fig_vol, height=360), width="stretch")

    with col_va2:
        st.markdown("#### Tabela Anual da Soja (Preços Reais, Volatilidade e Câmbio)")
        df_anual_tab = pd.DataFrame({
            "Ano": df_anual_f["ano"],
            "Preço Médio": df_anual_f["preco_medio_anual"].apply(fmt_brl),
            "Mínimo": df_anual_f["preco_minimo_anual"].apply(fmt_brl),
            "Máximo": df_anual_f["preco_maximo_anual"].apply(fmt_brl),
            "CV Anual": df_anual_f["coeficiente_variacao_anual"].apply(fmt_pct),
            "Var. Anual": df_anual_f["variacao_anual_percentual"].apply(fmt_pct),
            "Dólar Médio": df_anual_f["dolar_medio_anual"].apply(lambda v: fmt_brl(v, 4)),
        })
        st.dataframe(df_anual_tab, width="stretch", hide_index=True, height=360)

# ------------------------------------------------------------------------------
# ABA 4: SAZONALIDADE & DECOMPOSIÇÃO STL (SOJA)
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### Sazonalidade Mensal da Soja (Índice Sazonal: 100 = Média Histórica)")
    render_exp(
        "Meses com índice acima de 100 apresentaram historicamente preços médios superiores à média global da soja (com destaque para o segundo semestre/entressafra, como outubro e novembro). "
        "Meses abaixo de 100 concentram o período de colheita e entrada de safra."
    )

    df_saz = DATA["sazonalidade"].sort_values("mes")
    df_rank = DATA["ranking_meses"].sort_values("ranking_preco_medio")

    col_sz1, col_sz2 = st.columns([1.3, 1])
    with col_sz1:
        fig_saz = go.Figure()
        fig_saz.add_trace(
            go.Scatter(
                x=df_saz["nome_mes"],
                y=df_saz["indice_sazonal"],
                mode="lines+markers+text",
                name="Índice Sazonal da Soja",
                line=dict(color=COLORS["Soja"], width=3),
                marker=dict(size=9),
                text=[fmt_num(v, 1) for v in df_saz["indice_sazonal"]],
                textposition="top center",
            )
        )
        fig_saz.add_hline(y=100, line_dash="dot", line_color="#94a3b8", annotation_text="Média = 100")
        fig_saz.update_layout(
            xaxis=dict(title="Mês", categoryorder="array", categoryarray=MESES_ORDEM),
            yaxis=dict(title="Índice Sazonal (100 = média)"),
        )
        st.plotly_chart(apply_plotly_style(fig_saz, height=380), width="stretch")

    with col_sz2:
        st.markdown("#### Ranking Histórico dos Meses (Soja)")
        df_rank_view = pd.DataFrame({
            "Ranking": df_rank["ranking_preco_medio"],
            "Mês": df_rank["nome_mes"],
            "Preço Médio Real": df_rank["media_preco_mes"].apply(fmt_brl),
            "Índice Sazonal": df_rank["indice_sazonal"].apply(fmt_num),
            "CV no Mês": df_rank["coeficiente_variacao_mes"].apply(fmt_pct),
        })
        st.dataframe(df_rank_view, width="stretch", hide_index=True, height=380)

    st.markdown("### Decomposição STL da Soja (Seasonal and Trend decomposition using Loess)")
    render_exp(
        "Conforme descrito na seção de *Material e Métodos* do resumo expandido, a decomposição STL divide a série mensal da soja em três componentes: "
        "**Tendência** (trajetória estrutural), **Componente Sazonal** (padrão recorrente intra-anual) e **Resíduo** (choques atípicos de curto prazo)."
    )
    df_stl_f = filtrar_df(DATA["stl"]).sort_values("data")
    col_stl1, col_stl2, col_stl3 = st.columns(3)
    for col_ui, (campo, titulo, cor) in zip(
        [col_stl1, col_stl2, col_stl3],
        [
            ("tendencia", "Tendência (R$/60 kg)", "#16a34a"),
            ("sazonal", "Componente Sazonal (R$/60 kg)", "#38bdf8"),
            ("residuo", "Resíduo / Choques (R$/60 kg)", "#f59e0b"),
        ],
    ):
        with col_ui:
            fig_stl = go.Figure()
            fig_stl.add_trace(
                go.Scatter(
                    x=df_stl_f["data"],
                    y=df_stl_f[campo],
                    mode="lines",
                    name=titulo,
                    line=dict(color=cor, width=2),
                )
            )
            if campo != "tendencia":
                fig_stl.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
            fig_stl.update_layout(title=titulo, xaxis_title="Data", yaxis_title="R$/60 kg")
            st.plotly_chart(apply_plotly_style(fig_stl, height=320), width="stretch")

# ------------------------------------------------------------------------------
# ABA 5: EXTREMOS HISTÓRICOS DA SOJA
# ------------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### Picos e Vales Históricos da Soja (5 Maiores e 5 Menores Preços Reais)")
    render_exp(
        "Os cinco meses de maior preço real (concentrados em 2021–2022, atingindo até R$ 214,31/60 kg em março/2022) e os cinco meses de menor preço real da soja na série."
    )
    df_ext = DATA["extremos"].copy()
    df_ext["rotulo"] = df_ext["nome_mes"] + "/" + df_ext["ano"].astype(str)

    maiores = df_ext[df_ext["tipo_extremo"].str.contains("Maior", case=False, na=False)]
    menores = df_ext[df_ext["tipo_extremo"].str.contains("Menor", case=False, na=False)]

    fig_ext = go.Figure()
    fig_ext.add_trace(
        go.Bar(
            x=maiores["rotulo"],
            y=maiores["preco_real_dez_2024"],
            name="5 Maiores Preços Reais da Soja",
            marker_color="#16a34a",
            text=[fmt_brl(v) for v in maiores["preco_real_dez_2024"]],
            textposition="auto",
        )
    )
    fig_ext.add_trace(
        go.Bar(
            x=menores["rotulo"],
            y=menores["preco_real_dez_2024"],
            name="5 Menores Preços Reais da Soja",
            marker_color="#dc2626",
            text=[fmt_brl(v) for v in menores["preco_real_dez_2024"]],
            textposition="auto",
        )
    )
    fig_ext.update_layout(yaxis_title="Preço Real da Soja (R$/60 kg)", xaxis_title="Mês/Ano")
    st.plotly_chart(apply_plotly_style(fig_ext, height=400), width="stretch")

    df_ext_view = pd.DataFrame({
        "Tipo de Extremo": df_ext["tipo_extremo"],
        "Data": df_ext["data"].str.slice(0, 7),
        "Mês": df_ext["nome_mes"],
        "Preço Real (R$/60 kg)": df_ext["preco_real_dez_2024"].apply(fmt_brl),
        "Dólar Médio no Mês": df_ext["dolar_medio_mensal"].apply(lambda x: fmt_brl(x, 4)),
        "Variação Mensal": df_ext["variacao_preco_mensal_percentual"].apply(fmt_pct),
        "Variação 12 Meses": df_ext["variacao_preco_12_meses_percentual"].apply(fmt_pct),
        "Índice Base 100": df_ext["indice_preco_base_100"].apply(fmt_num),
    })
    st.dataframe(df_ext_view, width="stretch", hide_index=True)

# ------------------------------------------------------------------------------
# ABA 6: BASE 100, CÂMBIO & MERCADO INTERNACIONAL (CBOT / USDA-ERS)
# ------------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### 🌱 Integração da Soja com o Câmbio (BCB) e a Chicago Board of Trade (CBOT / USDA-ERS)")
    render_exp(
        "**Metodologia (Resumo Expandido IX SIEPE 2026):** Para a soja, incorporou-se a cotação de futuros da **Chicago Board of Trade (CBOT)** "
        "(disponibilizada pelo USDA/ERS), convertida de **US$/bushel** para **US$/60 kg** e depois para **R$/60 kg** pelo dólar médio mensal. "
        "A série foi tratada como referência internacional **sem prêmio regional** (pela ausência de série histórica regional confiável para todo o período)."
    )

    # KPIs de correlação da soja do Resumo Expandido
    k_c1, k_c2, k_c3, k_c4 = st.columns(4)
    with k_c1:
        render_kpi("DERAL Real x Dólar (Níveis)", "r = 0,691", "Var. mensais: r = 0,224 (Pearson)")
    with k_c2:
        render_kpi("DERAL Nominal x CBOT (R$)", "r = 0,988", "Em níveis · Spearman ρ = 0,983")
    with k_c3:
        render_kpi("Var. DERAL x Var. CBOT (R$)", "r = 0,730", "Var. mensais · Spearman ρ = 0,742")
    with k_c4:
        render_kpi("Var. DERAL x Var. CBOT (US$)", "r = 0,545", "Var. mensais · Spearman ρ = 0,506")

    st.write("")
    df_soja_m = filtrar_df(DATA["soja_mercado_mensal"]).sort_values("data")

    col_sm1, col_sm2 = st.columns([1.35, 1])
    with col_sm1:
        st.markdown("#### Preço Físico Nominal DERAL vs. Referência CBOT Convertida (R$/60 kg) e CBOT (US$/bu)")
        fig_scbot = go.Figure()
        fig_scbot.add_trace(
            go.Scatter(
                x=df_soja_m["data"],
                y=df_soja_m["preco_deral_nominal"],
                mode="lines",
                name="Preço Físico DERAL Nominal (R$/60 kg)",
                line=dict(color=COLORS["Soja"], width=2.5),
            )
        )
        fig_scbot.add_trace(
            go.Scatter(
                x=df_soja_m["data"],
                y=df_soja_m["cbot_brl_60kg_sem_premio"],
                mode="lines",
                name="CBOT Convertida s/ Prêmio (R$/60 kg)",
                line=dict(color=COLORS["CBOT_BRL"], width=2.2, dash="dash"),
            )
        )
        fig_scbot.add_trace(
            go.Scatter(
                x=df_soja_m["data"],
                y=df_soja_m["cbot_usd_bushel"],
                mode="lines",
                name="CBOT Futuros (US$/bushel)",
                yaxis="y2",
                line=dict(color=COLORS["CBOT"], width=1.6, dash="dot"),
            )
        )
        fig_scbot.update_layout(
            xaxis_title="Data",
            yaxis=dict(title="R$/60 kg"),
            yaxis2=dict(title="US$/bushel (CBOT)", overlaying="y", side="right", showgrid=False),
        )
        st.plotly_chart(apply_plotly_style(fig_scbot, height=420), width="stretch")

    with col_sm2:
        st.markdown("#### Comparação Relativa em Índice Base 100 (Janeiro/2007 = 100)")
        tipo_b100 = st.radio(
            "Escolha a base de comparação (Jan/2007 = 100):",
            options=["Mercado Nominal (DERAL, CBOT R$, CBOT US$, Dólar)", "Preço Real Deflacionado (IPCA) vs. Dólar"],
            horizontal=False,
        )
        fig_sb100 = go.Figure()
        if "Mercado Nominal" in tipo_b100:
            fig_sb100.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_deral_100"], mode="lines", name="DERAL Nominal (Base 100)", line=dict(color=COLORS["Soja"], width=2.3)))
            fig_sb100.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_cbot_convertida_100"], mode="lines", name="CBOT em R$ (Base 100)", line=dict(color=COLORS["CBOT_BRL"], width=2, dash="dash")))
            fig_sb100.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_dolar_100"], mode="lines", name="Dólar (Base 100)", line=dict(color=COLORS["Dolar"], width=1.8, dash="dot")))
            fig_sb100.add_trace(go.Scatter(x=df_soja_m["data"], y=df_soja_m["indice_cbot_100"], mode="lines", name="CBOT em US$ (Base 100)", line=dict(color=COLORS["CBOT"], width=1.6)))
        else:
            df_b100 = filtrar_df(DATA["base100"]).sort_values("data")
            fig_sb100.add_trace(go.Scatter(x=df_b100["data"], y=df_b100["indice_preco_base_100"], mode="lines", name="Soja Real IPCA (Base 100)", line=dict(color=COLORS["Soja"], width=2.5)))
            fig_sb100.add_trace(go.Scatter(x=df_b100["data"], y=df_b100["indice_dolar_base_100"], mode="lines", name="Dólar (Base 100)", line=dict(color=COLORS["Dolar"], width=2, dash="dot")))
        fig_sb100.add_hline(y=100, line_dash="dot", line_color="#94a3b8")
        fig_sb100.update_layout(xaxis_title="Data", yaxis_title="Índice (Jan/2007 = 100)")
        st.plotly_chart(apply_plotly_style(fig_sb100, height=350), width="stretch")

    st.markdown("#### Associações Estatísticas da Soja: Pearson vs. Spearman (Níveis e Variações Mensais)")
    render_exp(
        "**Discussão do Resumo Expandido:** Na comparação entre o preço real do DERAL e o dólar, a correlação de Pearson foi **0,691 em níveis**, mas caiu para **0,224 nas variações mensais**, "
        "indicando que a associação de longo prazo não significa repasse cambial imediato em todas as oscilações mensais. "
        "Já quando se integra a CBOT convertida em reais (R$/60 kg), a associação com o preço físico estadual da soja atinge **0,988 (Pearson)** e **0,983 (Spearman)** em níveis, "
        "e **0,730 (Pearson)** e **0,742 (Spearman)** nas variações mensais, demonstrando forte co-movimento (embora sem prova de causalidade e sem incluir prêmio de exportação ou frete)."
    )

    df_scorr = DATA["soja_correlacoes"]
    col_sc1, col_sc2 = st.columns([1.2, 1])
    with col_sc1:
        fig_sc = px.bar(
            df_scorr,
            x="comparacao",
            y="correlacao",
            color="metodo",
            facet_col="tipo_serie",
            barmode="group",
            text=df_scorr["correlacao"].apply(lambda v: fmt_num(v, 3)),
            color_discrete_sequence=["#16a34a", "#38bdf8"],
            labels={"comparacao": "Par de Variáveis", "correlacao": "Coeficiente (r / ρ)", "metodo": "Método"},
        )
        fig_sc.update_yaxes(range=[0, 1.1])
        st.plotly_chart(apply_plotly_style(fig_sc, height=360), width="stretch")

    with col_sc2:
        df_scorr_v = pd.DataFrame({
            "Comparação": df_scorr["comparacao"],
            "Série": df_scorr["tipo_serie"],
            "Método": df_scorr["metodo"],
            "n": df_scorr["n"],
            "Coeficiente": df_scorr["correlacao"].apply(lambda v: fmt_num(v, 4)),
            "p-valor": df_scorr["p_valor"].apply(lambda v: f"{v:.2e}" if v > 0 else "< 0,0001"),
        })
        st.dataframe(df_scorr_v, width="stretch", hide_index=True, height=360)

    with st.expander("📊 Tabela Anual da Soja: DERAL Nominal, CBOT (US$/bushel), Dólar e CBOT Convertida (R$/60 kg)"):
        df_sra = filtrar_df(DATA["soja_resumo_anual"])
        st.dataframe(
            pd.DataFrame({
                "Ano": df_sra["ano"],
                "Preço Médio DERAL Nominal (R$/60 kg)": df_sra["preco_deral_medio"].apply(fmt_brl),
                "CBOT Média (US$/bushel)": df_sra["cbot_media_usd_bushel"].apply(fmt_usd),
                "Dólar Médio (R$/US$)": df_sra["dolar_medio"].apply(lambda v: fmt_brl(v, 4)),
                "CBOT Convertida Média (R$/60 kg)": df_sra["cbot_convertida_media_brl_60kg"].apply(fmt_brl),
            }),
            width="stretch",
            hide_index=True,
        )

# ------------------------------------------------------------------------------
# ABA 7: DERAL x CEPEA & TENDÊNCIA LINEAR (SOJA)
# ------------------------------------------------------------------------------
with tabs[6]:
    st.markdown("### Comparação de Fontes para a Soja: DERAL/PR vs. CEPEA/ESALQ (Preços Reais IPCA)")
    render_exp(
        "Comparação entre os preços reais da soja (R$/60 kg, corrigidos pelo IPCA para dez/2024) levantados pelo **DERAL** (preço recebido pelo produtor no Paraná) "
        "e pelo **CEPEA/ESALQ** (indicador de referência de mercado). Embora caminhem de forma fortemente alinhada, a diferença reflete custos logísticos, prêmios portuários e etapas de comercialização."
    )

    df_cm = filtrar_df(DATA["comp_mensal_fontes"]).sort_values("data")
    col_f1, col_f2 = st.columns([1.4, 1])
    with col_f1:
        fig_fontes = go.Figure()
        fig_fontes.add_trace(
            go.Scatter(x=df_cm["data"], y=df_cm["CEPEA"], mode="lines", name="Soja · CEPEA (R$/60 kg real)", line=dict(color=COLORS["CEPEA"], width=2.2))
        )
        fig_fontes.add_trace(
            go.Scatter(x=df_cm["data"], y=df_cm["DERAL"], mode="lines", name="Soja · DERAL (R$/60 kg real)", line=dict(color=COLORS["DERAL"], width=2.2, dash="dot"))
        )
        fig_fontes.update_layout(xaxis_title="Data", yaxis_title="Preço Real (R$/60 kg - base dez/2024)")
        st.plotly_chart(apply_plotly_style(fig_fontes, height=400), width="stretch")

    with col_f2:
        fig_dif = go.Figure()
        fig_dif.add_trace(
            go.Scatter(
                x=df_cm["data"],
                y=df_cm["diferenca_cepea_menos_deral"],
                mode="lines",
                fill="tozeroy",
                name="Diferença CEPEA - DERAL (R$/60 kg)",
                line=dict(color="#38bdf8", width=2),
            )
        )
        fig_dif.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        fig_dif.update_layout(
            title="Spread Mensal: CEPEA menos DERAL (R$/60 kg)",
            xaxis_title="Data",
            yaxis_title="Diferença Real (R$/60 kg)",
        )
        st.plotly_chart(apply_plotly_style(fig_dif, height=400), width="stretch")

    st.markdown("### Tendência Linear Histórica da Soja (2007–2024) e Projeção Inercial (2025–2026)")
    render_exp(
        "Avalia a tendência histórica por regressão linear anual para o DERAL e o CEPEA, estendendo a reta de tendência para 2025–2026."
    )

    df_rh = filtrar_df(DATA["reg_linear_hist"]).sort_values("ano")
    df_prev = DATA["previsoes_25_26"].sort_values("ano")

    col_r1, col_r2 = st.columns([1.45, 1])
    with col_r1:
        fig_reg = go.Figure()
        for f_nome, cor in [("CEPEA", COLORS["CEPEA"]), ("DERAL", COLORS["DERAL"])]:
            sub = df_rh[df_rh["fonte"] == f_nome].sort_values("ano")
            sub_p = df_prev[df_prev["fonte"] == f_nome].sort_values("ano")
            fig_reg.add_trace(
                go.Scatter(
                    x=sub["ano"],
                    y=sub["preco_observado"],
                    mode="lines+markers",
                    name=f"Observado · {f_nome}",
                    line=dict(color=cor, width=2.5),
                )
            )
            anos_t = sub["ano"].tolist() + sub_p["ano"].tolist()
            est_t = sub["preco_estimado"].tolist() + sub_p["preco_estimado_tendencia"].tolist()
            fig_reg.add_trace(
                go.Scatter(
                    x=anos_t,
                    y=est_t,
                    mode="lines+markers",
                    name=f"Tendência Linear (c/ 2025–2026) · {f_nome}",
                    line=dict(color=cor, width=1.8, dash="dash"),
                )
            )
        fig_reg.update_layout(xaxis=dict(title="Ano", dtick=1), yaxis_title="Preço Real da Soja (R$/60 kg)")
        st.plotly_chart(apply_plotly_style(fig_reg, height=380), width="stretch")

    with col_r2:
        st.markdown("#### Erro da Tendência Linear (Soja)")
        df_res_reg = DATA["resumo_reg_linear"]
        st.dataframe(
            pd.DataFrame({
                "Cultura": df_res_reg["cultura"],
                "Preço Médio Observado": df_res_reg["media_preco_observado"].apply(fmt_brl),
                "MAE (Erro Médio Absoluto)": df_res_reg["erro_medio_absoluto"].apply(fmt_brl),
                "RMSE": df_res_reg["rmse"].apply(fmt_brl),
            }),
            width="stretch",
            hide_index=True,
        )
        st.markdown("#### Projeções Inerciais 2025–2026 (Soja)")
        st.dataframe(
            pd.DataFrame({
                "Fonte": df_prev["fonte"],
                "Ano Projetado": df_prev["ano"],
                "Preço Estimado pela Tendência": df_prev["preco_estimado_tendencia"].apply(fmt_brl),
            }),
            width="stretch",
            hide_index=True,
        )
        st.caption("⚠️ Projeções baseadas apenas na continuidade linear do tempo, sem incorporar choques climáticos, câmbio ou CBOT.")

# ------------------------------------------------------------------------------
# ABA 8: MODELOS PREDITIVOS DA SOJA (FIGURA 1 + MODELO DIRECIONAL LOGÍSTICO)
# ------------------------------------------------------------------------------
with tabs[7]:
    st.markdown("### 🤖 Modelagem Preditiva da Soja: Estimativa de Preço e Direção Mensal (Teste: 2022–2024)")
    render_exp(
        "**Protocolo Experimental (Resumo Expandido IX SIEPE 2026):**\n"
        "- **Modelo de Regressão de Preço:** Relacionou o preço físico nominal DERAL à referência internacional CBOT convertida em R$/60 kg, utilizando **2007–2021 para treinamento** e **2022–2024 para teste independente (36 meses)**.\n"
        "- **Modelo Direcional (Regressão Logística):** Classificou alta ou não alta mensal a partir das variações do mês anterior da **CBOT**, do **dólar** e do **DERAL**. "
        "O período **2019–2021** foi usado como validação interna para selecionar o **corte de probabilidade (0,67)**, mantendo **2022–2024** exclusivamente como teste final."
    )

    # KPIs dos modelos da soja
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        render_kpi("R² no Teste (Preço)", "0,757", "Treino (2007–2021): 0,977")
    with k2:
        render_kpi("MAPE (Preço)", "8,09%", "Teste 2022–2024 (36 meses)")
    with k3:
        render_kpi("MAE & RMSE", "R$ 10,58", "RMSE: R$ 12,35 / 60 kg")
    with k4:
        render_kpi("Acurácia Direcional", "69,44%", "Corte validado = 0,67")
    with k5:
        render_kpi("Acurácia Balanceada", "66,19%", "Sens.: 46,67% · Espec.: 85,71%")
    with k6:
        render_kpi("Ganho s/ Baseline", "+27,78 p.p.", "Baseline majoritário: 41,67%")

    st.write("")
    st.markdown("#### Figura 1 do Resumo Expandido — Preço Observado da Soja no DERAL vs. Preço Estimado pelo Modelo (2022–2024)")
    render_exp(
        "**Figura 1 —** Preço observado da soja no DERAL e preço estimado pelo modelo baseado na referência da CBOT convertida pelo câmbio, "
        "no período de teste de 2022 a 2024. *Fonte: elaboração própria a partir de dados do DERAL, BCB e USDA/ERS.*"
    )

    df_sp_teste = DATA["soja_modelo_preco_teste"].sort_values("data")
    col_fig1, col_err = st.columns([1.45, 1])

    with col_fig1:
        fig_f1 = go.Figure()
        fig_f1.add_trace(
            go.Scatter(
                x=df_sp_teste["data"],
                y=df_sp_teste["preco_estimado_modelo"],
                mode="lines+markers",
                name="Preço estimado pelo modelo",
                line=dict(color=COLORS["Modelo"], width=2.8),
                marker=dict(size=7),
            )
        )
        fig_f1.add_trace(
            go.Scatter(
                x=df_sp_teste["data"],
                y=df_sp_teste["preco_deral_nominal"],
                mode="lines+markers",
                name="Preço observado DERAL",
                line=dict(color=COLORS["Observado_Teste"], width=2.8),
                marker=dict(size=7),
            )
        )
        fig_f1.update_layout(
            xaxis_title="Mês/Ano (Período de Teste Independente: 2022–2024)",
            yaxis_title="Preço da soja (R$/60 kg)",
        )
        st.plotly_chart(apply_plotly_style(fig_f1, height=420), width="stretch")

    with col_err:
        fig_res_m = go.Figure()
        fig_res_m.add_trace(
            go.Bar(
                x=df_sp_teste["data"],
                y=df_sp_teste["erro"],
                name="Erro (Observado - Estimado)",
                marker_color=["#16a34a" if e >= 0 else "#ef4444" for e in df_sp_teste["erro"]],
            )
        )
        fig_res_m.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        fig_res_m.update_layout(
            title="Erro Mensal de Estimativa no Teste (Observado - Estimado em R$/60 kg)",
            xaxis_title="Data (2022–2024)",
            yaxis_title="Erro (R$/60 kg)",
        )
        st.plotly_chart(apply_plotly_style(fig_res_m, height=420), width="stretch")

    st.divider()
    st.markdown("#### Modelo Direcional da Soja (Regressão Logística — Teste 2022–2024)")
    render_exp(
        "No modelo direcional final, o corte de probabilidade selecionado antes do teste foi **0,67**. "
        "A acurácia em 2022–2024 alcançou **69,44%**, enquanto o baseline de classe majoritária atingiu **41,67%**, resultando em ganho de **27,78 pontos percentuais**. "
        "A acurácia balanceada foi **66,19%**, com sensibilidade de **46,67%** e especificidade de **85,71%**. "
        "O resultado mostra maior capacidade para reconhecer meses sem alta do que para identificar todas as altas, devendo ser interpretado como ferramenta analítica de apoio."
    )

    df_sdir = DATA["soja_modelo_dir_teste"].sort_values("data")
    col_sd1, col_sd2 = st.columns([1.45, 1])

    with col_sd1:
        fig_sprob = go.Figure()
        fig_sprob.add_trace(
            go.Scatter(
                x=df_sdir["data"],
                y=df_sdir["probabilidade_alta"],
                mode="lines+markers",
                name="Probabilidade Estimada de Alta",
                line=dict(color=COLORS["Soja"], width=2.4),
                marker=dict(
                    size=9,
                    color=[
                        "#16a34a" if o == p else "#ef4444"
                        for o, p in zip(df_sdir["classe_observada_texto"], df_sdir["classe_prevista_texto"])
                    ],
                    line=dict(width=1, color="#ffffff"),
                ),
            )
        )
        fig_sprob.add_hline(
            y=0.67,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text="Corte validado (2019–2021) = 0,67",
            annotation_position="top left",
        )
        fig_sprob.update_layout(
            title="Probabilidade Mensal de Alta vs. Corte (0,67) — Marcador Verde = Acerto | Vermelho = Erro",
            xaxis_title="Data (2022–2024)",
            yaxis=dict(title="Probabilidade de Alta", range=[0, 1.05]),
        )
        st.plotly_chart(apply_plotly_style(fig_sprob, height=380), width="stretch")

    with col_sd2:
        df_smc = DATA["soja_matriz_conf"]
        pivot_mc = df_smc.pivot(index="observado", columns="previsto", values="quantidade").fillna(0)
        fig_mc = px.imshow(
            pivot_mc,
            text_auto=True,
            color_continuous_scale="Greens",
            labels=dict(x="Classe Prevista", y="Classe Observada", color="Meses"),
            title="Matriz de Confusão da Soja no Teste (2022–2024, n = 36)",
        )
        fig_mc.update_layout(height=380, margin=dict(t=50, l=40, r=40, b=40))
        st.plotly_chart(fig_mc, width="stretch")

    st.markdown("#### Resumo Oficial de Métricas e Tabela de Auditoria no Período de Teste (2022–2024)")
    t_c1, t_c2 = st.columns([1, 2.1])
    with t_c1:
        df_smm = DATA["soja_metricas_modelos"].copy()
        df_smm["valor"] = df_smm["valor"].apply(lambda v: fmt_num(v, 3))
        st.dataframe(
            df_smm.rename(columns={"grupo": "Modelo", "metrica": "Métrica Avaliada", "valor": "Resultado"}),
            width="stretch",
            hide_index=True,
            height=420,
        )
    with t_c2:
        df_aud_soja = pd.DataFrame({
            "Data": df_sdir["data"].str.slice(0, 7),
            "DERAL Obs. (R$)": df_sdir["preco_deral_nominal"].apply(fmt_brl),
            "Modelo Preço (R$)": df_sp_teste["preco_estimado_modelo"].apply(fmt_brl),
            "Erro Abs. (R$)": df_sp_teste["erro_absoluto"].apply(fmt_brl),
            "Erro (%)": df_sp_teste["erro_percentual_absoluto"].apply(fmt_pct),
            "Var. CBOT (t-1)": df_sdir["variacao_cbot_anterior"].apply(fmt_pct),
            "Var. Dólar (t-1)": df_sdir["variacao_dolar_anterior"].apply(fmt_pct),
            "Var. DERAL (t-1)": df_sdir["variacao_deral_anterior"].apply(fmt_pct),
            "Prob. Alta": df_sdir["probabilidade_alta"].apply(lambda v: fmt_num(v, 3)),
            "Observado": df_sdir["classe_observada_texto"],
            "Previsto (0,67)": df_sdir["classe_prevista_texto"],
        })
        st.dataframe(df_aud_soja, width="stretch", hide_index=True, height=420)

# ==============================================================================
# RODAPÉ
# ==============================================================================
st.markdown(
    """
    <div class="footer-box">
        <strong>IX SIEPE — Semana de Integração Ensino, Pesquisa e Extensão (UNICENTRO, 2026)</strong><br>
        Análise dos Preços da Soja no Paraná: Relações com Inflação, Câmbio e Mercado Internacional (2007–2024)<br>
        Fontes de Dados: DERAL/SEAB-PR · CEPEA/ESALQ-USP · IPCA/IBGE · Banco Central do Brasil (BCB) · USDA/ERS (CBOT)
    </div>
    """,
    unsafe_allow_html=True,
)
