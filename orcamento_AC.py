import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, DataReturnMode
import pandas as pd
import io

# Configuração da página
st.set_page_config(page_title='Custos Instalação Ar Condicionado', page_icon='🌀')
st.title('Custos Instalação Ar Condicionado')

# Adiciona o estilo CSS para alterar a cor dos botões
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização da tabela de materiais
if 'materiais' not in st.session_state:
    st.session_state['materiais'] = []

# Função para adicionar um novo material à tabela
def add_material(material, quantidade, preco_unit):
    preco_total = quantidade * preco_unit
    st.session_state['materiais'].append({
        'Material': material,
        'Quantidade': quantidade,
        'Preço Unitário (R$)': preco_unit,
        'Preço Total (R$)': preco_total
    })

# Função para recalcular os preços totais com base nas edições da tabela
def recalcular_tabela(data):
    df = pd.DataFrame(data)
    df['Preço Total (R$)'] = df['Quantidade'] * df['Preço Unitário (R$)']
    return df.to_dict('records')

# Inicialização das variáveis de entrada
if 'material_input' not in st.session_state:
    st.session_state['material_input'] = ''
if 'quantidade_input' not in st.session_state:
    st.session_state['quantidade_input'] = 0.0
if 'preco_unit_input' not in st.session_state:
    st.session_state['preco_unit_input'] = 0.0

# Barra lateral com os dados da instalação
with st.sidebar:
    st.title('Custos e Despesas')
    cobre_liquido = st.selectbox('Selecione a bitola da linha de líquido:', ['1/4', '3/8', '5/8', '3/4'])
    cobre_succao = st.selectbox('Selecione a bitola da linha de succão:', ['3/8', '1/2', '5/8', '7/8', '3/4'])
    metros = st.number_input('Digite quantos metros tem a linha:', min_value=0.0, step=0.1)
    valor_cobre = st.number_input('Digite o preço do kilo do cobre:', min_value=0.1, step=0.1)

    # Cálculo do preço do cobre com base nas bitolas e metros
    preco_cobre = 0
    if cobre_succao == '3/8' and cobre_liquido == '1/4':
        preco_cobre = float(metros * 0.255 + metros * 0.132) * valor_cobre
    elif cobre_succao == '1/2' and cobre_liquido == '1/4':
        preco_cobre = float(metros * 0.285 + metros * 0.132) * valor_cobre
    elif cobre_succao == '5/8' and cobre_liquido == '1/4':
        preco_cobre = float(metros * 0.365 + metros * 0.132) * valor_cobre
    elif cobre_succao == '5/8' and cobre_liquido == '3/8':
        preco_cobre = float(metros * 0.365 + metros * 0.255) * valor_cobre
    elif cobre_succao == '7/8' and cobre_liquido == '3/8':
        preco_cobre = float(metros * 0.520 + metros * 0.255) * valor_cobre
    elif cobre_succao == '7/8' and cobre_liquido == '3/4':
        preco_cobre = float(metros * 0.520 + metros * 0.415) * valor_cobre
    elif cobre_succao == '3/4' and cobre_liquido == '3/8':
        preco_cobre = float(metros * 0.415 + metros * 0.255) * valor_cobre
    elif cobre_succao == '3/4' and cobre_liquido == '5/8':
        preco_cobre = float(metros * 0.415 + metros * 0.365) * valor_cobre
    else:
        st.warning('Combinação de bitolas não reconhecida.')

    # Adiciona o preço do cobre à tabela de materiais
    if st.button('Adicionar Cobre'):
        if preco_cobre > 0:
            add_material(f'Cobre (Sucção: {cobre_succao}, Líquido: {cobre_liquido})', metros, preco_cobre / metros)
            st.success(f'O valor do cobre é R$ {preco_cobre:.2f} e foi adicionado à tabela.')
        else:
            st.error('Não foi possível calcular o valor do cobre.')

# Seção para entrada de outros materiais
st.write('### Adicionar outros materiais')
st.session_state['material_input'] = st.text_input('Nome do Material:', value=st.session_state['material_input'])
st.session_state['quantidade_input'] = st.number_input('Quantidade:', min_value=0.0, step=0.1, value=st.session_state['quantidade_input'])
st.session_state['preco_unit_input'] = st.number_input('Preço Unitário (R$):', min_value=0.0, step=0.1, value=st.session_state['preco_unit_input'])

# Botão para adicionar material adicional
if st.button('Adicionar Material'):
    if st.session_state['material_input'] and st.session_state['quantidade_input'] > 0 and st.session_state['preco_unit_input'] > 0:
        add_material(st.session_state['material_input'], st.session_state['quantidade_input'], st.session_state['preco_unit_input'])
        st.success('Material adicionado com sucesso!')
        st.session_state['material_input'] = ''
        st.session_state['quantidade_input'] = 0.0
        st.session_state['preco_unit_input'] = 0.0
    else:
        st.error('Preencha todos os campos corretamente.')

# Exibição da tabela de materiais usando AgGrid
if st.session_state['materiais']:
    df = pd.DataFrame(st.session_state['materiais'])
    
    # Configuração da tabela para permitir edição
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(editable=True)
    gridOptions = gb.build()

    # Exibição da tabela
    response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        editable=True,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
    )

    # Atualizar a tabela após edição
    updated_data = response['data']
    if updated_data is not None and not updated_data.empty:
        df_updated = pd.DataFrame(updated_data)
        df_updated['Preço Total (R$)'] = df_updated['Quantidade'] * df_updated['Preço Unitário (R$)']
        st.session_state['materiais'] = df_updated.to_dict('records')
        st.success('Tabela atualizada com sucesso!')

# Cálculo do preço total dos materiais
preco_total = sum(item['Preço Total (R$)'] for item in st.session_state['materiais'])
st.write(f'**Valor da Instalação sem Markup: R$ {preco_total:.2f}**')

# Campos para impostos e lucro
st.write('### Calcular Markup')
impostos = st.number_input('Impostos (%):', min_value=0.0, step=0.1)
lucro = st.number_input('Lucro desejado (%):', min_value=0.0, step=0.1)

# Cálculo do valor final com markup
if impostos + lucro < 100:
    markup = 1 + (impostos + lucro) / 100
    valor_final = preco_total * markup
    st.write(f'**Valor da Instalação com Markup: R$ {valor_final:.2f}**')
else:
    st.error('A soma de impostos e lucro não pode ser maior que 100%.')

# Botão para salvar o orçamento em Excel
if st.button('Salvar Orçamento'):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Orçamento')
        
        # Adiciona o nome do cliente na primeira célula
        workbook = writer.book
        worksheet = writer.sheets['Orçamento']
        worksheet.write('A1', f'Nome do Cliente: {cliente}')
    st.download_button(
        label='Baixar Orçamento em Excel',
        data=output.getvalue(),
        file_name='orcamento_instalacao.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
