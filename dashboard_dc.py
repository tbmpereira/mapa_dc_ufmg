import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from data_process import df

# Configuração da página
st.set_page_config(page_title="Mapeamento Divulgação Científica UFMG", layout="wide")

# Layout do título e imagem alinhados
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Mapeamento da Divulgação Científica na UFMG")
    st.header("Resultados Parciais", divider="gray")
with col2:
    st.image("assets/principal_completa_ufmg.jpg", width=250)

# Listas de opções
unidades = [unidade for unidade in sorted(df['unidade'].unique()) if unidade != 'nan']
areas_cnpq = [area for area in sorted(df['gde_area'].unique()) if area != 'nan']
areas_extensao = [area for area in sorted(df['area_extensao'].unique()) if area != 'nan']
tipos = ['extensão', 'ensino', 'pesquisa', "não informou"]
vinculos = df.vinculo.unique().tolist()

# Sidebar
st.sidebar.header("Filtros")

gde_area = st.sidebar.selectbox("Grande Área CNPq", ["Todas"] + areas_cnpq)
area_extensao = st.sidebar.selectbox("Área de Extensão", ["Todas"] + areas_extensao)
tipo = st.sidebar.multiselect("Tipo de ação", tipos, default=tipos)
vinculo = st.sidebar.multiselect("Vínculo com a UFMG", vinculos, default=vinculos)
unidade = st.sidebar.selectbox("Unidade", ["Todas"] + unidades)
posgrad = st.sidebar.radio("Vínculo com Programa de Pós-Graduação?", ["Sim", "Não", "Qualquer"], index=2)

# Filtragem dos dados
dff = df.copy()
if unidade != "Todas":
    dff = dff[dff['unidade'] == unidade]
if gde_area != "Todas":
    dff = dff[dff['gde_area'] == gde_area]
if area_extensao != "Todas":
    dff = dff[dff['area_extensao'] == area_extensao]
if set(tipo) != set(tipos): # Se o usuário selecionou algum tipo de ação
    if "não informou" in tipo:
        dff = dff[(dff[tipo].sum(axis=1) > 0) | (dff[['extensão', 'ensino', 'pesquisa']].fillna(0).sum(axis=1) == 0)]
    elif tipo:
        dff = dff[dff[tipo].fillna(0).sum(axis=1) > 0]
if vinculo:
    dff = dff[dff['vinculo'].isin(vinculo)]
if posgrad != "Qualquer":
    dff = dff[dff['programas'] == posgrad]
st.subheader(f"Total de registros: {len(dff)}")

# Abas
tabs = st.tabs([
    "Tabela de ações",
    "Distribuição por Grande Área CNPq",
    "Distribuição de Ações",
    "Distribuição de Vínculos",
    "Distribuição por Área de Extensão",
    "Distribuição por Unidade",
    "Públicos Específicos",
    "Redes Sociais",
    "Sobre"
])

# Tabela de registros
# Criar o novo dataframe com as colunas específicas e renomeá-las
df_topage = dff[
    [
        'unidade',
        'iniciativa[SQ001_SQ001]',
        'iniciativa[SQ002_SQ001]',
        'iniciativa[SQ003_SQ001]',
        'iniciativa[SQ004_SQ001]',
        'iniciativa[SQ005_SQ001]',
        'links[SQ001]',
        'links[SQ002]',
        'links[SQ004]',
        'links[SQ005]',
        'links[SQ006]'
    ]
].copy()

# Renomear as colunas conforme especificado
df_topage = df_topage.rename(columns={
    'iniciativa[SQ001_SQ001]': 'iniciativa1',
    'iniciativa[SQ002_SQ001]': 'iniciativa2',
    'iniciativa[SQ003_SQ001]': 'iniciativa3',
    'iniciativa[SQ004_SQ001]': 'iniciativa4',
    'iniciativa[SQ005_SQ001]': 'iniciativa5',
    'links[SQ001]': 'webpage',
    'links[SQ002]': 'facebook',
    'links[SQ004]': 'instagram',
    'links[SQ005]': 'youtube',
    'links[SQ006]': 'outro'
})

