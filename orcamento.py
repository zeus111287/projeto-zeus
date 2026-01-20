import streamlit as st
import pandas as pd
import plotly.express as px
import feedparser 
import json
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Projeto Zeus - Inteligência Financeira", page_icon="🐾", layout="wide")

# 2. PERSISTÊNCIA DE DADOS
NOME_ARQUIVO = "dados_zeus.json"

def salvar_dados():
    dados_para_salvar = {
        "receitas": st.session_state.receitas_por_mes,
        "cofrinho": st.session_state.cofrinho_real,
        "mural": st.session_state.mural_conversa,
        "lembretes": st.session_state.lista_lembretes,
        "meta_cofrinho": st.session_state.meta_cofrinho,
        "gastos": {mes: df.to_dict() for mes, df in st.session_state.dados_mensais.items()}
    }
    with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

def carregar_dados():
    if os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
            st.session_state.receitas_por_mes = dados["receitas"]
            st.session_state.cofrinho_real = dados["cofrinho"]
            st.session_state.mural_conversa = dados["mural"]
            st.session_state.lista_lembretes = dados["lembretes"]
            st.session_state.meta_cofrinho = dados.get("meta_cofrinho", 1000.0)
            st.session_state.dados_mensais = {mes: pd.DataFrame(df_dict) for mes, df_dict in dados["gastos"].items()}
        return True
    return False

