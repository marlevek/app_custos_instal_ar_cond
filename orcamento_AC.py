import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
from fpdf import FPDF
import io

# page_icon: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.set_page_config(page_title='Custos Instalação Ar Condicionado', page_icon=':mechanic:', layout='wide')
st.title('Orçamento Instalação Ar-Condicionado :mechanic:')

# Adiciona o estilo CSS para alterar a cor dos botões
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50; /* Cor de fundo do botão */
        color: white; /* Cor do texto */
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
        background-color: #4CAF50; /* Cor de fundo ao passar o mouse */
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
    # Adiciona o material à lista de materiais mantida na sessão
    st.session_state['materiais'].append({
        'Material': material,
        'Quantidade': quantidade,
        'Preço Unitário (R$)': preco_unit,
        'Preço Total (R$)': preco_total
    })
    
# Campo para o nome do cliente
cliente = st.text_input('Nome do Cliente: ').strip()


st.title('Custos e Despesas')
st.write('## Tubulação de Cobre')
    
# Usando selectbox para garantir entrada consistente
cobre_liquido = st.selectbox('Selecione a bitola da linha de líquido:', ['1/4', '3/8'])
cobre_succao = st.selectbox('Selecione a bitola da linha de succão:', ['3/8', '1/2', '5/8', '7/8', '3/4'])
metros = st.number_input('Digite quantos metros tem a linha:', min_value=0.0, step=0.1)
valor_cobre = st.number_input('Digite o preço do kg do cobre')
preco_cobre = 0
           
if cobre_succao == '3/8' and cobre_liquido == '1/4':
    preco_cobre = float(metros * 0.255 + metros * 0.132) * valor_cobre
    
elif cobre_succao == '1/2' and cobre_liquido == '1/4':
    preco_cobre = float(metros * 0.285 + metros * 0.132) * valor_cobre
    
elif cobre_succao == '5/8' and cobre_liquido == '3/8':
    preco_cobre = float(metros * 0.365 + metros * 0.255) * valor_cobre
    
elif cobre_succao == '5/8' and cobre_liquido == '1/4':
    preco_cobre = float(metros * 0.365 + metros * 0.132) * valor_cobre

else:
    st.warning('Combinação de bitolas não reconhecida. Verifique os valores inseridos.')
    
# Adiciona o preço do cobre à tabela de materiais
if st.button('Adicionar Cobre'):
    if preco_cobre > 0:
        add_material('Cobre (Sucção: )' + cobre_succao + ', Líquido: ' + cobre_liquido + ')', metros, preco_cobre / metros)
        st.success(f'O valor do cobre é R$ {preco_cobre:.2f} e foi adicionado à tabela ')
    else:
        st.error('Não foi possível calcular o valor do cobre. Verifique os dados inseridos')    

# Seção para cálculo do km rodado
st.write('### Cálculo do km rodado (ida e volta) até o local do serviço') 
tipo_combustivel = st.selectbox('Combustível:', ['Gasolina', 'Etanol', 'Diesel'])
preco_litro = st.number_input('Preço do litro do combustível (R$):', min_value=0.0, step=0.1)
km_rodado = st.number_input('Distância em km até o local do serviço:', min_value=0.0, step=0.1)
consumo_por_km = st.number_input('Consumo médio do veículo (km/L):', min_value=0.1, step=0.1)

# Cálculo do custo do km rodado
preco_km = round(km_rodado / consumo_por_km) * preco_litro

# Adiciona o preço do km rodado à tabela de materiais
if st.button('Adicionar km rodado'):
    if preco_km > 0:
        add_material(f'Km rodado ({tipo_combustivel})', km_rodado, preco_km / km_rodado)
        st.success(f'Preço do km rodado adicionado: R${preco_km:.2f}')
    else:
        st.error('Não foi possível calcular o preço do km rodado. Verifique os dados inseridos.')

# Outros custos
st.write('## Outros Custos')

