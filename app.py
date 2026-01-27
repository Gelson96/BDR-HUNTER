import streamlit as st
import pandas as pd
import requests
import re

# 1. Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Gelson96", layout="wide", page_icon="🚀")

URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"

# --- CSS PARA CENTRALIZAR ---
st.markdown(
    f"""
    <style>
    .centered-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; }}
    .centered-container img {{ width: 400px; margin-bottom: 10px; }}
    h1, h2, h3, .stSubheader {{ text-align: center !important; width: 100%; }}
    </style>
    <div class="centered-container"><img src="{URL_LOGO}"></div>
    """,
    unsafe_allow_html=True
)

st.title("BDR Hunter")
st.subheader("Inteligência de Mercado & Setores Estratégicos")
st.divider()

# --- FUNÇÕES ---
def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    if porte_cod in [1, "01"]: return "PEQUENO (ME)", "Até R$ 360k*", "1-9*"
    elif porte_cod in [3, "03"]: return "PEQUENO (EPP)", "R$ 360k-4,8M*", "10-49*"
    else:
        if cap > 10000000: return "GRANDE", "100M+*", "500+*"
        elif cap > 1000000: return "MÉDIO", "10M-50M*", "100-250*"
        else: return "MÉDIO", "4,8M+*", "50+*"

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                porte, fat, func = processar_inteligencia_premium(d)
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_limpo = limpar_nome_empresa(fantasia)
                cnae_desc = d.get('cnae_fiscal_descricao', 'Não Informado')
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "Atividade Principal (CNAE)": cnae_desc,
                    "Porte": porte,
                    "Faturamento Est.*": fat,
                    "Funcionários Est.*": func,
                    "Capital Social": f"R$ {float(d.get('capital_social',0)):,.2f}",
                    "Cidade/UF": f"{d.get('municipio', '')}/{d.get('uf', '')}",
                    "LinkedIn": f"https://www.linkedin.com/search/results/people/?keywords={nome_limpo.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos%20OR%20Compras)",
                    "WhatsApp": f"https://www.google.com.br/search?q=whatsapp+telefone+setor+compras+{(nome_limpo + ' ' + d.get('municipio', '')).replace(' ', '+')}",
                    "Endereço": f"{d.get('logradouro', '')}, {d.get('numero', '')} - {d.get('municipio', '')}/{d.get('uf', '')}",
                    "Nome Busca": nome_limpo
                })
        except: continue
        progresso.progress((i + 1) / len(lista_cnpjs))
    return pd.DataFrame(dados_finais)

# --- INTERFACE ---
col_in1, col_in2, col_in3 = st.columns([1, 4, 1])
with col_in2:
    entrada = st.text_area("Insira os CNPJs:", height=150)
    iniciar = st.button("🚀 Iniciar Análise Completa", use_container_width=True)

if iniciar:
    if entrada:
        cnpjs = re.findall(r'\d+', entrada)
        if cnpjs:
            st.session_state.df_resultado = processar_lista(cnpjs)
        else: st.error("Nenhum CNPJ encontrado.")

if 'df_resultado' in st.session_state and not st.session_state.df_resultado.empty:
    df = st.session_state.df_resultado
    st.success(f"Pronto! {len(df)} empresas mapeadas.")
    
    # Exibe a tabela com o CNAE agora!
    st.dataframe(
        df.drop(columns=['Endereço', 'Nome Busca']), 
        column_config={
            "LinkedIn": st.column_config.LinkColumn("Pessoas"), 
            "WhatsApp": st.column_config.LinkColumn("Busca Zap")
        }, 
        hide_index=True, use_container_width=True
    )
    
    st.download_button("📥 Baixar Excel Completo", data=df.to_csv(index=False).encode('utf-8-sig'), file_name="prospeccao_premium.csv", use_container_width=True)

    # --- SEÇÃO DE MAPA ---
    st.divider()
    st.subheader("📍 Investigação Visual (Maps)")
    emp_sel = st.selectbox("Selecione a empresa:", df["Empresa"].tolist())
    if emp_sel:
        row = df[df["Empresa"] == emp_sel].iloc[0]
        query = f"{row['Nome Busca']} {row['Endereço']}".replace(" ", "+")
        st.info(f"📍 **Setor:** {row['Atividade Principal (CNAE)']} | **Endereço:** {row['Endereço']}")
        st.components.v1.iframe(f"https://www.google.com/maps?q={query}&output=embed", height=450)