# Configurar as colunas de links para serem clicáveis
column_config = {
    "webpage": st.column_config.LinkColumn(
        label="webpage",
        display_text=None,  # Exibe o próprio URL
        validate="^https?://.+$",  # Valida URLs que começam com http:// ou https://
    ),
    "facebook": st.column_config.LinkColumn(
        label="facebook",
        display_text=None,
        validate="^https?://.+$",
    ),
    "instagram": st.column_config.LinkColumn(
        label="instagram",
        display_text=None,
        validate="^https?://.+$",
    ),
    "youtube": st.column_config.LinkColumn(
        label="youtube",
        display_text=None,
        validate="^https?://.+$",
    ),
    "outro": st.column_config.LinkColumn(
        label="outro",
        display_text=None,
        validate="^https?://.+$",
    ),
}

with tabs[0]:
    st.dataframe(df_topage, column_config=column_config, height=500, use_container_width=True)

# Gráficos
# Gráfico de Vínculos
with tabs[3]:
    vinculos_counts = dff['vinculo'].value_counts().reset_index()
    vinculos_counts.columns = ['vinculo', 'count']
    fig_vinculos = px.bar(
        vinculos_counts, 
        x='vinculo', 
        y='count',
        labels={'vinculo': '', 'count': ''}, 
        title="Distribuição de Vínculos")
    st.plotly_chart(fig_vinculos, use_container_width=True)

# Gráfico de Tipo de Ação
with tabs[2]:
    contagens = dff[['extensão', 'ensino', 'pesquisa']].sum()
    fig_tipo = go.Figure(data=[go.Pie(labels=contagens.index, values=contagens.values, title="")])
    st.write("**Distribuição de Ações de Divulgação Científica**")
    st.plotly_chart(fig_tipo, use_container_width=True)
    st.markdown("**Observação:** Cada respondente poderia mencionar até 5 ações de Divulgação Científica. Os números aqui apresentados representam o somatório de todas as ações.")

# Gráfico de Grande Área CNPq
with tabs[1]:
    gde_area_counts = dff['gde_area'].value_counts().reset_index()
    gde_area_counts.columns = ['gde_area', 'count']
    fig_grande_area = px.bar(
        gde_area_counts, 
        x='gde_area', 
        y='count',
        labels={'gde_area': '', 'count': ''}, 
        title="Distribuição por Grande Área")
    st.plotly_chart(fig_grande_area, use_container_width=True)

# Gráfico de Área de Extensão
with tabs[4]:
    area_ext_counts = dff['area_extensao'].value_counts().reset_index()
    area_ext_counts.columns = ['area_extensao', 'count']
    fig_area_extensao = px.bar(
        area_ext_counts, 
        x='area_extensao', 
        y='count', 
        labels={'area_extensao': '', 'count': ''},
        title="Distribuição por Área de Extensão")
    st.plotly_chart(fig_area_extensao, use_container_width=True)

# Gráfico de Unidades
with tabs[5]:
    mapeamento = {
        'Escola de Ciências da Informação': 'ECI',
        'Escola de Belas-Artes': 'EBA',
        'Faculdade de Filosofia e Ciências Humanas': 'FAFICH',
        'Escola de Enfermagem': 'Enfermagem',
        'Escola de Engenharia': 'Engenharia',
        'Faculdade de Ciências Econômicas': 'FACE',
        'Pró-Reitoria de Extensão': 'PROEX',
        'Instituto de Ciências Exatas': 'ICEX',
        'Instituto de Ciências Biológicas': 'ICB',
        'Instituto de Geociências': 'IGC',
        'Faculdade de Educação': 'FAE',
        'Escola de Arquitetura': 'Arquitetura',
        'Faculdade de Odontologia': 'Odonto',
        'Pró-Reitoria de Administração': 'PRA',
        'Faculdade de Letras': 'FALE',
        'Faculdade de Medicina': 'Medicina',
        'Pró-Reitoria de Recursos Humanos': 'PRORH',
        'Escola de Veterinária': 'Veterinária',
        'FUMP': 'FUMP',
        'Escola de Educação Física, Fisioterapia e Terapia Ocupacional': 'EEFFTO',
        'CEDECOM': 'CEDECOM',
        'Instituto de Ciências Agrárias': 'ICA',
        'Faculdade de Direito': 'Direito',
        'Gabinete da Reitoria': 'Gab. Reitoria',
        'Faculdade de Farmácia': 'Farmácia',
        'Colégio Técnico': 'COLTEC',
        'Escola de Música': 'Música',
        'Biblioteca Universitária': 'Biblioteca',
        'Centro Pedagógico': 'CP'
        }
    dff_unidade_counts = dff.unidade.value_counts().reset_index()
    dff_unidade_counts.columns = ['unidade', 'contagem']
    dff_unidade_counts['unidade'] = dff_unidade_counts['unidade'].map(mapeamento)
    fig_unidades = px.bar(dff_unidade_counts, x='unidade', y='contagem',
                        labels={'unidade': '', 'contagem': ''},
                        title='Distribuição de ações por Unidade (números absolutos)')
    st.plotly_chart(fig_unidades, use_container_width=True)

