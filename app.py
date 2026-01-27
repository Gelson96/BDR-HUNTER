import streamlit as st
import pandas as pd
import requests
import re

st.set_page_config(page_title="BDR Hunter Pro", layout="wide")

st.title("🤖 BDR Hunter - Inteligência de Mercado")
st.markdown("### Extração de CNPJ com Porte, Capital Social e Links de Prospecção")

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

def processar_lista(lista_cnpjs):
    dados_finais = []
    progresso = st.progress(0)
    
    # Dicionário de Portes atualizado e mais robusto
    portes_map = {
        1: "ME (Microempresa)",
        3: "EPP (Empresa de Pequeno Porte)",
        5: "Demais (Médio/Grande Porte)",
        "01": "ME (Microempresa)",
        "03": "EPP (Empresa de Pequeno Porte)",
        "05": "Demais (Médio/Grande Porte)"
    }

    for i, cnpj_bruto in enumerate(lista_cnpjs):
        cnpj = "".join(filter(str.isdigit, str(cnpj_bruto))).zfill(14)
        try:
            res = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            if res.status_code == 200:
                d = res.json()
                fantasia = d.get('nome_fantasia') or d.get('razao_social')
                nome_busca = limpar_nome_empresa(fantasia)
                
                # Tradução do Porte com fallback para o valor bruto
                porte_valor = d.get('porte')
                porte_texto = portes_map.get(porte_valor, f"Porte Código: {porte_valor}")
                
                # Links Inteligentes
                l_link = f"https://www.linkedin.com/search/results/people/?keywords={nome_busca.replace(' ', '%20')}%20(Comprador%20OR%20Suprimentos)"
                g_link = f"https://www.google.com.br/search?q=telefone+whatsapp+compras+{nome_busca.replace(' ', '+')}"
                
                dados_finais.append({
                    "Empresa": fantasia,
                    "Porte": porte_texto,
                    "Capital Social": formatar_moeda(d.get('capital_social')),
                    "LinkedIn": l_link,
                    "WhatsApp (Busca)": g_link,
                    "Cidade/UF": f"{d.get('municipio')}/{d.get('uf')}",
                    "Atividade Principal": d.get('cnae_fiscal_descricao', 'N/D')
                })
        except:
            continue
        progresso.progress((i + 1) / len(lista_cnpjs))
        
    return pd.DataFrame(dados_finais)

entrada = st.text_area("Cole os CNPJs aqui:", height=150)

if st.button("🚀 Gerar Inteligência de Vendas"):
    if entrada:
        cnpjs = re.findall(r'\d+', entrada)
        df = processar_lista(cnpjs)
        
        if not df.empty:
            st.success("Dados extraídos com sucesso!")
            st.dataframe(
                df,
                column_config={
                    "LinkedIn": st.column_config.LinkColumn("Pessoas"),
                    "WhatsApp (Busca)": st.column_config.LinkColumn("Contatos")
                },
                hide_index=True
            )
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Baixar Relatório Completo", data=csv, file_name="inteligencia_bdr.csv")