# 3. ESTILO CSS
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    .mural-batepapo { background-color: #fff9c4; padding: 15px; border-radius: 10px; border: 1px solid #fbc02d; color: #333; }
    .lembrete-item { background-color: #ffffff; padding: 10px; border-radius: 8px; border-left: 5px solid #ff5722; margin-bottom: 8px; font-weight: bold; color: #d84315; }
    .reserva-card { padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 20px; text-align: center; font-size: 1.2em; border: 1px solid #ccc; }
    .noticia-item { background-color: #ffffff; padding: 8px; border-radius: 5px; border-left: 3px solid #2196f3; margin-bottom: 8px; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# 4. INICIALIZAÇÃO
meses_ano = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

if 'dados_mensais' not in st.session_state:
    if not carregar_dados():
        st.session_state.dados_mensais = {mes: pd.DataFrame({"Categoria": ["Outros"], "Item": ["Exemplo"], "Valor": [0.0]}) for mes in meses_ano}
        st.session_state.cofrinho_real = {mes: 0.0 for mes in meses_ano}
        st.session_state.receitas_por_mes = {mes: 0.0 for mes in meses_ano}
        st.session_state.mural_conversa = "🐾 Bate-papo da família Zeus!"
        st.session_state.lista_lembretes = "COMPRAR GÁS"
        st.session_state.meta_cofrinho = 1000.0

def fmt_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.title("🐾 Estratégia Zeus")
    st.subheader("🌐 Economia")
    try:
        feed = feedparser.parse("https://g1.globo.com/rss/g1/economia/")
        for n in feed.entries[:3]:
            st.markdown(f'<div class="noticia-item"><a href="{n.link}" target="_blank" style="text-decoration:none; color:#0d47a1;">{n.title}</a></div>', unsafe_allow_html=True)
    except: st.info("Notícias off-line")

    st.markdown("---")
    mes_sel = st.selectbox("📅 Mês:", meses_ano)
    st.session_state.receitas_por_mes[mes_sel] = st.number_input(f"Receita (R$):", min_value=0.0, format="%.2f", value=float(st.session_state.receitas_por_mes[mes_sel]))
    
    st.markdown("---")
    st.header("🐷 Cofrinho")
    st.session_state.meta_cofrinho = st.number_input("Meta (R$):", min_value=0.0, value=float(st.session_state.meta_cofrinho), format="%.2f")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ DEP"): st.session_state.op = "dep"
    with c2:
        if st.button("➖ RES"): st.session_state.op = "res"
    v_op = st.number_input("Valor da Op.:", min_value=0.0, format="%.2f")
    if st.button("🚀 Confirmar"):
        if st.session_state.get('op') == "dep": st.session_state.cofrinho_real[mes_sel] += v_op
        elif st.session_state.get('op') == "res" and st.session_state.cofrinho_real[mes_sel] >= v_op:
            st.session_state.cofrinho_real[mes_sel] -= v_op
        salvar_dados()
        st.rerun()

# --- 6. PAINEL CENTRAL ---
st.title(f"📊 Dashboard Zeus - {mes_sel}")

total_rec_mes = st.session_state.receitas_por_mes[mes_sel]
total_gas_mes = st.session_state.dados_mensais[mes_sel]["Valor"].sum()
total_cof_mes = st.session_state.cofrinho_real[mes_sel]
total_cof_acumulado = sum(st.session_state.cofrinho_real.values())
reserva_mes = total_rec_mes - total_gas_mes - total_cof_mes

m1, m2, m3, m4 = st.columns(4)
m1.metric("Entrada", fmt_moeda(total_rec_mes))
m2.metric("Saída", fmt_moeda(total_gas_mes))
m3.metric("No Cofrinho", fmt_moeda(total_cof_mes))
m4.metric("Saldo Restante", fmt_moeda(reserva_mes))

if reserva_mes >= 0:
    st.markdown(f'<div style="background-color:#e8f5e9; color:#2e7d32;" class="reserva-card">✅ Saldo do Mês: {fmt_moeda(reserva_mes)}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="background-color:#ffebee; color:#c62828;" class="reserva-card">🚨 Atenção! Déficit: {fmt_moeda(reserva_mes)}</div>', unsafe_allow_html=True)

st.subheader(f"🎯 Meta Geral (Guardado: {fmt_moeda(total_cof_acumulado)})")
progresso = min(total_cof_acumulado / st.session_state.meta_cofrinho, 1.0) if st.session_state.meta_cofrinho > 0 else 0
st.progress(progresso)
st.write(f"Você já alcançou **{progresso*100:.1f}%** da meta de **{fmt_moeda(st.session_state.meta_cofrinho)}**")

# --- 7. MURAL E LEMBRETES ---
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("💬 Bate-papo")
    st.session_state.mural_conversa = st.text_area("Mensagem:", value=st.session_state.mural_conversa, height=70, key="chat")
    st.markdown(f'<div class="mural-batepapo">{st.session_state.mural_conversa}</div>', unsafe_allow_html=True)
with col_b:
    st.subheader("🚨 Lembretes")
    st.session_state.lista_lembretes = st.text_area("Lembrete:", value=st.session_state.lista_lembretes, height=70, key="rem")
    for item in st.session_state.lista_lembretes.split('\n'):
        if item.strip(): st.markdown(f'<div class="lembrete-item">⚠️ {item.upper()}</div>', unsafe_allow_html=True)

# --- 8. ANALYTICS LADO A LADO ---
st.markdown("---")
col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    st.subheader("📈 Histórico")
    dados_comp = []
    for m in meses_ano:
        dados_comp.append({"Mês": m, "Tipo": "Receita", "Valor": st.session_state.receitas_por_mes[m]})
        dados_comp.append({"Mês": m, "Tipo": "Gasto", "Valor": st.session_state.dados_mensais[m]["Valor"].sum()})
    df_comp = pd.DataFrame(dados_comp)
    fig_comp = px.bar(df_comp, x="Mês", y="Valor", color="Tipo", barmode="group", color_discrete_map={"Receita": "#4caf50", "Gasto": "#f44336"})
    st.plotly_chart(fig_comp, use_container_width=True)
with col_graf2:
    st.subheader(f"🍕 Divisão de Gastos")
    fig_pizza = px.pie(st.session_state.dados_mensais[mes_sel], values='Valor', names='Categoria', hole=0.4)
    st.plotly_chart(fig_pizza, use_container_width=True)

# --- 9. TABELA DETALHADA COM FORMATAÇÃO R$ ---
st.markdown("---")
st.subheader(f"📝 Lançamentos - {mes_sel}")
colunas_config = {
    "Valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
}
df_ed = st.data_editor(st.session_state.dados_mensais[mes_sel], column_config=colunas_config, num_rows="dynamic", use_container_width=True)

if st.button("💾 SALVAR TUDO"):
    st.session_state.dados_mensais[mes_sel] = df_ed
    salvar_dados()
    st.success("Tudo salvo com sucesso!")
    st.rerun()