# Construindo o gráfico de Públicos Específicos
with tabs[6]:
    dff_publicos = dff.filter(like="publicoespecifico").iloc[:, :-1]
    colunas = [
    'Crianças', 'Jovens', 'Adultos', 'Idosos', 
    'Educação Infantil', 'Ensino Fundamental', 'Ensino Médio',
    'Cadastro Único', 'Indígenas', 'Pessoas negras', 'Entorno', 
    'Trabalhadores UFMG', 'Pessoas com deficiência', 'Doenças crônicas',
    'Moradores vilas', 'Comunidades rurais', 'Comunidades quilombolas',
    'Mulheres', 'LGBTQIA+', 'Imigrantes', 'Moradores de rua'
    ]
    dff_publicos.columns = colunas
    dff_publicos = dff_publicos.apply(lambda col: col.value_counts().get('Sim', 0)).reset_index()
    dff_publicos.columns = ['Público', 'Contagem']
    dff_publicos = dff_publicos.sort_values('Contagem', ascending=False)
    fig_publicos = px.bar(dff_publicos, 
                            x='Público', 
                            y='Contagem',
                        labels={'Público': '', 'Contagem': ''},
                        title='Público Alvo Específico (números absolutos)<br><sup>Entre os respondentes que informaram públicos específicos</sup>')
    st.plotly_chart(fig_publicos, use_container_width=True)

# Construindo o gráfico de Redes Sociais
with tabs[7]:
    url_pattern = re.compile(r'(https?|ftp)://[^\s/$.?#].[^\s]*', re.IGNORECASE)
    def is_valid_url(url):
        if pd.isna(url):
            return False
        return re.match(url_pattern, url) is not None
    websites = dff['links[SQ001]'].apply(is_valid_url).sum()
    facebook = dff['links[SQ002]'].apply(lambda x: "facebook" in str(x)).sum()
    instagram = dff['links[SQ004]'].apply(lambda x: "instagram" in str(x) or '@' in str(x)).sum()
    youtube = dff['links[SQ005]'].apply(lambda x: "youtu" in str(x)).sum()
    redes_sociais = pd.DataFrame({'Rede Social': ['Websites', 'Facebook', 'Instagram', 'Youtube'],
                                            'Contagem': [websites, facebook, instagram, youtube]
                                            })
    redes_sociais = redes_sociais.sort_values('Contagem', ascending=False)
    fig_socialmedia = px.bar(redes_sociais, 
                                x='Rede Social', 
                                y='Contagem',
                            labels={'Rede Social':'', 'Contagem':''},
                            title='Uso de Redes Sociais nas ações de Divulgação Científica (números absolutos)',
                            )
    st.plotly_chart(fig_socialmedia, use_container_width=True)

# Sobre
with tabs[8]:
    st.subheader("Sobre o Mapeamento")
    st.write(
        "Este dashboard apresenta resultados parciais do Mapeamento de Divulgação Científica da UFMG. "
        "O mapeamento ainda está aberto para preenchimento de toda a comunidade acadêmica da UFMG "
        "que atua no âmbito do ensino, da pesquisa e da extensão em divulgação científica."
    )
    st.write(
        "Através deste mapeamento, esperamos reunir informações que nos orientem na "
        "elaboração de políticas institucionais e que contribuam para a promoção de "
        "processos solidários e sinérgicos na divulgação científica."
    )
    st.write(
        "Se você participa de alguma ação de ensino, pesquisa ou extensão que tenha como "
        "objetivo o compartilhamento do conhecimento gerado na universidade com o público "
        "não especializado, sua colaboração é fundamental. Por favor, responda ao "
        "questionário clicando no botão abaixo."
    )
    st.markdown(
        "[Clique aqui para responder](https://questionarios.ufmg.br/index.php/286584?lang=pt-BR)",
        unsafe_allow_html=True
    )

st.markdown("---")
st.markdown("Dashboard desenvolvido por [Marcelo Pereira](https://marcelo-pereira.notion.site/)")