# Ajudante
st.subheader('Ajudante')
qtde_ajudante = st.number_input('Quantos ajudantes', min_value=1, step=1)
valor_ajudante = st.number_input('Valor Diária', min_value=1.0, step=1.0)
total_ajudante = valor_ajudante * qtde_ajudante
if st.button('Adicionar Ajudante'):
    if total_ajudante > 0:
        add_material('Ajudante', qtde_ajudante, total_ajudante / qtde_ajudante)
        st.success(f'Custos do ajudante adicionado: R$ {total_ajudante:.2f}')
    else:
        st.error('Não foi possível adicionar custos com ajudante. Verifique os dados') 

# Alimentação
st.subheader('Alimentação')
pessoas_alim = st.number_input('Quantas pessoas', min_value=1, step=1)
custo_alim = st.number_input('Preço', min_value=1.0, step=1.0)
custo_total_alim = pessoas_alim * custo_alim
if st.button('Adicionar Alimentação'):
    if custo_total_alim > 0:
        add_material('Alimentação', pessoas_alim, custo_total_alim / pessoas_alim)
        st.success(f'Custos de alimentação adicionado: R$ {custo_total_alim:.2f}')
    else:
        st.error('Não foi possível adicionar custos de alimentação. Verifique os valores.')

# Entrada de materiais adicionais
st.write('### Adicionar outros materiais')

# Inicializa os campos temporários se ainda não estiverem definidos
if 'materiais' not in st.session_state:
    st.session_state['materiais'] = []

if 'quantidade_input' not in st.session_state:
    st.session_state['quantidade_input'] = 0.0

if 'preco_unit_input' not in st.session_state:
    st.session_state['preco_unit_input'] = 0.0

if 'material_input' not in st.session_state:
    st.session_state['material_input'] = ''

# Função para resetar os campos
def reseta_campos():
    st.session_state['material_input'] = ''
    st.session_state['quantidade_input'] = 0.0
    st.session_state['preco_unit_input'] = 0.0


# Campos de entrada para o material adicional
material_input = st.text_input(
    'Nome do Material:',
    value=st.session_state['material_input'],
    key="material_input_widget"
)

quantidade_input = st.number_input(
    'Quantidade:',
    min_value=0.0,
    step=0.1,
    value=st.session_state['quantidade_input'],
    key="quantidade_input_widget"
)

preco_unit_input = st.number_input(
    'Preço Unitário (R$):',
    min_value=0.0,
    step=0.1,
    value=st.session_state['preco_unit_input'],
    key="preco_unit_input_widget"
)

# Botão para incluir material adicional
if st.button('Adicionar Material'):
    material = material_input.strip()
    quantidade = quantidade_input
    preco_unitario = preco_unit_input

    if material and quantidade > 0 and preco_unitario > 0:
        # Adiciona à lista de materiais
        st.session_state['materiais'].append({
            'Material': material,
            'Quantidade': quantidade,
            'Preço Unitário': preco_unitario,
        })
        st.success(f'Material "{material}" adicionado com sucesso!')
        reseta_campos()  # Reseta os campos no session state
    else:
        st.error('Preencha todos os campos corretamente.')


# Exibição da tabela de materiais usando AgGrid
if st.session_state['materiais']:
    df = pd.DataFrame(st.session_state['materiais'])
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gridOptions = gb.build()
    
    st.write('## Tabela de Custos Variáveis')
    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, fit_columns_on_grid_load=True)

if st.session_state['materiais']:
    preco_total = sum(item['Preço Total (R$)'] for item in st.session_state['materiais'])
    st.write(f'**Valor dos Custos Variáveis: R$ {preco_total:.2f}**')

# Custos Fixos
st.subheader('**Cálculo dos Custos Fixos:**')
despesas_totais = st.number_input('Digite o valor das despesas totais da sua empresa', min_value=1.0, step=0.1)
horas_trabalhadas = st.number_input('Informe o total de horas trabalhadas por mes', min_value=1.0, step=0.1)
tempo_instalacao = st.number_input('Informe quanto tempo (h) levará a instalação', min_value=1.0, step=0.1)
custos_fixos = (despesas_totais / horas_trabalhadas) * tempo_instalacao
btn_custos_fixos = st.button('Calcular Custos Fixos')
if btn_custos_fixos:
    st.write(f'**O valor dos custos fixos é R$ {custos_fixos:.2f}**')


