import streamlit as st
import altair as alt
import pandas as pd
import io

# --- Lógica Central de Cálculo Financeiro ---
def calcular_dre_e_pe(receita_bruta, custos_variaveis, custos_fixos):
    """Calcula a DRE e o Ponto de Equilíbrio."""
    
    # 1. Validação de Inputs
    if receita_bruta < 0 or custos_variaveis < 0 or custos_fixos < 0:
        st.error("Erro de Validação: Nenhum valor pode ser negativo.")
        return None, None

    if custos_variaveis > receita_bruta:
        st.warning("Atenção: Custos Variáveis são maiores que a Receita Bruta. A Margem de Contribuição será negativa.")

    # 2. Cálculos da DRE
    margem_contribuicao = receita_bruta - custos_variaveis
    lucro_operacional = margem_contribuicao - custos_fixos

    # 3. Cálculo do Ponto de Equilíbrio (PE)
    if receita_bruta > 0:
        margem_contribuicao_percentual = margem_contribuicao / receita_bruta
        
        # PE em Valor (Receita necessária para cobrir Custos Fixos)
        if margem_contribuicao_percentual > 0:
            pe_valor = custos_fixos / margem_contribuicao_percentual
            
            # PE em % da Receita Atual
            pe_percentual = (pe_valor / receita_bruta) * 100
        else:
            pe_valor = float('inf')
            pe_percentual = float('inf')
    else:
        margem_contribuicao_percentual = 0
        pe_valor = float('inf')
        pe_percentual = float('inf')

    # Estrutura da DRE para exibição
    dre_data = {
        "Descrição": ["Receita Bruta", "(-) Custos Variáveis", "(=) Margem de Contribuição", "(-) Custos Fixos", "(=) Lucro Operacional"],
        "Valor": [receita_bruta, -custos_variaveis, margem_contribuicao, -custos_fixos, lucro_operacional]
    }
    df_dre = pd.DataFrame(dre_data)

    # Estrutura dos Indicadores
    indicadores = {
        "margem_contribuicao": margem_contribuicao,
        "lucro_operacional": lucro_operacional,
        "margem_contribuicao_percentual": margem_contribuicao_percentual,
        "pe_valor": pe_valor,
        "pe_percentual": pe_percentual
    }

    return df_dre, indicadores

