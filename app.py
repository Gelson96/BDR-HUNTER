import streamlit as st
import pandas as pd
import requests
import re
import os

# Configuração da Página
st.set_page_config(page_title="BDR Hunter Pro | Inteligência", layout="wide", page_icon="🚀")

# LINKS E ARQUIVOS DE IMAGEM
URL_LOGO = "https://static.wixstatic.com/media/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png/v1/fill/w_232,h_67,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/82a786_45084cbd16f7470993ad3768af4e8ef4~mv2.png"
ARQUIVO_ASSINATURA = "Captura de tela 2026-01-27 143218.png" # Nome exato do arquivo que você subiu no GitHub

# --- BARRA LATERAL ---
with st.sidebar:
    st.image(URL_LOGO, use_container_width=True)
    st.divider()
    
    st.markdown("### 🛠️ Configurações")
    st.info("Ferramenta de Inteligência de Mercado e Extração de Decisores.")
    
    st.divider()
    
    # Tenta carregar a assinatura do GitHub
    st.markdown("### 📧 Contato")
    if os.path.exists(ARQUIVO_ASSINATURA):
        st.image(ARQUIVO_ASSINATURA, use_container_width=True)
    else:
        st.warning("Suba o arquivo 'assinatura.png' para o GitHub para visualizá-lo aqui.")

# --- CORPO PRINCIPAL ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image(URL_LOGO, width=150)
with col2:
    st.title("BDR Hunter - Unificado")
    st.subheader("Inteligência Premium de Dados e Prospecção")

st.divider()

# --- FUNÇÕES DE LÓGICA (MANTIDAS) ---
def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_inteligencia_premium(d):
    porte_cod = d.get('porte')
    cap = d.get('capital_social', 0)
    if porte_cod in [1, "01"]:
        porte, faturamento, funcionarios = "PEQUENO (ME)", "Até R$ 360.000*", "1 a 9*"
    elif porte_cod in [3, "03"]:
        porte, faturamento, funcionarios = "PEQUENO (EPP)", "R$ 360k a R$ 4,8 Milhões*", "10 a 49*"
    else:
        porte = "MÉDIO OU GRANDE"
        if cap > 10000000:
            faturamento, funcionarios = "Acima de R$ 100 Milhões*", "500+*"
        elif cap > 1000000:
            faturamento, funcionarios = "R$ 10M a R$ 50 Milhões*", "100 a 250*"
        else:
            faturamento, funcionarios = "Acima de R$ 4,8 Milhões*", "50+*"
    return porte, faturamento, funcionarios

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
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_limpo.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos%20OR%20Compras)"
                g_link = f"https://www.google.com.br/search?q=whatsapp+telefone+setor+compras+{nome_limpo.replace(' ', '+')}"
                dados_finais.append({
                    "Empresa": fantasia,
                    "Porte Real": porte,
                    "Faturamento Est.*": fat,
                    "Funcionários Est.*": func,
                    "LinkedIn": l_link,
                    "WhatsApp (Busca)": g_link,
                    "Capital Social": f"R$ {float(d.get('capital_social',0)):,.2f}"
                })
        except: continue
        progresso.progress((i + 1) / len(lista_cnpjs))
    return pd.DataFrame(dados_finais)

entrada = st.text_area("Insira os CNPJs para análise:", height=150)

if st.button("🚀 Gerar Inteligência Premium"):
    if entrada:
        cnpjs = re.findall(r'\d+', entrada)
        if cnpjs:
            df = processar_lista(cnpjs)
            if not df.empty:
                st.success(f"Sucesso! {len(df)} leads analisados.")
                st.dataframe(df, column_config={"LinkedIn": st.column_config.LinkColumn("Decisores"), "WhatsApp (Busca)": st.column_config.LinkColumn("Contatos")}, hide_index=True)
                st.download_button("📥 Baixar Relatório", df.to_csv(index=False).encode('utf-8-sig'), "prospeccao_bdr.csv")