# Markup
st.subheader('Informações para o cálculo do markup:')
st.write('O markup é a diferença entre o custo de um produto ou serviço e o seu preço de venda. Ele é comumente utilizado como uma porcentagem adicionada ao custo de produção, para cobrir todas as despesas e ainda gerar lucro.')
st.write('Imposto:')
imposto = st.number_input('Digite apenas o valor. Ex.: 2 para 2%', min_value=0.0, step=0.1)
st.write('Lucro:')
lucro =  st.number_input('Digite o valor do seu lucro. Ex.: 15 para 15%', min_value=0.0, step=0.1)
markup = 1 + (imposto / 100) + (lucro / 100)

# Cálculo do preço total da instalação
btn_valor_total = st.button('Calcular Valor Total')
if btn_valor_total:
    if not st.session_state['materiais']:
        st.error('Certifique-se de adicionar materiais antes de calcular o valor total.')
    elif custos_fixos <= 0 or preco_total <= 0 or markup <= 0:
        st.error('Certifique-se de preencher os campos obrigatórios para custos fixos, custos variáveis e markup.')
    else:
        # Agora, realiza o cálculo apenas se os dados estiverem completos
        valor_total_instalacao = (preco_total + custos_fixos) * markup
        st.write(f'**Valor Total da Instalação: R$ {valor_total_instalacao:.2f}')
        lucro_obtido = valor_total_instalacao - preco_total
        st.write(f'O lucro nessa instalação é de: R$ {lucro_obtido:.2f}')


# Botão para salvar o orçamento em Excel
if st.button('Salvar Orçamento em excel'):
    if cliente and st.session_state['materiais']:
        df = pd.DataFrame(st.session_state['materiais'])
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
    else:
        st.error('Certifique-se de preencher o nome do cliente e adicionar os materiais antes de gerar o arquivo em excel.')


# Função paa criar PDF
def criar_pdf(cliente, materiais, custos_fixos, preco_total, markup, valor_total_instalacao):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    
    pdf.set_font('Arial', style='B', size=14) # titulo
    pdf.cell(200, 10, txt='Orçamento - Instalação de Ar-Condicionado', ln=True, align='C')
    
    # Dados Cliente
    pdf.set_font('Arial', size=12)
    pdf.ln(10)
    pdf.cell(200, 10, text=f'Cliente: {cliente}', ln=True, align='L')
    
    # Tabela de Materiais
    pdf.ln(10)
    pdf.cell(200, 10, text='Materiais', ln=True, align='L')
    pdf.set_font('Arial', size=10)
    for item in materiais:
        material = item['Material']
        quantidade = item['Quantidade']
        preco_unit = item['Preço Unitário (R$)']
        preco_total_item = item['Preço Total (R$)']
        pdf.cell(200, 10, txt=f'{material} - {quantidade}x - R$ {preco_unit:.2f} (Total: R$ {preco_total_item:.2f})', ln=True)
    
    # Custos Fixos
    pdf.ln(10)
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, text=f'Custos Fixos: R$ {custos_fixos:.2f}', ln=True)
    
    # Custos Variáveis
    pdf.cell(200, 10, text=f'Custos Variáveis: R$ {preco_total:.2f}', ln=True)
    
    # Markup e valor total
    pdf.cell(200, 10, text=f'Markup Aplicado: {markup:.2f}', ln=True)
    pdf.set_font('Arial', style='B', size=12)
    pdf.cell(200, 10, text=f'Valor Total da Instalação: R$ {valor_total_instalacao:.2f}', ln=True)
    
    return pdf

# Botão para salvar o orçamento em PDF
if st.button('Salvar orçamento em PDF'):
    if cliente and st.session_state['materiais']:
        pdf = criar_pdf(cliente, st.session_state['materiais'], custos_fixos, preco_total, markup, valor_total_instalacao)
        pdf_output = io.BytesIO()
        pdf.output(pdf_output, 'F')
        st.download_button(
            label='Baixar Orçamento em PDF',
            data = pdf_output.getvalue(),
            file_name='orcamento_instalacao.pdf',
            mime='application/pdf',
        )
    else:
        st.error('Certifique-se de preencher o nome do cliente e adicionar os materiais antes de gerar o pdf.')

    