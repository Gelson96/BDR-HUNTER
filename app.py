import streamlit as st
import pandas as pd
import requests
import re
import time

# Configuração da página
st.set_page_config(page_title="BDR Hunter Bot v4.0", layout="wide")

st.title("🤖 BDR Hunter - Localizador de Compradores")
st.markdown("### Cole os CNPJs para gerar links diretos de prospecção")

# Função para limpar o nome da empresa e melhorar a busca
def limpar_nome_empresa(nome):
    if not nome: return ""
    # Remove termos que "sujam" a busca no LinkedIn/Google
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    total = len(lista_cnpjs)
    
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        # Limpa o CNPJ para deixar apenas números
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        
        try:
            # Consulta API gratuita BrasilAPI
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_busca = limpar_nome_empresa(fantasia)
                
                # Links Inteligentes de Prospecção
                # Busca por Cargos de Decisão no LinkedIn
                cargos = "(Comprador OR Suprimentos OR Procurement OR Purchasing)"
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_busca.replace(' ', '%20')}%20{cargos}"
                
                # Busca profunda por Telefone/WhatsApp no Google
                g_link = f"https://www.google.com.br/search?q=telefone+whatsapp+setor+compras+{nome_busca.replace(' ', '+')}"
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "LinkedIn (Achar Comprador)": l_link,
                    "Google (WhatsApp/Tel Real)": g_link,
                    "Telefone (Receita)": d.get('ddd_telefone_1', 'N/D'),
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}"
                })
        except Exception as e:
            continue
            
        # Atualiza a barra de progresso
        progresso.progress((i + 1) / total)
        
    return pd.DataFrame(dados_finais)

# Área de entrada de dados
entrada = st.text_area("Cole aqui os CNPJs (um por linha ou separados por vírgula):", height=200)

if st.button("🚀 Gerar Lista de Prospecção"):
    if entrada:
        # Extrai todos os números que pareçam CNPJs da entrada
        cnpjs_encontrados = re.findall(r'\d+', entrada)
        
        if cnpjs_encontrados:
            df_resultado = processar_lista(cnpjs_encontrados)
            
            if not df_resultado.empty:
                st.success(f"Foram encontradas {len(df_resultado)} empresas!")
                
                # Exibe a tabela com links clicáveis
                st.dataframe(
                    df_resultado,
                    column_config={
                        "LinkedIn (Achar Comprador)": st.column_config.LinkColumn("Abrir LinkedIn"),
                        "Google (WhatsApp/Tel Real)": st.column_config.LinkColumn("Buscar no Google")
                    },
                    hide_index=True
                )
                
                # Botão para baixar Excel
                csv = df_resultado.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Baixar Planilha para Excel",
                    data=csv,
                    file_name="prospeccao_bdr.csv",
                    mime="text/csv"
                )
        else:
            st.error("Nenhum CNPJ válido foi identificado no texto colado.")
    else:
        st.warning("Por favor, cole os CNPJs antes de clicar no botão.")
