import streamlit as st
import pandas as pd
import requests
import re

st.set_page_config(page_title="BDR Hunter Pro", layout="wide")

st.title("🤖 BDR Hunter - Inteligência de Mercado")
st.markdown("### Classificação por Porte (Pequena, Média ou Grande)")

def limpar_nome_empresa(nome):
    if not nome: return ""
    termos = r'\b(LTDA|S\.?A|S/A|INDUSTRIA|COMERCIO|EIRELI|ME|EPP|CONSTRUTORA|SERVICOS|BRASIL|MATRIZ)\b'
    nome_limpo = re.sub(termos, '', nome, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', nome_limpo).strip()

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except:
        return "N/D"

def classificar_porte_detalhado(dado_api):
    porte_cod = str(dado_api.get('porte', ''))
    capital = float(dado_api.get('capital_social', 0))
    
    # Se for código 01 ou 03, é obrigatoriamente pequena (ME/EPP)
    if porte_cod in ["01", "1", "03", "3"]:
        return "PEQUENA EMPRESA"
    
    # Se for código 05 (Demais), filtramos pelo Capital Social para diferenciar Média de Grande
    if porte_cod in ["05", "5"]:
        if capital >= 10000000: # Exemplo: Capital acima de 10 milhões
            return "GRANDE EMPRESA"
        else:
            return "MÉDIA EMPRESA"
            
    return "NÃO INFORMADO"

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    
    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_busca = limpar_nome_empresa(fantasia)
                
                # Inteligência de Negócio
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_busca.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos)"
                g_link = f"https://www.google.com.br/search?q=telefone+whatsapp+compras+{nome_busca.replace(' ', '+')}"
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "CLASSIFICAÇÃO": classificar_porte_detalhado(d),
                    "Capital Social": formatar_moeda(d.get('capital_social')),
                    "LinkedIn": l_link,
                    "WhatsApp (Busca)": g_link,
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}",
                    "Atividade": d.get('cnae_fiscal_descricao', 'N/D')
                })
        except:
            continue
        progresso.progress((i + 1) / len(lista_cnpjs))
        
    return pd.DataFrame(dados_finais)

# --- INTERFACE ---
entrada = st.text_area("Cole os CNPJs aqui:", height=150)

if st.button("🚀 Gerar Inteligência de Vendas"):
    if entrada:
        cnpjs = re.findall(r'\d+', entrada)
        df = processar_lista(cnpjs)
        
        if not df.empty:
            st.success("Busca Finalizada!")
            st.dataframe(
                df,
                column_config={
                    "LinkedIn": st.column_config.LinkColumn("Pessoas"),
                    "WhatsApp (Busca)": st.column_config.LinkColumn("Google")
                },
                hide_index=True
            )
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Baixar Planilha", data=csv, file_name="leads_classificados.csv")