# --- Interface Streamlit (Estrutura Inicial) ---
st.set_page_config(
    page_title="App de Gestão Financeira",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Aplicativo de Gestão Financeira")
st.markdown("Insira seus dados para calcular a DRE, Ponto de Equilíbrio e simular cenários.")

# Sidebar para Inputs
st.sidebar.header("Dados Financeiros Atuais")

# Inputs com validação implícita (Streamlit lida com tipos)
receita_bruta = st.sidebar.number_input("Receita Bruta (R$)", min_value=0.0, value=100000.0, step=1000.0)
custos_variaveis = st.sidebar.number_input("Custos Variáveis (R$)", min_value=0.0, value=40000.0, step=1000.0)
custos_fixos = st.sidebar.number_input("Custos Fixos (R$)", min_value=0.0, value=30000.0, step=1000.0)

# Colunas para exibir resultados
col1, col2 = st.columns(2)

df_dre, indicadores = calcular_dre_e_pe(receita_bruta, custos_variaveis, custos_fixos)

if df_dre is not None:
    
    # Exibição da DRE
    with col1:
        st.header("Demonstração do Resultado (DRE)")
        # Formatação para moeda
        df_dre_formatado = df_dre.copy()
        df_dre_formatado['Valor'] = df_dre_formatado['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.table(df_dre_formatado)

    # Exibição dos Indicadores (KPIs)
    with col2:
        st.header("Indicadores Chave (KPIs)")
        
        mc_perc = indicadores['margem_contribuicao_percentual'] * 100
        pe_perc = indicadores['pe_percentual']
        
        # Alerta de Liquidez (Exemplo simples: Lucro Operacional > 0)
        if indicadores['lucro_operacional'] > 0:
            alerta_liquidez = "🟢 Lucro Positivo"
            alerta_cor = "green"
        elif indicadores['lucro_operacional'] == 0:
            alerta_liquidez = "🟡 Ponto de Equilíbrio Atingido"
            alerta_cor = "orange"
        else:
            alerta_liquidez = "🔴 Prejuízo Operacional"
            alerta_cor = "red"

        st.metric(label="Margem de Contribuição (%)", value=f"{mc_perc:,.2f}%")
        st.metric(label="Lucro Operacional (R$)", value=f"R$ {indicadores['lucro_operacional']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric(label="Alerta de Liquidez", value=alerta_liquidez)
        
        # Ponto de Equilíbrio em % da Receita
        if pe_perc != float('inf'):
            st.metric(label="Ponto de Equilíbrio em % da Receita", value=f"{pe_perc:,.2f}%")
            if pe_perc > 100:
                st.warning("O Ponto de Equilíbrio está acima de 100% da Receita Atual. A empresa está operando no prejuízo.")
            elif pe_perc > 80:
                st.info("O Ponto de Equilíbrio está alto. Margem de segurança baixa.")
            else:
                st.success("O Ponto de Equilíbrio está saudável.")
        else:
            st.metric(label="Ponto de Equilíbrio em % da Receita", value="Não Calculável")
            st.error("Margem de Contribuição não positiva. Impossível atingir o Ponto de Equilíbrio.")

# --- Gráfico DRE ---
st.header("Gráfico DRE")

# Preparar dados para o gráfico (Waterfall Chart simplificado)
data_grafico = {
    "Item": ["Receita Bruta", "Custos Variáveis", "Margem de Contribuição", "Custos Fixos", "Lucro Operacional"],
    "Valor": [receita_bruta, -custos_variaveis, indicadores['margem_contribuicao'], -custos_fixos, indicadores['lucro_operacional']],
    "Tipo": ["Receita", "Custo", "Margem", "Custo", "Lucro"]
}
df_grafico = pd.DataFrame(data_grafico)

# Cálculo da base para o gráfico (para o waterfall)
df_grafico['start'] = df_grafico['Valor'].cumsum().shift(1).fillna(0)
df_grafico['end'] = df_grafico['start'] + df_grafico['Valor']
df_grafico['base'] = df_grafico[['start', 'end']].min(axis=1)
df_grafico['height'] = df_grafico['end'] - df_grafico['start']

# Definir cores
color_scale = alt.Scale(domain=['Receita', 'Custo', 'Margem', 'Lucro'],
                        range=['#4CAF50', '#F44336', '#FFC107', '#2196F3'])

chart = alt.Chart(df_grafico).mark_bar().encode(
    x=alt.X('Item:N', sort=None),
    y=alt.Y('base:Q', title="Valor (R$)"),
    y2='end:Q',
    color=alt.Color('Tipo:N', scale=color_scale),
    tooltip=['Item', 'Valor', 'Tipo']
).properties(
    title="Demonstração do Resultado (DRE) - Visual"
)

# Adicionar rótulos (valores visíveis)
text = chart.mark_text(
    align='center',
    baseline='middle',
    dy=-10 # Deslocamento vertical
).encode(
    text=alt.Text('end:Q', format=',.2f'),
    color=alt.value('black')
)

st.altair_chart(chart + text, use_container_width=True)

# --- Exportação para Excel ---
st.header("Exportação de Dados")

def to_excel(df_dre, indicadores):
    """Cria um arquivo Excel em memória com a DRE e o Resumo."""
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # DRE
    df_dre.to_excel(writer, sheet_name='DRE', index=False)
    
    # Resumo/Indicadores
    resumo_data = {
        "Indicador": ["Receita Bruta", "Custos Variáveis", "Custos Fixos", "Margem de Contribuição (%)", "Lucro Operacional", "Ponto de Equilíbrio em % da Receita"],
        "Valor": [
            receita_bruta, 
            custos_variaveis, 
            custos_fixos, 
            indicadores['margem_contribuicao_percentual'] * 100, 
            indicadores['lucro_operacional'], 
            indicadores['pe_percentual'] if indicadores['pe_percentual'] != float('inf') else "Não Calculável"
        ]
    }
    df_resumo = pd.DataFrame(resumo_data)
    df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
    
    writer.close()
    processed_data = output.getvalue()
    return processed_data

if df_dre is not None:
    excel_data = to_excel(df_dre, indicadores)
    st.download_button(
        label="📥 Baixar Resumo e DRE (Excel)",
        data=excel_data,
        file_name='relatorio_financeiro.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# --- Simulação de Cenários e Análise de Sensibilidade ---
st.header("Simulação de Cenários e Análise de Sensibilidade")

with st.expander("Simulação de Cenários (Otimista/Pessimista)"):
    st.markdown("Teste o impacto de um aumento de receita e/ou redução de custos.")
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    
    perc_aumento_receita = col_sim1.slider("Aumento de Receita (%)", min_value=-50, max_value=50, value=10, step=5)
    perc_reducao_cv = col_sim2.slider("Redução de Custos Variáveis (%)", min_value=0, max_value=50, value=5, step=5)
    perc_reducao_cf = col_sim3.slider("Redução de Custos Fixos (%)", min_value=0, max_value=50, value=5, step=5)
    
    # Cálculo do Cenário Simulado
    receita_simulada = receita_bruta * (1 + perc_aumento_receita / 100)
    cv_simulado = custos_variaveis * (1 - perc_reducao_cv / 100)
    cf_simulado = custos_fixos * (1 - perc_reducao_cf / 100)
    
    df_dre_sim, indicadores_sim = calcular_dre_e_pe(receita_simulada, cv_simulado, cf_simulado)
    
    if df_dre_sim is not None:
        lucro_simulado = indicadores_sim['lucro_operacional']
        
        st.subheader("Resultado da Simulação")
        
        col_res1, col_res2 = st.columns(2)
        
        # Comparação com o cenário atual
        delta_lucro = lucro_simulado - indicadores['lucro_operacional']
        
        col_res1.metric(
            label="Lucro Operacional Simulado (R$)", 
            value=f"R$ {lucro_simulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            delta=f"R$ {delta_lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        pe_perc_sim = indicadores_sim['pe_percentual']
        if pe_perc_sim != float('inf'):
            col_res2.metric(
                label="Ponto de Equilíbrio Simulado (%)", 
                value=f"{pe_perc_sim:,.2f}%"
            )
        else:
            col_res2.metric(label="Ponto de Equilíbrio Simulado (%)", value="Não Calculável")
            
        st.dataframe(df_dre_sim, hide_index=True)

with st.expander("Análise de Sensibilidade (Aumento de 10% nos Custos Fixos)"):
    st.markdown("Avalie o impacto de um aumento de 10% nos Custos Fixos (Cenário de Risco).")
    
    # Cenário de Sensibilidade
    cf_sensibilidade = custos_fixos * 1.10
    
    df_dre_sens, indicadores_sens = calcular_dre_e_pe(receita_bruta, custos_variaveis, cf_sensibilidade)
    
    if df_dre_sens is not None:
        lucro_sensibilidade = indicadores_sens['lucro_operacional']
        
        col_sens1, col_sens2 = st.columns(2)
        
        # Comparação com o cenário atual
        delta_lucro_sens = lucro_sensibilidade - indicadores['lucro_operacional']
        
        col_sens1.metric(
            label="Lucro Operacional (Custo Fixo +10%)", 
            value=f"R$ {lucro_sensibilidade:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            delta=f"R$ {delta_lucro_sens:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        pe_perc_sens = indicadores_sens['pe_percentual']
        if pe_perc_sens != float('inf'):
            col_sens2.metric(
                label="Ponto de Equilíbrio (%)", 
                value=f"{pe_perc_sens:,.2f}%"
            )
        else:
            col_sens2.metric(label="Ponto de Equilíbrio (%)", value="Não Calculável")
            
        if lucro_sensibilidade < 0:
            st.error("Alerta de Risco: O aumento de 10% nos Custos Fixos leva a um prejuízo operacional.")
        elif delta_lucro_sens < 0:
            st.warning("Aumento de Custos Fixos reduz o lucro, mas a operação permanece lucrativa.")
        else:
            st.info("O cenário de risco não impactou negativamente o lucro.")
