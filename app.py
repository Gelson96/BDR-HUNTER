import streamlit as st
import pandas as pd
import requests
import re

st.set_page_config(page_title="BDR Hunter Pro", layout="wide")

# Barra lateral para colar a chave que você acabou de criar
with st.sidebar:
    st.title("Configurações")
    apollo_api_key = st.text_input("Cole sua API Key do Apollo aqui", type="password")
    st.info("A chave que você criou no Apollo liberará os telefones diretos.")

def buscar_decisor_apollo(dominio, empresa, api_key):
    url = "https://api.apollo.io/v1/people/match"
    payload = {
        "api_key": api_key,
        "domain": dominio,
        "organization_name": empresa,
        "titles": ["comprador", "suprimentos", "procurement", "purchasing", "compras"]
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            person = response.json().get('person', {})
            return {
                "Nome": person.get('name', 'Não encontrado'),
                "Cargo": person.get('title', 'N/A'),
                "Celular": person.get('sanitized_phone', 'N/D'),
                "E-mail": person.get('email', 'N/D')
            }
    except:
        pass
    return {"Nome": "Não encontrado", "Cargo": "N/A", "Celular": "N/D", "E-mail": "N/D"}

st.title("🤖 BDR Hunter - Localizador de Compradores")
st.markdown("Insira os CNPJs para buscar o contato direto do decisor via Apollo.")

txt_cnpjs = st.text_area("Cole os CNPJs (um por linha):", height=150)

if st.button("🚀 Buscar Decisores e Telefones"):
    if not apollo_api_key:
        st.error("Por favor, insira sua API Key do Apollo na barra lateral.")
    elif not txt_cnpjs:
        st.warning("Insira pelo menos um CNPJ.")
    else:
        cnpjs = re.findall(r'\d+', txt_cnpjs)
        lista_final = []
        
        progresso = st.progress(0)
        for i, cnpj in enumerate(cnpjs):
            # Busca domínio na BrasilAPI (via e-mail de registro)
            try:
                res_br = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}").json()
                razao = res_br.get('razao_social', 'N/A')
                email_reg = res_br.get('email', '')
                dominio = email_reg.split('@')[-1] if '@' in email_reg else ""
                
                # Busca no Apollo
                decisor = buscar_decisor_apollo(dominio, razao, apollo_api_key)
                
                lista_final.append({
                    "Empresa": razao,
                    "Comprador": decisor['Nome'],
                    "Cargo": decisor['Cargo'],
                    "WhatsApp/Celular": decisor['Celular'],
                    "E-mail Direto": decisor['E-mail']
                })
            except:
                continue
            progresso.progress((i + 1) / len(cnpjs))
            
        df = pd.DataFrame(lista_final)
        st.success("Busca concluída!")
        st.dataframe(df)
        
        # Botão para baixar o resultado
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Planilha para Prospecção", data=csv, file_name="leads_apollo.csv", mime="text/csv")
