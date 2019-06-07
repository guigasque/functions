
# Módulo 3.2 - Validação Template DDI

### Validar os campos que serão utilizados da base DDI

Data de criação: 07/06/2019 <br>
Atualização: 07/06/2019 <br>
Responsável: Xito

##### Premissas:
    - Nome Arquivo (?)
    - Nome da Aba devem manter o padrão - 'Curso';
    - Nome das colunas, ao menos das que serão utilizadas para validação deverão ser padronizadas;

### Carregando Libs


```python
import re
import pandas as pd
import datetime as dt
from libs.generic_operator import write_dataframe_to_csv_on_s3
try:
    import unidecode
finally:
    !pip install unidecode
```

    Requirement already satisfied: unidecode in /home/ec2-user/anaconda3/envs/python3/lib/python3.6/site-packages (1.0.23)


##### Diretórios:

###### Bases de Entrada:


```python
INPUT_BASE_DDI = 's3a://krotonanalytics/stakeholders/academico/0_transient/NAVE_ENADE/BASE_DDI/raw/base_ddi.xlsx'

OUTPUT_BASE_DDI = ''
```

##### Lista com os nomes das colunas para verificação


```python
# Identificanado ano ENADE anterior para
ano_enade_1 = dt.date(dt.datetime.now().year - 1, dt.datetime.now().month, dt.datetime.now().day)
ano_enade_1 = ano_enade_1.strftime("%y")
```


```python
COLUNA_VERIFICACAO = [
'Cód. IES',
'Cód. Curso',
#'Cód. Curso Representado',
'Curso',
'Cód. Local de Oferta',
'Grau',
'Situação de funcionamento do curso - e-Mec',
'Situação de funcionamento do curso (dez/{})'.format(ano_enade_1),
'Situação do Curso no Censo 20{}'.format(ano_enade_1)]
```


```python
try:
    df = pd.read_excel(INPUT_BASE_DDI, sheet_name = 'Curso')
    df = df.applymap(str)
except:
    print('O nome da aba não está de acordo com o padrão, por favor revise.')
    exit()
```

##### Verificação se o nomes das colunas foram alterados


```python
COLUNAS_VERIFICADAS = set(COLUNA_VERIFICACAO).difference(set(df.columns))
assert(COLUNAS_VERIFICADAS == set()), 'A(s) seguinte(s) coluna(s) {} não estão de acordo com a padronização'.format(COLUNAS_VERIFICADAS).replace('{', '').replace('}', '')
```


```python
df[COLUNA_VERIFICACAO].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Cód. IES</th>
      <th>Cód. Curso</th>
      <th>Curso</th>
      <th>Cód. Local de Oferta</th>
      <th>Grau</th>
      <th>Situação de funcionamento do curso - e-Mec</th>
      <th>Situação de funcionamento do curso (dez/18)</th>
      <th>Situação do Curso no Censo 2018</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>242</td>
      <td>6159</td>
      <td>PEDAGOGIA</td>
      <td>2800</td>
      <td>LICENCIATURA</td>
      <td>EM ATIVIDADE</td>
      <td>EM ATIVIDADE</td>
      <td>Ativo com alunos em 2018</td>
    </tr>
    <tr>
      <th>1</th>
      <td>242</td>
      <td>6160</td>
      <td>PSICOLOGIA</td>
      <td>657799</td>
      <td>BACHARELADO</td>
      <td>EM ATIVIDADE</td>
      <td>EM ATIVIDADE</td>
      <td>Ativo com alunos em 2018</td>
    </tr>
    <tr>
      <th>2</th>
      <td>242</td>
      <td>6163</td>
      <td>LETRAS</td>
      <td>657799</td>
      <td>LICENCIATURA</td>
      <td>EXTINTO</td>
      <td>EXTINTO</td>
      <td>Não Carregado no Censo 2018</td>
    </tr>
    <tr>
      <th>3</th>
      <td>242</td>
      <td>6164</td>
      <td>FABRICAÇÃO MECÂNICA</td>
      <td>2800</td>
      <td>TECNOLÓGICO</td>
      <td>EM ATIVIDADE</td>
      <td>EM ATIVIDADE</td>
      <td>Ativo com alunos em 2018</td>
    </tr>
    <tr>
      <th>4</th>
      <td>242</td>
      <td>6165</td>
      <td>AUTOMAÇÃO INDUSTRIAL</td>
      <td>2800</td>
      <td>TECNOLÓGICO</td>
      <td>EM ATIVIDADE</td>
      <td>EM EXTINÇÃO</td>
      <td>Ativo somente para desvincular alunos 2017</td>
    </tr>
  </tbody>
</table>
</div>



###### Retirando espaço e acentos do nome da coluna


```python
for x in df.columns:
    df = df.rename(columns = {x : re.sub('[^A-Za-z0-9]+', '_', unidecode.unidecode(x)).lower()})
    for x in df.columns:
        if x[len(x)-1:] == '_':
            df = df.rename(columns = {x : x[0:len(x)-1]})
            
COLUNA_VERIFICACAO_MINUSCULA = [re.sub('[^A-Za-z0-9]+', '_', unidecode.unidecode(word)).lower() for word in COLUNA_VERIFICACAO]

for x in range(0, len(COLUNA_VERIFICACAO_MINUSCULA) - 1):
    if COLUNA_VERIFICACAO_MINUSCULA[x][len(COLUNA_VERIFICACAO_MINUSCULA[x])-1:] == '_':
        COLUNA_VERIFICACAO_MINUSCULA[x] = COLUNA_VERIFICACAO_MINUSCULA[x][0:len(COLUNA_VERIFICACAO_MINUSCULA[x])-1]
```

##### Validação se as colunas que serão utilizadas para conferência não contém valores nulos


```python
for x in COLUNA_VERIFICACAO_MINUSCULA:
    if bool(set(~df[x].isnull())) == True:
        print('A coluna {} está validada'.format(x))
        pass
    else:
        print('A coluna {} contém valores vazios, por favor, reveja essa coluna'.format(x))
```

    A coluna cod_ies está validada
    A coluna cod_curso está validada
    A coluna curso está validada
    A coluna cod_local_de_oferta está validada
    A coluna grau está validada
    A coluna situacao_de_funcionamento_do_curso_e_mec está validada
    A coluna situacao_de_funcionamento_do_curso_dez_18 está validada
    A coluna situacao_do_curso_no_censo_2018 está validada



```python
df[COLUNA_VERIFICACAO_MINUSCULA].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cod_ies</th>
      <th>cod_curso</th>
      <th>curso</th>
      <th>cod_local_de_oferta</th>
      <th>grau</th>
      <th>situacao_de_funcionamento_do_curso_e_mec</th>
      <th>situacao_de_funcionamento_do_curso_dez_18</th>
      <th>situacao_do_curso_no_censo_2018</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>242</td>
      <td>6159</td>
      <td>PEDAGOGIA</td>
      <td>2800</td>
      <td>LICENCIATURA</td>
      <td>EM ATIVIDADE</td>
      <td>EM ATIVIDADE</td>
      <td>Ativo com alunos em 2018</td>
    </tr>
    <tr>
      <th>1</th>
      <td>242</td>
      <td>6160</td>
      <td>PSICOLOGIA</td>
      <td>657799</td>
      <td>BACHARELADO</td>
      <td>EM ATIVIDADE</td>
      <td>EM ATIVIDADE</td>
      <td>Ativo com alunos em 2018</td>
    </tr>
    <tr>
      <th>2</th>
      <td>242</td>
      <td>6163</td>
      <td>LETRAS</td>
      <td>657799</td>
      <td>LICENCIATURA</td>
      <td>EXTINTO</td>
      <td>EXTINTO</td>
      <td>Não Carregado no Censo 2018</td>
    </tr>
    <tr>
      <th>3</th>
      <td>242</td>
      <td>6164</td>
      <td>FABRICAÇÃO MECÂNICA</td>
      <td>2800</td>
      <td>TECNOLÓGICO</td>
      <td>EM ATIVIDADE</td>
      <td>EM ATIVIDADE</td>
      <td>Ativo com alunos em 2018</td>
    </tr>
    <tr>
      <th>4</th>
      <td>242</td>
      <td>6165</td>
      <td>AUTOMAÇÃO INDUSTRIAL</td>
      <td>2800</td>
      <td>TECNOLÓGICO</td>
      <td>EM ATIVIDADE</td>
      <td>EM EXTINÇÃO</td>
      <td>Ativo somente para desvincular alunos 2017</td>
    </tr>
  </tbody>
</table>
</div>



##### Dicionário 



# Módulo 2.2 - Padroniza Nome Cursos Ativos

### Padroniza os Cursos Elegíveis ao ENADE não capturados pelo Módulo 2.1 - Compara Cursos Ativos

 - Padronização dos nomes de cursos ENADE não encontrados pelo módulo de comparação

Data de criação: 31/05/2019 <br>
Atualização: 05/06/2019 <br>
Responsável: Xito e Faius

### Carregando Libs


```python
import pandas as pd
from libs.generic_operator import write_dataframe_to_csv_on_s3, apply_depara
```

#### Diretórios


```python
INPUT_CURSOS_ENADE = 's3://krotonanalytics/stakeholders/academico/0_transient/NAVE_ENADE/CURSOS_ENADE/trusted/cursos_enade.csv'
INPUT_CURSOS_ATIVOS_ENADE = 's3://krotonanalytics/stakeholders/academico/0_transient/NAVE_ENADE/CURSOS_PADRONIZADOS/trusted/cursos_padronizados.csv'

OUTPUT_CURSOS_ATIVOS_ENADE = 'stakeholders/academico/0_transient/NAVE_ENADE/CURSOS_PADRONIZADOS/trusted/cursos_padronizados_verificados.csv'
```

### Leitura dos Dados


```python
df_cursos_ativos = pd.read_csv(INPUT_CURSOS_ATIVOS_ENADE, encoding='latin-1', sep=';')
df_cursos_enade = pd.read_csv(INPUT_CURSOS_ENADE, sep=';')
```

##### Cursos encontrados pela regra automática


```python
df_cursos_ativos_curso_padronizado_check = set(df_cursos_ativos.curso_padronizado)
```

##### Atribuir a quantidade de observacoes da tabela original para que ao final do processo seja feita a conferência


```python
df_cursos_ativos_observacoes = df_cursos_ativos.shape[0]
```

#### Constantes do Processo

 - Setando Ano do ENADE

# Mudar ano enade para datetime


```python
ANO_ENADE = int(df_cursos_ativos.ano_enade.drop_duplicates())
```

- Setando os graus dos cursos Enadistas do ano vigente:
    - Utilize BCH para Bacharelado;
    - Utilize LIC para Licenciatura;
    - Utilize TEC para Tecnólogo;


```python
GRAU_ENADE = list(set(df_cursos_enade.area_padronizada[df_cursos_enade.ano_enade == ANO_ENADE]))
```


```python
CURSOS_ENADE = list(set(df_cursos_enade.nome_curso_edital[df_cursos_enade.ano_enade == ANO_ENADE]))
```


```python
print('Ano ENADE:', ANO_ENADE, 'Graus Avaliados:', GRAU_ENADE)
```

    Ano ENADE: 2019 Graus Avaliados: ['TEC', 'BCH']


##### Lista de cursos ENADE

##### Filtragem que seleciona os cursos ENADE que foram identificados no Módulo 2.1 - Compara Cursos Ativos


```python
df_cursos_ativos_enade_correto_filt = df_cursos_ativos[(df_cursos_ativos.flag_not_found_curso_enade == False)]
```


```python
df_cursos_ativos_enade_correto_filt.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>44</td>
      <td>97980</td>
      <td>ADMINISTRAÇÃO</td>
      <td>BCH</td>
      <td>administracao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>47</td>
      <td>97990</td>
      <td>SERVIÇO SOCIAL</td>
      <td>BCH</td>
      <td>servico social</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>48</td>
      <td>97327</td>
      <td>SUPERIOR DE TECNOLOGIA EM PROCESSOS GERENCIAIS</td>
      <td>TEC</td>
      <td>processos gerenciais</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>39</td>
      <td>89380</td>
      <td>PEDAGOGIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>pedagogia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>60</td>
      <td>NaN</td>
      <td>FILOSOFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>filosofia</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>



##### Criação lista de cursos que ja foram tratados


```python
df_cursos_ativos_total = list(set(df_cursos_ativos.curso_padronizado))
set(df_cursos_ativos_total)
```




    {'administracao',
     'agronegocio',
     'agronomia',
     'analise e desenvolvimento de sistemas',
     'arquitetura e urbanismo',
     'artes visuais',
     'atualizacao de documentos provaveis formandos 2019/1 aesa',
     'automacao industrial',
     'banco de dados',
     'biomedicina',
     'ciencia da computacao',
     'ciencias aeronauticas',
     'ciencias biologicas',
     'ciencias contabeis',
     'ciencias economicas',
     'ciencias economicas (economia)',
     'comercio exterior',
     'desenho industrial',
     'desenvolvimento em software',
     'design',
     'design de interiores',
     'design de moda',
     'design grafico',
     'direito',
     'educacao fisica',
     'eletrotecnica industrial',
     'embelezamento e imagem pessoal',
     'empreendedorismo',
     'enfermagem',
     'engenharia ambiental',
     'engenharia ambiental e sanitaria',
     'engenharia civil',
     'engenharia da computacao',
     'engenharia de computacao',
     'engenharia de controle e automacao',
     'engenharia de minas',
     'engenharia de petroleo',
     'engenharia de producao',
     'engenharia de producao mecanica',
     'engenharia eletrica',
     'engenharia eletronica',
     'engenharia florestal',
     'engenharia mecanica',
     'engenharia mecatronica',
     'engenharia quimica',
     'estetica e cosmetica',
     'estetica e imagem pessoal',
     'eventos',
     'fabricacao mecanica',
     'farmacia',
     'filosofia',
     'fisica',
     'fisioterapia',
     'fonoaudiologia',
     'fotografia',
     'gastronomia',
     'geografia',
     'gestao ambiental',
     'gestao comercial',
     'gestao da producao industrial',
     'gestao da qualidade',
     'gestao da ti',
     'gestao de recursos humanos',
     'gestao de seguranca privada',
     'gestao de ti',
     'gestao de turismo',
     'gestao do agronegocio',
     'gestao financeira',
     'gestao hospitalar',
     'gestao publica',
     'historia',
     'jogos digitais',
     'jornalismo',
     'letras - espanhol',
     'letras - ingles',
     'letras - portugues',
     'letras - portugues e espanhol',
     'letras - portugues e ingles',
     'logistica',
     'marketing',
     'marketing digital',
     'matematica',
     'mecatronica industrial',
     'medicina',
     'medicina veterinaria',
     'musica',
     'nutricao',
     'odontologia',
     'pedagogia',
     'pilotagem profissional de aeronaves',
     'processos gerenciais',
     'producao audiovisual',
     'producao multimidia',
     'psicologia',
     'publicidade e propaganda',
     'quimica',
     'radiologia',
     'redes de computadores',
     'relacoes internacionais',
     'relacoes publicas',
     'secretariado executivo bilingue',
     'seguranca do trabalho',
     'seguranca no trabalho',
     'seguranca publica',
     'servico social',
     'servicos juridicos, cartorarios e notariais',
     'sistemas de informacao',
     'sistemas para internet',
     'sociologia',
     'turismo'}



##### Filtragem que seleciona os cursos ENADE,  que não foram identificados no Módulo 2.1 - Compara Cursos Ativos


```python
df_cursos_ativos_enade_erro_filt = df_cursos_ativos[(df_cursos_ativos.flag_not_found_curso_enade == True) &
                                                    (df_cursos_ativos.flag_not_implied_area_padronizada == False)]
df_cursos_ativos_enade_erro_filt.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>111</td>
      <td>NaN</td>
      <td>SUPERIOR DE TECNOLOGIA EM ESTÉTICA E IMAGEM PE...</td>
      <td>TEC</td>
      <td>estetica e imagem pessoal</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>True</td>
    </tr>
    <tr>
      <th>21</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2OH</td>
      <td>13827</td>
      <td>SUPERIOR DE TECNOLOGIA EM MARKETING DIGITAL</td>
      <td>TEC</td>
      <td>marketing digital</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>True</td>
    </tr>
    <tr>
      <th>29</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>BAQ</td>
      <td>NaN</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO DE TURISMO</td>
      <td>TEC</td>
      <td>gestao de turismo</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>True</td>
    </tr>
    <tr>
      <th>30</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>BAQ</td>
      <td>NaN</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO DE TURISMO</td>
      <td>TEC</td>
      <td>gestao de turismo</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>True</td>
    </tr>
    <tr>
      <th>32</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>BAP</td>
      <td>NaN</td>
      <td>PUBLICIDADE E PROPAGANDA</td>
      <td>BCH</td>
      <td>publicidade e propaganda</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python

```

##### Lista de cursos ENADE, das áreas de bacharel e licenciatura que não foram identificados com área padronizada no Módulo 2.1 - Compara Cursos Ativos para conferência


```python
vec_curso_area = df_cursos_ativos_enade_erro_filt[['curso_padronizado', 'area_padronizada']].drop_duplicates()
vec_curso_area.sort_values('curso_padronizado')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>curso_padronizado</th>
      <th>area_padronizada</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1855</th>
      <td>artes visuais</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>255</th>
      <td>automacao industrial</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>2655</th>
      <td>banco de dados</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>1282</th>
      <td>ciencias aeronauticas</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>53</th>
      <td>ciencias economicas (economia)</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>2262</th>
      <td>desenho industrial</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>3443</th>
      <td>desenvolvimento em software</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>2235</th>
      <td>eletrotecnica industrial</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>34</th>
      <td>embelezamento e imagem pessoal</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>40</th>
      <td>empreendedorismo</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>196</th>
      <td>engenharia ambiental e sanitaria</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>260</th>
      <td>engenharia da computacao</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>969</th>
      <td>engenharia de minas</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>852</th>
      <td>engenharia de petroleo</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>482</th>
      <td>engenharia de producao mecanica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>2361</th>
      <td>engenharia eletronica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>2930</th>
      <td>engenharia mecatronica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>8</th>
      <td>estetica e imagem pessoal</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>1583</th>
      <td>eventos</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>1159</th>
      <td>fabricacao mecanica</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>1429</th>
      <td>fotografia</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>3031</th>
      <td>gestao da ti</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>515</th>
      <td>gestao de seguranca privada</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>1126</th>
      <td>gestao de ti</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>29</th>
      <td>gestao de turismo</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>46</th>
      <td>gestao do agronegocio</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>618</th>
      <td>jogos digitais</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>180</th>
      <td>jornalismo</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>21</th>
      <td>marketing digital</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>984</th>
      <td>mecatronica industrial</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>2637</th>
      <td>pilotagem profissional de aeronaves</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>361</th>
      <td>producao audiovisual</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>1896</th>
      <td>producao multimidia</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>32</th>
      <td>publicidade e propaganda</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>601</th>
      <td>relacoes publicas</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>583</th>
      <td>secretariado executivo bilingue</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>6560</th>
      <td>seguranca do trabalho</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>106</th>
      <td>seguranca publica</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>114</th>
      <td>servicos juridicos, cartorarios e notariais</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>176</th>
      <td>sistemas de informacao</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>1699</th>
      <td>sistemas para internet</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>112</th>
      <td>sociologia</td>
      <td>LIC</td>
    </tr>
  </tbody>
</table>
</div>



##### Cursos ENADE e Área Padronizada


```python
df_cursos_enade = df_cursos_enade[df_cursos_enade.ano_enade == ANO_ENADE]
df_cursos_enade[['nome_curso_edital', 'area_padronizada']].sort_values('nome_curso_edital')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nome_curso_edital</th>
      <th>area_padronizada</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>23</th>
      <td>agronegocio</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>0</th>
      <td>agronomia</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>1</th>
      <td>arquitetura e urbanismo</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>2</th>
      <td>biomedicina</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>3</th>
      <td>educacao fisica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>4</th>
      <td>enfermagem</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>5</th>
      <td>engenharia ambiental</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>6</th>
      <td>engenharia civil</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>7</th>
      <td>engenharia de alimentos</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>8</th>
      <td>engenharia de computacao</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>10</th>
      <td>engenharia de controle e automacao</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>9</th>
      <td>engenharia de producao</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>11</th>
      <td>engenharia eletrica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>12</th>
      <td>engenharia florestal</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>13</th>
      <td>engenharia mecanica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>14</th>
      <td>engenharia quimica</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>24</th>
      <td>estetica e cosmetica</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>15</th>
      <td>farmacia</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>16</th>
      <td>fisioterapia</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>17</th>
      <td>fonoaudiologia</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>25</th>
      <td>gestao ambiental</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>26</th>
      <td>gestao hospitalar</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>18</th>
      <td>medicina</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>19</th>
      <td>medicina veterinaria</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>20</th>
      <td>nutricao</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>21</th>
      <td>odontologia</td>
      <td>BCH</td>
    </tr>
    <tr>
      <th>27</th>
      <td>radiologia</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>28</th>
      <td>seguranca no trabalho</td>
      <td>TEC</td>
    </tr>
    <tr>
      <th>22</th>
      <td>zootecnia</td>
      <td>BCH</td>
    </tr>
  </tbody>
</table>
</div>



### Criação de lista de cursos não enadistas

##### Lista de cursos não enadistas


```python
DEPARA_CURSO_PADRONIZADO_NAO_ENADE = {
    'artes visuais': '',
    'automacao industrial': '',
    'banco de dados': '',
    'cartorarios e notariais': '',
    'ciencias aeronauticas': '',
    'ciencias economicas (economia)': '',
    'desenho industrial': '',
    'desenvolvimento em software': '',
    'eletrotecnica industrial': '',
    'embelezamento e imagem pessoal': '',       # Duvida Estética e Cosmética;
    'empreendedorismo': '',
    'estetica e imagem pessoal': '',            # Duvida Estética e Cosmética;
    'eventos': '',
    'fabricacao mecanica': '',
    'fotografia': '',
    'gestao de seguranca privada': '',
    'gestao de turismo': '',
    'gestao do agronegocio': '',
    'jogos digitais': '',
    'jornalismo': '',
    'marketing digital': '',
    'mecatronica industrial': '',
    'pilotagem profissional de aeronaves': '',
    'producao audiovisual': '',
    'producao multimidia': '',
    'publicidade e propaganda': '',
    'relacoes publicas': '',
    'secretariado executivo bilingue': '',
    'seguranca publica': '',
    'servicos juridicos': '', 
    'sistemas para internet':'' 
}
```

##### Lista DE PARA Cursos ENADE


```python
DEPARA_CURSO_PADRONIZADO_ENADE = {
'engenharia ambiental e sanitaria': 'engenharia ambiental',
'engenharia da computacao': 'engenharia de computacao',
# 'engenharia de minas': 'engenharia',
# 'engenharia de petroleo': 'engenharia',
# 'engenharia de producao mecanica': 'engenharia',
# 'engenharia eletronica': 'engenharia',
'engenharia mecatronica': 'engenharia de controle e automacao',
'seguranca do trabalho': 'seguranca no trabalho'
}
```

##### Premissas:

    - Checkagem dos registros que serão modificados;
    - Verificação se os cursos que serão modificados, realmente não foram modificados;
    - Não pode haver a inserção de um curso que já foi deparado;
    - Criação de variáveis para checkagem de modificção dos registros;
    - Curso inserido que não consta na lista de Cursos ENADE;


```python
curso_revisar = set(DEPARA_CURSO_PADRONIZADO_ENADE.values())\
                                       .difference(set(df_cursos_enade.nome_curso_edital[df_cursos_enade.ano_enade == ANO_ENADE]))
curso_revisar = str(curso_revisar).replace('{', '').replace('}', '')
```


```python
assert(str(set(DEPARA_CURSO_PADRONIZADO_ENADE.values())\
                                       .difference(set(df_cursos_enade.nome_curso_edital[df_cursos_enade.ano_enade == ANO_ENADE]))) == 'set()'), \
        'Verificar a lista de curso inserida na etapa de DEPARA, {} inserido para modificação não consta na lista de cursos ENADE, revise por favor'.format(curso_revisar)

print('Verificação realizada com sucesso')
```

    Verificação realizada com sucesso


##### Verificação se o registro inserido para que seja feita a modificação existe na base de cursos ENADE


```python
set(DEPARA_CURSO_PADRONIZADO_ENADE.keys())
```




    {'engenharia ambiental e sanitaria',
     'engenharia da computacao',
     'engenharia mecatronica',
     'seguranca do trabalho'}




```python
set(DEPARA_CURSO_PADRONIZADO_ENADE.keys()).difference(set(CURSOS_ENADE))
```




    {'engenharia ambiental e sanitaria',
     'engenharia da computacao',
     'engenharia mecatronica',
     'seguranca do trabalho'}




```python
CURSOS_ATIVOS_DIFERENCA_CONTAGEM = len(set(DEPARA_CURSO_PADRONIZADO_ENADE.keys())\
                                       .difference(set(CURSOS_ENADE)))

DEPARA_CURSO_PADRONIZADO_ENADE_CONTAGEM = len(DEPARA_CURSO_PADRONIZADO_ENADE.keys())

assert(CURSOS_ATIVOS_DIFERENCA_CONTAGEM == DEPARA_CURSO_PADRONIZADO_ENADE_CONTAGEM), \
        'Verificar a lista de curso inserida na etapa de DEPARA, algum registro inserido para modificação não consta na lista de cursos ENADE, revise por favor'

print('Verificação realizada com sucesso"')
```

    Verificação realizada com sucesso"


##### Criação de chave para filtragem do dataframe contendo os cursos que serão deparados


```python
chaves_dicionario = set(DEPARA_CURSO_PADRONIZADO_ENADE.keys())
```

##### Dividir o dataframe para que o depara seja aplicado, a coluna de curso_padronizado será replicada para que seja mantida a rastreabilidade


```python
df_cursos_ativos['curso_padronizado_old'] = df_cursos_ativos['curso_padronizado']

filtro_curso_deparado = df_cursos_ativos['curso_padronizado_old'].isin(chaves_dicionario)
```

##### Aplicação do DE PARA


```python
df_cursos_ativos['curso_padronizado'] = df_cursos_ativos.curso_padronizado.apply(apply_depara(DEPARA_CURSO_PADRONIZADO_ENADE))
```

##### Conferência dos cursos deparados


```python
df_cursos_ativos[filtro_curso_deparado][['curso_padronizado', 'curso_padronizado_old']].drop_duplicates()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>curso_padronizado</th>
      <th>curso_padronizado_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>196</th>
      <td>engenharia ambiental</td>
      <td>engenharia ambiental e sanitaria</td>
    </tr>
    <tr>
      <th>260</th>
      <td>engenharia de computacao</td>
      <td>engenharia da computacao</td>
    </tr>
    <tr>
      <th>2930</th>
      <td>engenharia de controle e automacao</td>
      <td>engenharia mecatronica</td>
    </tr>
    <tr>
      <th>6560</th>
      <td>seguranca no trabalho</td>
      <td>seguranca do trabalho</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_cursos_ativos.loc[filtro_curso_deparado, 'FLAG_NOME_CURSO_PADRONIZADO_DEPARADO'] = True
```

### Cursos com nome alterados pelo DE PARA


```python
df_cursos_ativos[filtro_curso_deparado]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
      <th>curso_padronizado_old</th>
      <th>FLAG_NOME_CURSO_PADRONIZADO_DEPARADO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>196</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>508</td>
      <td>4362</td>
      <td>4493</td>
      <td>120422</td>
      <td>Engenharia Ambiental e Sanitária - M</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia ambiental e sanitaria</td>
      <td>True</td>
    </tr>
    <tr>
      <th>197</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>508</td>
      <td>4362</td>
      <td>67695</td>
      <td>120422</td>
      <td>Engenharia Ambiental e Sanitária - N</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia ambiental e sanitaria</td>
      <td>True</td>
    </tr>
    <tr>
      <th>218</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>532</td>
      <td>13743</td>
      <td>69117</td>
      <td>1070320</td>
      <td>Engenharia Ambiental e Sanitária - N</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia ambiental e sanitaria</td>
      <td>True</td>
    </tr>
    <tr>
      <th>260</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>503</td>
      <td>1492</td>
      <td>3848</td>
      <td>1284127</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>274</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>573</td>
      <td>891</td>
      <td>4186</td>
      <td>1280504</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>324</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>600</td>
      <td>5288</td>
      <td>12640</td>
      <td>1280475</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>336</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>596</td>
      <td>5555</td>
      <td>12312</td>
      <td>1321971</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>339</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>601</td>
      <td>376</td>
      <td>12687</td>
      <td>1323716</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>428</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>608</td>
      <td>671</td>
      <td>13114</td>
      <td>41701</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>610</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>502</td>
      <td>1632</td>
      <td>3839</td>
      <td>1281009</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>619</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>8</td>
      <td>2037</td>
      <td>4230</td>
      <td>1322106</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>630</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>552</td>
      <td>298</td>
      <td>99257</td>
      <td>38809</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>665</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>659</td>
      <td>5216</td>
      <td>16336</td>
      <td>1118154</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>708</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>592</td>
      <td>4826</td>
      <td>12002</td>
      <td>1280610</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>843</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>770</td>
      <td>242</td>
      <td>13535</td>
      <td>1403875</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>868</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>666</td>
      <td>376</td>
      <td>16664</td>
      <td>1403866</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>923</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>508</td>
      <td>4362</td>
      <td>2893</td>
      <td>120422</td>
      <td>Engenharia Ambiental e Sanitária - Mista - M</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia ambiental e sanitaria</td>
      <td>True</td>
    </tr>
    <tr>
      <th>997</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>502</td>
      <td>1632</td>
      <td>3838</td>
      <td>1281009</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1012</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>8</td>
      <td>2037</td>
      <td>4231</td>
      <td>1322106</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1047</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>573</td>
      <td>891</td>
      <td>10706</td>
      <td>1280504</td>
      <td>Engenharia da Computação - Mista - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1109</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>603</td>
      <td>2191</td>
      <td>12832</td>
      <td>1280516</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1150</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>583</td>
      <td>1412</td>
      <td>11464</td>
      <td>49107</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1257</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>597</td>
      <td>1345</td>
      <td>91706</td>
      <td>1321778</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1258</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>770</td>
      <td>242</td>
      <td>35269</td>
      <td>1403875</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1276</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>627</td>
      <td>781</td>
      <td>14095</td>
      <td>1280518</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1401</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>6</td>
      <td>3034</td>
      <td>4804</td>
      <td>1304009</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1434</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>503</td>
      <td>1492</td>
      <td>89449</td>
      <td>1284127</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1509</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>595</td>
      <td>5550</td>
      <td>12197</td>
      <td>1280248</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1510</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>595</td>
      <td>5550</td>
      <td>12196</td>
      <td>1280248</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1514</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>644</td>
      <td>3603</td>
      <td>15904</td>
      <td>1280593</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1798</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>532</td>
      <td>13743</td>
      <td>30541</td>
      <td>1070320</td>
      <td>Engenharia Ambiental e Sanitária - Mista - M</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia ambiental e sanitaria</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1827</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>519</td>
      <td>4865</td>
      <td>24186</td>
      <td>1322136</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1856</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>552</td>
      <td>298</td>
      <td>2896</td>
      <td>38809</td>
      <td>Engenharia da Computação - Mista - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1866</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>573</td>
      <td>891</td>
      <td>4187</td>
      <td>1280504</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1933</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>596</td>
      <td>5555</td>
      <td>12311</td>
      <td>1321971</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>663</td>
      <td>376</td>
      <td>16526</td>
      <td>1403869</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2088</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>591</td>
      <td>4652</td>
      <td>11932</td>
      <td>1303692</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2475</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>537</td>
      <td>1774</td>
      <td>95947</td>
      <td>1330520</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2516</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>503</td>
      <td>1492</td>
      <td>67596</td>
      <td>5000206</td>
      <td>Engenharia Ambiental e Sanitária - N</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia ambiental e sanitaria</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2676</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>771</td>
      <td>780</td>
      <td>3047</td>
      <td>1266093</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2688</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>519</td>
      <td>4865</td>
      <td>8898</td>
      <td>1322136</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2711</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>552</td>
      <td>298</td>
      <td>99260</td>
      <td>38809</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2714</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>510</td>
      <td>2271</td>
      <td>4513</td>
      <td>1280279</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2852</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>583</td>
      <td>1412</td>
      <td>11463</td>
      <td>49107</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2899</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>608</td>
      <td>671</td>
      <td>82409</td>
      <td>41701</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2919</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>630</td>
      <td>5303</td>
      <td>28778</td>
      <td>1330449</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2930</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>602</td>
      <td>4141</td>
      <td>12789</td>
      <td>90899</td>
      <td>Engenharia Mecatrônica - N</td>
      <td>BCH</td>
      <td>engenharia de controle e automacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia mecatronica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2973</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>594</td>
      <td>4656</td>
      <td>12132</td>
      <td>1280493</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2980</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>636</td>
      <td>457</td>
      <td>89625</td>
      <td>1324017</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3110</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>771</td>
      <td>780</td>
      <td>3048</td>
      <td>1266093</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3117</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>6</td>
      <td>3034</td>
      <td>4802</td>
      <td>1304009</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3232</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>603</td>
      <td>2191</td>
      <td>12831</td>
      <td>1280516</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3235</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>592</td>
      <td>4826</td>
      <td>85595</td>
      <td>1280610</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3394</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>667</td>
      <td>376</td>
      <td>79515</td>
      <td>1403872</td>
      <td>Engenharia da Computação - M</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3395</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>667</td>
      <td>376</td>
      <td>16729</td>
      <td>1403872</td>
      <td>Engenharia da Computação - N</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3814</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>EAD</td>
      <td>671</td>
      <td>ECOQUINPI</td>
      <td>1318199</td>
      <td>Engenharia da Computação</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3956</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>EAD</td>
      <td>671</td>
      <td>EGCOTQUANI</td>
      <td>1318199</td>
      <td>Engenharia da Computação</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6560</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FNT</td>
      <td>671</td>
      <td>TSTRQUINI</td>
      <td>1382661</td>
      <td>Tecnologia em Segurança do Trabalho</td>
      <td>TEC</td>
      <td>seguranca no trabalho</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>seguranca do trabalho</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6651</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>EAD</td>
      <td>671</td>
      <td>EGCOTERNI</td>
      <td>1318199</td>
      <td>Engenharia da Computação</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>engenharia da computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6657</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FJK</td>
      <td>671</td>
      <td>TSTRQUINI</td>
      <td>1382661</td>
      <td>Tecnologia em Segurança do Trabalho</td>
      <td>TEC</td>
      <td>seguranca no trabalho</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>seguranca do trabalho</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>





###### Lista de Cursos Bacharel que são ENADE


```python
list_cursos_bacharelado_enade = [
    'administracao',
    'administracao publica',
    'agronomia',
    'arquitetura e urbanismo',
    'biomedicina',
    'ciencia da computacao',
    'ciencias biologicas',
    'ciencias contabeis',
    'ciencias economicas',
    'ciencias sociais',
    'comunicacao social - jornalismo',
    'comunicacao social - publicidade e propaganda',
    'design',
    'direito',
    'educacao fisica',
    'enfermagem',
    'engenharia',
    'engenharia ambiental',
    'engenharia civil',
    'engenharia de alimentos',
    'engenharia de computacao',
    'engenharia de controle e automacao',
    'engenharia de producao',
    'engenharia eletrica',
    'engenharia florestal',
    'engenharia mecanica',
    'engenharia quimica',
    'farmacia',
    'filosofia',
    'fisica',
    'fisioterapia',
    'fonoaudiologia',
    'geografia',
    'historia',
    'letras - portugues',
    'matematica',
    'medicina',
    'medicina veterinaria',
    'nutricao',
    'odontologia',
    'psicologia',
    'quimica',
    'relacoes internacionais',
    'secretariado executivo',
    'servico social',
    'sistema de informacao',
    'teologia',
    'turismo',
    'zootecnia'
]
```


```python
filtro_curso_deparado_bch = df_cursos_ativos['curso_padronizado_old'].isin(list_cursos_bacharelado_enade)
```


```python
depara_bacharelado = {
    "ciencias economicas (economia)": "ciencias economicas",
    "engenharia ambiental e sanitaria": "engenharia ambiental",     # DEPARA Cursos elegíveis 2017
    "engenharia da computacao": "engenharia de computacao",         # DEPARA Cursos elegíveis 2017
    "engenharia de minas": "engenharia",                            # DEPARA Cursos elegíveis 2017
    "engenharia de petroleo": "engenharia",                         # DEPARA Cursos elegíveis 2017
    "engenharia de producao mecanica": "engenharia",                # DEPARA Cursos elegíveis 2017
    "engenharia eletronica": "engenharia",                          # DEPARA Cursos elegíveis 2017
    "engenharia mecatronica": "engenharia de controle e automacao", # DEPARA Cursos elegíveis 2017
    "jornalismo": "comunicacao social - jornalismo",
    "publicidade e propaganda": "comunicacao social - publicidade e propaganda",
    "sistemas de informacao": "sistema de informacao"
}
```


```python
not_evaluated_bacharelado = {
    "artes visuais",         # O enquadramento de 2017 estava correto?
    "ciencias aeronauticas", # não está enquandrado
    "desenho industrial",    # não está enquandrado 
    "relacoes publicas"      # não está enquandrado 
}
```

##### Aplicação do DE PARA


```python
df_cursos_ativos['curso_padronizado'] = df_cursos_ativos.curso_padronizado.apply(apply_depara(depara_bacharelado))
```


```python
df_cursos_ativos[filtro_curso_deparado_bch][['curso_padronizado', 'curso_padronizado_old']].drop_duplicates()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>curso_padronizado</th>
      <th>curso_padronizado_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>administracao</td>
      <td>administracao</td>
    </tr>
    <tr>
      <th>2</th>
      <td>servico social</td>
      <td>servico social</td>
    </tr>
    <tr>
      <th>4</th>
      <td>educacao fisica</td>
      <td>educacao fisica</td>
    </tr>
    <tr>
      <th>6</th>
      <td>filosofia</td>
      <td>filosofia</td>
    </tr>
    <tr>
      <th>7</th>
      <td>letras - portugues</td>
      <td>letras - portugues</td>
    </tr>
    <tr>
      <th>11</th>
      <td>fisioterapia</td>
      <td>fisioterapia</td>
    </tr>
    <tr>
      <th>12</th>
      <td>historia</td>
      <td>historia</td>
    </tr>
    <tr>
      <th>13</th>
      <td>fisica</td>
      <td>fisica</td>
    </tr>
    <tr>
      <th>15</th>
      <td>geografia</td>
      <td>geografia</td>
    </tr>
    <tr>
      <th>17</th>
      <td>engenharia eletrica</td>
      <td>engenharia eletrica</td>
    </tr>
    <tr>
      <th>22</th>
      <td>engenharia mecanica</td>
      <td>engenharia mecanica</td>
    </tr>
    <tr>
      <th>38</th>
      <td>agronomia</td>
      <td>agronomia</td>
    </tr>
    <tr>
      <th>41</th>
      <td>matematica</td>
      <td>matematica</td>
    </tr>
    <tr>
      <th>48</th>
      <td>ciencias contabeis</td>
      <td>ciencias contabeis</td>
    </tr>
    <tr>
      <th>52</th>
      <td>quimica</td>
      <td>quimica</td>
    </tr>
    <tr>
      <th>55</th>
      <td>ciencias biologicas</td>
      <td>ciencias biologicas</td>
    </tr>
    <tr>
      <th>65</th>
      <td>engenharia de computacao</td>
      <td>engenharia de computacao</td>
    </tr>
    <tr>
      <th>73</th>
      <td>enfermagem</td>
      <td>enfermagem</td>
    </tr>
    <tr>
      <th>76</th>
      <td>nutricao</td>
      <td>nutricao</td>
    </tr>
    <tr>
      <th>77</th>
      <td>engenharia civil</td>
      <td>engenharia civil</td>
    </tr>
    <tr>
      <th>94</th>
      <td>engenharia de producao</td>
      <td>engenharia de producao</td>
    </tr>
    <tr>
      <th>95</th>
      <td>arquitetura e urbanismo</td>
      <td>arquitetura e urbanismo</td>
    </tr>
    <tr>
      <th>120</th>
      <td>ciencia da computacao</td>
      <td>ciencia da computacao</td>
    </tr>
    <tr>
      <th>121</th>
      <td>engenharia ambiental</td>
      <td>engenharia ambiental</td>
    </tr>
    <tr>
      <th>123</th>
      <td>odontologia</td>
      <td>odontologia</td>
    </tr>
    <tr>
      <th>125</th>
      <td>farmacia</td>
      <td>farmacia</td>
    </tr>
    <tr>
      <th>129</th>
      <td>biomedicina</td>
      <td>biomedicina</td>
    </tr>
    <tr>
      <th>137</th>
      <td>psicologia</td>
      <td>psicologia</td>
    </tr>
    <tr>
      <th>152</th>
      <td>direito</td>
      <td>direito</td>
    </tr>
    <tr>
      <th>186</th>
      <td>medicina</td>
      <td>medicina</td>
    </tr>
    <tr>
      <th>191</th>
      <td>engenharia de controle e automacao</td>
      <td>engenharia de controle e automacao</td>
    </tr>
    <tr>
      <th>229</th>
      <td>fonoaudiologia</td>
      <td>fonoaudiologia</td>
    </tr>
    <tr>
      <th>235</th>
      <td>engenharia quimica</td>
      <td>engenharia quimica</td>
    </tr>
    <tr>
      <th>387</th>
      <td>medicina veterinaria</td>
      <td>medicina veterinaria</td>
    </tr>
    <tr>
      <th>1067</th>
      <td>design</td>
      <td>design</td>
    </tr>
    <tr>
      <th>1476</th>
      <td>turismo</td>
      <td>turismo</td>
    </tr>
    <tr>
      <th>2166</th>
      <td>engenharia florestal</td>
      <td>engenharia florestal</td>
    </tr>
    <tr>
      <th>2422</th>
      <td>relacoes internacionais</td>
      <td>relacoes internacionais</td>
    </tr>
    <tr>
      <th>3684</th>
      <td>ciencias economicas</td>
      <td>ciencias economicas</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_cursos_ativos.loc[filtro_curso_deparado_bch, 'FLAG_NOME_CURSO_PADRONIZADO_DEPARADO'] = True
```

### Cursos com nome alterados pelo DE PARA


```python
df_cursos_ativos[filtro_curso_deparado_bch]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
      <th>curso_padronizado_old</th>
      <th>FLAG_NOME_CURSO_PADRONIZADO_DEPARADO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>44</td>
      <td>97980</td>
      <td>ADMINISTRAÇÃO</td>
      <td>BCH</td>
      <td>administracao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>administracao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>47</td>
      <td>97990</td>
      <td>SERVIÇO SOCIAL</td>
      <td>BCH</td>
      <td>servico social</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>servico social</td>
      <td>True</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SO</td>
      <td>1268023</td>
      <td>FORMAÇÃO PEDAGÓGICA EM EDUCAÇÃO FÍSICA</td>
      <td>NO_DEGREE</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>60</td>
      <td>NaN</td>
      <td>FILOSOFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>filosofia</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>filosofia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2SH</td>
      <td>89379</td>
      <td>FORMAÇÃO PEDAGÓGICA EM LETRAS - PORTUGUÊS</td>
      <td>NO_DEGREE</td>
      <td>letras - portugues</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>letras - portugues</td>
      <td>True</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>7MB</td>
      <td>1404111</td>
      <td>FISIOTERAPIA - BACHARELADO</td>
      <td>BCH</td>
      <td>fisioterapia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>fisioterapia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>5S8</td>
      <td>97986</td>
      <td>2ª LICENCIATURA EM HISTÓRIA</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>7MD</td>
      <td>NaN</td>
      <td>FÍSICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>fisica</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2SM</td>
      <td>1420102</td>
      <td>FORMAÇÃO PEDAGÓGICA EM FÍSICA</td>
      <td>NO_DEGREE</td>
      <td>fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>183</td>
      <td>1190156</td>
      <td>GEOGRAFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>352</td>
      <td>1268023</td>
      <td>EDUCAÇÃO FÍSICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2ON</td>
      <td>1357953</td>
      <td>ENGENHARIA ELÉTRICA</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>22</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2OO</td>
      <td>1357883</td>
      <td>ENGENHARIA MECÂNICA</td>
      <td>BCH</td>
      <td>engenharia mecanica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia mecanica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>25</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SM</td>
      <td>1420102</td>
      <td>FORMAÇÃO PEDAGÓGICA EM FÍSICA</td>
      <td>NO_DEGREE</td>
      <td>fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>26</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2ON</td>
      <td>1357953</td>
      <td>ENGENHARIA ELÉTRICA</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>27</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>183</td>
      <td>1190156</td>
      <td>GEOGRAFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>31</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2QM</td>
      <td>1374069</td>
      <td>EDUCAÇÃO FÍSICA - BACHARELADO</td>
      <td>BCH</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>38</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>7MA</td>
      <td>1420100</td>
      <td>AGRONOMIA - BACHARELADO</td>
      <td>BCH</td>
      <td>agronomia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>agronomia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>41</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SL</td>
      <td>1190159</td>
      <td>FORMAÇÃO PEDAGÓGICA EM MATEMÁTICA</td>
      <td>NO_DEGREE</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>42</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SE</td>
      <td>97986</td>
      <td>FORMAÇÃO PEDAGÓGICA EM HISTÓRIA</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>43</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SH</td>
      <td>89379</td>
      <td>FORMAÇÃO PEDAGÓGICA EM LETRAS - PORTUGUÊS</td>
      <td>NO_DEGREE</td>
      <td>letras - portugues</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>letras - portugues</td>
      <td>True</td>
    </tr>
    <tr>
      <th>44</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>46</td>
      <td>97986</td>
      <td>HISTÓRIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>48</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>45</td>
      <td>97982</td>
      <td>CIÊNCIAS CONTÁBEIS</td>
      <td>BCH</td>
      <td>ciencias contabeis</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>ciencias contabeis</td>
      <td>True</td>
    </tr>
    <tr>
      <th>52</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>7MC</td>
      <td>NaN</td>
      <td>QUÍMICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>quimica</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>quimica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>55</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SD</td>
      <td>1190061</td>
      <td>FORMAÇÃO PEDAGÓGICA EM CIÊNCIAS BIOLÓGICAS</td>
      <td>NO_DEGREE</td>
      <td>ciencias biologicas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>ciencias biologicas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>56</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SG</td>
      <td>1190156</td>
      <td>FORMAÇÃO PEDAGÓGICA EM GEOGRAFIA</td>
      <td>NO_DEGREE</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>57</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>60</td>
      <td>NaN</td>
      <td>FILOSOFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>filosofia</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>filosofia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>61</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>5SB</td>
      <td>1420101</td>
      <td>2ª LICENCIATURA EM QUÍMICA</td>
      <td>NO_DEGREE</td>
      <td>quimica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>quimica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>65</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>794</td>
      <td>1322923</td>
      <td>ENGENHARIA DE COMPUTAÇÃO</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia de computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>67</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>184</td>
      <td>1190159</td>
      <td>MATEMÁTICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7264</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FJK</td>
      <td>671</td>
      <td>LMTQUINI</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7265</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FCB</td>
      <td>671</td>
      <td>CESW</td>
      <td>1382659</td>
      <td>Ciências Econômicas</td>
      <td>BCH</td>
      <td>ciencias economicas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>ciencias economicas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7266</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPJ</td>
      <td>671</td>
      <td>LHISQUINI</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7268</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FA3</td>
      <td>671</td>
      <td>CTQUANI</td>
      <td>89309</td>
      <td>Ciências Contábeis</td>
      <td>BCH</td>
      <td>ciencias contabeis</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>ciencias contabeis</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7274</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FFA</td>
      <td>671</td>
      <td>FPELETRW</td>
      <td>87237</td>
      <td>Formação Pedagógica em Letras - Português</td>
      <td>NO_DEGREE</td>
      <td>letras - portugues</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>letras - portugues</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7276</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPD</td>
      <td>671</td>
      <td>CTSW</td>
      <td>89309</td>
      <td>Ciências Contábeis</td>
      <td>BCH</td>
      <td>ciencias contabeis</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>ciencias contabeis</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7278</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UT2</td>
      <td>671</td>
      <td>LHISTSEGNI</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7282</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSB</td>
      <td>671</td>
      <td>FPEQMCAW</td>
      <td>averificar</td>
      <td>Formação Pedagógica em Química</td>
      <td>NO_DEGREE</td>
      <td>quimica</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>quimica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7283</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FKA</td>
      <td>671</td>
      <td>GEOW</td>
      <td>1298413</td>
      <td>Geografia - Licenciatura</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7287</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAS</td>
      <td>671</td>
      <td>LMTW</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7291</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FDO</td>
      <td>671</td>
      <td>MATW</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7294</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CIP</td>
      <td>671</td>
      <td>LGEW</td>
      <td>1298413</td>
      <td>Geografia - Licenciatura</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7299</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSJ</td>
      <td>671</td>
      <td>FPEMATW</td>
      <td>1298841</td>
      <td>Formação Pedagógica em Matemática</td>
      <td>NO_DEGREE</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7302</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FST</td>
      <td>671</td>
      <td>FPEHISTOW</td>
      <td>1298770</td>
      <td>Formação Pedagógica em História</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7303</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CPL</td>
      <td>671</td>
      <td>HISTQUINI</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7309</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FEC</td>
      <td>671</td>
      <td>ADQUANI</td>
      <td>87284</td>
      <td>Administração</td>
      <td>BCH</td>
      <td>administracao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>administracao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7311</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UDP</td>
      <td>671</td>
      <td>ADSNOTI</td>
      <td>87284</td>
      <td>Administração</td>
      <td>BCH</td>
      <td>administracao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>administracao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7313</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FA3</td>
      <td>671</td>
      <td>HISTW</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7317</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAI</td>
      <td>671</td>
      <td>EGCVTERNI</td>
      <td>1295689</td>
      <td>Engenharia Civil</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7318</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSO</td>
      <td>671</td>
      <td>HISTW</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7319</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FEC</td>
      <td>671</td>
      <td>CTTERNI</td>
      <td>89309</td>
      <td>Ciências Contábeis</td>
      <td>BCH</td>
      <td>ciencias contabeis</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>ciencias contabeis</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7321</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAT</td>
      <td>671</td>
      <td>CESW</td>
      <td>1382659</td>
      <td>Ciências Econômicas</td>
      <td>BCH</td>
      <td>ciencias economicas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>ciencias economicas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7322</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CIL</td>
      <td>671</td>
      <td>GEOW</td>
      <td>1298413</td>
      <td>Geografia - Licenciatura</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7323</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FED</td>
      <td>671</td>
      <td>EGETERNPI</td>
      <td>1296028</td>
      <td>Engenharia Elétrica</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7332</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FED</td>
      <td>671</td>
      <td>NUTQMPI</td>
      <td>1382623</td>
      <td>Nutrição</td>
      <td>BCH</td>
      <td>nutricao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>nutricao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7338</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FRP</td>
      <td>671</td>
      <td>SERSW</td>
      <td>97573</td>
      <td>Serviço Social</td>
      <td>BCH</td>
      <td>servico social</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>servico social</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7341</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FNI</td>
      <td>671</td>
      <td>FPEHISW</td>
      <td>1298770</td>
      <td>Formação Pedagógica em História</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7348</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FDO</td>
      <td>671</td>
      <td>SERSENOTI</td>
      <td>97573</td>
      <td>Serviço Social</td>
      <td>BCH</td>
      <td>servico social</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>servico social</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7352</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPE</td>
      <td>671</td>
      <td>MATW</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7355</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UDP</td>
      <td>671</td>
      <td>ADSADIUI</td>
      <td>87284</td>
      <td>Administração</td>
      <td>BCH</td>
      <td>administracao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>administracao</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
<p>4095 rows × 19 columns</p>
</div>



###### Lista de Cursos Licenciatura que são ENADE


```python
list_cursos_licenciatura_enade = [
    "analise e desenvolvimento de sistemas",
    "artes visuais",
    "ciencia da computacao",
    "ciencias biologicas",
    "ciencias sociais",
    "educacao fisica",
    "filosofia",
    "fisica",
    "geografia",
    "gestao da producao industrial",
    "gestao da tecnologia da informacao",
    "historia",
    "letras - ingles",
    "letras - portugues",
    "letras - portugues e espanhol",
    "letras - portugues e ingles",
    "matematica",
    "musica",
    "pedagogia",
    "quimica",
    # "redes de computadores"
]
```


```python
filtro_curso_deparado_lic = df_cursos_ativos['curso_padronizado_old'].isin(list_cursos_licenciatura_enade)
```


```python
depara_licenciatura = {
'gestao da ti': 'gestao da tecnologia da informacao',  
'gestao de ti': 'gestao da tecnologia da informacao',
'sistemas de informacao': 'sistema de informacao'
}
```


```python
not_evaluated_licenciatura = {'sociologia',                   # não está enquandrado
                              'letras - espanhol'             # não está enquandrado
                             }
```

##### Aplicação do DE PARA


```python
df_cursos_ativos['curso_padronizado'] = df_cursos_ativos.curso_padronizado.apply(apply_depara(depara_licenciatura))
```


```python
df_cursos_ativos[filtro_curso_deparado_lic][['curso_padronizado', 'curso_padronizado_old']].drop_duplicates()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>curso_padronizado</th>
      <th>curso_padronizado_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>educacao fisica</td>
      <td>educacao fisica</td>
    </tr>
    <tr>
      <th>5</th>
      <td>pedagogia</td>
      <td>pedagogia</td>
    </tr>
    <tr>
      <th>6</th>
      <td>filosofia</td>
      <td>filosofia</td>
    </tr>
    <tr>
      <th>7</th>
      <td>letras - portugues</td>
      <td>letras - portugues</td>
    </tr>
    <tr>
      <th>9</th>
      <td>analise e desenvolvimento de sistemas</td>
      <td>analise e desenvolvimento de sistemas</td>
    </tr>
    <tr>
      <th>12</th>
      <td>historia</td>
      <td>historia</td>
    </tr>
    <tr>
      <th>13</th>
      <td>fisica</td>
      <td>fisica</td>
    </tr>
    <tr>
      <th>15</th>
      <td>geografia</td>
      <td>geografia</td>
    </tr>
    <tr>
      <th>23</th>
      <td>letras - portugues e ingles</td>
      <td>letras - portugues e ingles</td>
    </tr>
    <tr>
      <th>28</th>
      <td>letras - portugues e espanhol</td>
      <td>letras - portugues e espanhol</td>
    </tr>
    <tr>
      <th>41</th>
      <td>matematica</td>
      <td>matematica</td>
    </tr>
    <tr>
      <th>49</th>
      <td>letras - ingles</td>
      <td>letras - ingles</td>
    </tr>
    <tr>
      <th>52</th>
      <td>quimica</td>
      <td>quimica</td>
    </tr>
    <tr>
      <th>55</th>
      <td>ciencias biologicas</td>
      <td>ciencias biologicas</td>
    </tr>
    <tr>
      <th>58</th>
      <td>gestao da producao industrial</td>
      <td>gestao da producao industrial</td>
    </tr>
    <tr>
      <th>62</th>
      <td>artes visuais</td>
      <td>artes visuais</td>
    </tr>
    <tr>
      <th>120</th>
      <td>ciencia da computacao</td>
      <td>ciencia da computacao</td>
    </tr>
    <tr>
      <th>453</th>
      <td>musica</td>
      <td>musica</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_cursos_ativos.loc[filtro_curso_deparado_lic, 'FLAG_NOME_CURSO_PADRONIZADO_DEPARADO'] = True
```

### Cursos com nome alterados pelo DE PARA


```python
df_cursos_ativos[filtro_curso_deparado_lic]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
      <th>curso_padronizado_old</th>
      <th>FLAG_NOME_CURSO_PADRONIZADO_DEPARADO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SO</td>
      <td>1268023</td>
      <td>FORMAÇÃO PEDAGÓGICA EM EDUCAÇÃO FÍSICA</td>
      <td>NO_DEGREE</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>39</td>
      <td>89380</td>
      <td>PEDAGOGIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>pedagogia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>pedagogia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>60</td>
      <td>NaN</td>
      <td>FILOSOFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>filosofia</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>filosofia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2SH</td>
      <td>89379</td>
      <td>FORMAÇÃO PEDAGÓGICA EM LETRAS - PORTUGUÊS</td>
      <td>NO_DEGREE</td>
      <td>letras - portugues</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>letras - portugues</td>
      <td>True</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>62</td>
      <td>111090</td>
      <td>SUPERIOR DE TECNOLOGIA EM ANÁLISE E DESENVOLVI...</td>
      <td>TEC</td>
      <td>analise e desenvolvimento de sistemas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>analise e desenvolvimento de sistemas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>5S8</td>
      <td>97986</td>
      <td>2ª LICENCIATURA EM HISTÓRIA</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>7MD</td>
      <td>NaN</td>
      <td>FÍSICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>fisica</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2SM</td>
      <td>1420102</td>
      <td>FORMAÇÃO PEDAGÓGICA EM FÍSICA</td>
      <td>NO_DEGREE</td>
      <td>fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>183</td>
      <td>1190156</td>
      <td>GEOGRAFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>352</td>
      <td>1268023</td>
      <td>EDUCAÇÃO FÍSICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>23</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2T4</td>
      <td>NaN</td>
      <td>LETRAS - LICENCIATURA EM LÍNGUA PORTUGUESA E L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>25</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SM</td>
      <td>1420102</td>
      <td>FORMAÇÃO PEDAGÓGICA EM FÍSICA</td>
      <td>NO_DEGREE</td>
      <td>fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>27</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>183</td>
      <td>1190156</td>
      <td>GEOGRAFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>28</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>7ME</td>
      <td>1420104</td>
      <td>LETRAS - PORTUGUÊS E ESPANHOL - LICENCIATURA</td>
      <td>LIC</td>
      <td>letras - portugues e espanhol</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>letras - portugues e espanhol</td>
      <td>True</td>
    </tr>
    <tr>
      <th>31</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2QM</td>
      <td>1374069</td>
      <td>EDUCAÇÃO FÍSICA - BACHARELADO</td>
      <td>BCH</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>37</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>62</td>
      <td>111090</td>
      <td>SUPERIOR DE TECNOLOGIA EM ANÁLISE E DESENVOLVI...</td>
      <td>TEC</td>
      <td>analise e desenvolvimento de sistemas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>analise e desenvolvimento de sistemas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>41</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SL</td>
      <td>1190159</td>
      <td>FORMAÇÃO PEDAGÓGICA EM MATEMÁTICA</td>
      <td>NO_DEGREE</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>42</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SE</td>
      <td>97986</td>
      <td>FORMAÇÃO PEDAGÓGICA EM HISTÓRIA</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>43</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SH</td>
      <td>89379</td>
      <td>FORMAÇÃO PEDAGÓGICA EM LETRAS - PORTUGUÊS</td>
      <td>NO_DEGREE</td>
      <td>letras - portugues</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>letras - portugues</td>
      <td>True</td>
    </tr>
    <tr>
      <th>44</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>46</td>
      <td>97986</td>
      <td>HISTÓRIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>49</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SI</td>
      <td>1420105</td>
      <td>FORMAÇÃO PEDAGÓGICA EM LETRAS - INGLÊS</td>
      <td>NO_DEGREE</td>
      <td>letras - ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>letras - ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>52</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>7MC</td>
      <td>NaN</td>
      <td>QUÍMICA - LICENCIATURA</td>
      <td>LIC</td>
      <td>quimica</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>quimica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>55</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SD</td>
      <td>1190061</td>
      <td>FORMAÇÃO PEDAGÓGICA EM CIÊNCIAS BIOLÓGICAS</td>
      <td>NO_DEGREE</td>
      <td>ciencias biologicas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>ciencias biologicas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>56</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SG</td>
      <td>1190156</td>
      <td>FORMAÇÃO PEDAGÓGICA EM GEOGRAFIA</td>
      <td>NO_DEGREE</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>57</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>60</td>
      <td>NaN</td>
      <td>FILOSOFIA - LICENCIATURA</td>
      <td>LIC</td>
      <td>filosofia</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>filosofia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>58</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>878</td>
      <td>13579</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO DA PRODUÇÃO I...</td>
      <td>TEC</td>
      <td>gestao da producao industrial</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>gestao da producao industrial</td>
      <td>True</td>
    </tr>
    <tr>
      <th>61</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>5SB</td>
      <td>1420101</td>
      <td>2ª LICENCIATURA EM QUÍMICA</td>
      <td>NO_DEGREE</td>
      <td>quimica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>quimica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>62</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>353</td>
      <td>1266926</td>
      <td>ARTES VISUAIS - LICENCIATURA</td>
      <td>LIC</td>
      <td>artes visuais</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>artes visuais</td>
      <td>True</td>
    </tr>
    <tr>
      <th>63</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>5SA</td>
      <td>89380</td>
      <td>2ª LICENCIATURA EM PEDAGOGIA</td>
      <td>NO_DEGREE</td>
      <td>pedagogia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>pedagogia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>66</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2SC</td>
      <td>1266926</td>
      <td>FORMAÇÃO PEDAGÓGICA EM ARTES VISUAIS</td>
      <td>NO_DEGREE</td>
      <td>artes visuais</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>COLABORAR</td>
      <td>True</td>
      <td>artes visuais</td>
      <td>True</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7264</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FJK</td>
      <td>671</td>
      <td>LMTQUINI</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7266</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPJ</td>
      <td>671</td>
      <td>LHISQUINI</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7271</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAV</td>
      <td>671</td>
      <td>LPIW</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7274</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FFA</td>
      <td>671</td>
      <td>FPELETRW</td>
      <td>87237</td>
      <td>Formação Pedagógica em Letras - Português</td>
      <td>NO_DEGREE</td>
      <td>letras - portugues</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>letras - portugues</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7275</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FIZ</td>
      <td>671</td>
      <td>PEDTERNI</td>
      <td>87280</td>
      <td>Pedagogia - Licenciatura</td>
      <td>LIC</td>
      <td>pedagogia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>pedagogia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7278</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UT2</td>
      <td>671</td>
      <td>LHISTSEGNI</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7279</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CPL</td>
      <td>671</td>
      <td>LTPILWEB</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7282</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSB</td>
      <td>671</td>
      <td>FPEQMCAW</td>
      <td>averificar</td>
      <td>Formação Pedagógica em Química</td>
      <td>NO_DEGREE</td>
      <td>quimica</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>quimica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7283</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FKA</td>
      <td>671</td>
      <td>GEOW</td>
      <td>1298413</td>
      <td>Geografia - Licenciatura</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7287</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAS</td>
      <td>671</td>
      <td>LMTW</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7288</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FBO</td>
      <td>671</td>
      <td>LPIQUINI</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7289</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSJ</td>
      <td>671</td>
      <td>TGPITERNI</td>
      <td>1363727</td>
      <td>Tecnologia em Gestão da Produção Industrial</td>
      <td>TEC</td>
      <td>gestao da producao industrial</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao da producao industrial</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7291</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FDO</td>
      <td>671</td>
      <td>MATW</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7294</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CIP</td>
      <td>671</td>
      <td>LGEW</td>
      <td>1298413</td>
      <td>Geografia - Licenciatura</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7299</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSJ</td>
      <td>671</td>
      <td>FPEMATW</td>
      <td>1298841</td>
      <td>Formação Pedagógica em Matemática</td>
      <td>NO_DEGREE</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7300</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPR</td>
      <td>671</td>
      <td>TASIW</td>
      <td>1194058</td>
      <td>Tecnologia em Análise e Desenvolvimento de Sis...</td>
      <td>TEC</td>
      <td>analise e desenvolvimento de sistemas</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>analise e desenvolvimento de sistemas</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7302</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FST</td>
      <td>671</td>
      <td>FPEHISTOW</td>
      <td>1298770</td>
      <td>Formação Pedagógica em História</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7303</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CPL</td>
      <td>671</td>
      <td>HISTQUINI</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7304</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FCI</td>
      <td>671</td>
      <td>PEDW</td>
      <td>87280</td>
      <td>Pedagogia - Licenciatura</td>
      <td>LIC</td>
      <td>pedagogia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>pedagogia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7313</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FA3</td>
      <td>671</td>
      <td>HISTW</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7318</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSO</td>
      <td>671</td>
      <td>HISTW</td>
      <td>1298770</td>
      <td>História - Licenciatura</td>
      <td>LIC</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7322</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CIL</td>
      <td>671</td>
      <td>GEOW</td>
      <td>1298413</td>
      <td>Geografia - Licenciatura</td>
      <td>LIC</td>
      <td>geografia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>geografia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7326</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CIP</td>
      <td>671</td>
      <td>LPIW</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7327</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FGO</td>
      <td>671</td>
      <td>LPIW</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7334</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UDP</td>
      <td>671</td>
      <td>AVISEGNI</td>
      <td>1404178</td>
      <td>Artes Visuais - Licenciatura</td>
      <td>LIC</td>
      <td>artes visuais</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>artes visuais</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7341</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FNI</td>
      <td>671</td>
      <td>FPEHISW</td>
      <td>1298770</td>
      <td>Formação Pedagógica em História</td>
      <td>NO_DEGREE</td>
      <td>historia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>SIAE</td>
      <td>True</td>
      <td>historia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7343</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSE</td>
      <td>671</td>
      <td>LPIW</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7345</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FIZ</td>
      <td>671</td>
      <td>TGPIW</td>
      <td>1363727</td>
      <td>Tecnologia em Gestão da Produção Industrial</td>
      <td>TEC</td>
      <td>gestao da producao industrial</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao da producao industrial</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7349</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FST</td>
      <td>671</td>
      <td>LPILSEGNI</td>
      <td>87237</td>
      <td>Letras - Licenciatura em Língua Portuguesa e L...</td>
      <td>LIC</td>
      <td>letras - portugues e ingles</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>letras - portugues e ingles</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7352</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPE</td>
      <td>671</td>
      <td>MATW</td>
      <td>1298841</td>
      <td>Matemática - Licenciatura</td>
      <td>LIC</td>
      <td>matematica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>matematica</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
<p>1981 rows × 19 columns</p>
</div>



###### Lista de Cursos Tecnologia que são ENADE


```python
list_cursos_tecnologo_enade = [
    "agronegocio",
    "analise e desenvolvimento de sistemas",
    "comercio exterior",
    "design grafico",
    "design de interiores",
    "design de moda",
    "estetica e cosmetica",
    "gastronomia",
    "gestao ambiental",
    "gestao comercial",
    "gestao da producao industrial",
    "gestao da qualidade",
    "gestao da tecnologia da informacao",
    "gestao de recursos humanos",
    "gestao financeira",
    "gestao hospitalar",
    "gestao publica",
    "logistica",
    "marketing",
    "processos gerenciais",
    "radiologia",
    "redes de computadores",
    "seguranca no trabalho"
]
```


```python
depara_tecnologia = {
    "gestao da ti": "gestao da tecnologia da informacao",
    "gestao de ti": "gestao da tecnologia da informacao",
    "seguranca do trabalho": "seguranca no trabalho" 
}
```


```python
filtro_curso_deparado_tec = df_cursos_ativos['curso_padronizado_old'].isin(depara_tecnologia)
```


```python
not_evaluated_tecnologia = {
    "automacao industrial",
    "banco de dados",
    "desenvolvimento em software",
    "eletrotecnica industrial",
    "embelezamento e imagem pessoal",
    "empreendedorismo",
    "estetica e imagem pessoal",
    "eventos",
    "fabricacao mecanica",
    "fotografia",
    "gestao de seguranca privada",
    "gestao de turismo",
    "gestao do agronegocio",
    "jogos digitais",
    "marketing digital",
    "mecatronica industrial",
    "pilotagem profissional de aeronaves",
    "producao audiovisual",
    "producao multimidia",
    "seguranca publica",
    "servicos juridicos, cartorarios e notariais",
    "sistemas para internet"
} 
```

##### Aplicação do DE PARA


```python
df_cursos_ativos['curso_padronizado'] = df_cursos_ativos.curso_padronizado.apply(apply_depara(depara_tecnologia))
```


```python
df_cursos_ativos[filtro_curso_deparado_tec][['curso_padronizado', 'curso_padronizado_old']].drop_duplicates()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>curso_padronizado</th>
      <th>curso_padronizado_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1126</th>
      <td>gestao da tecnologia da informacao</td>
      <td>gestao de ti</td>
    </tr>
    <tr>
      <th>3031</th>
      <td>gestao da tecnologia da informacao</td>
      <td>gestao da ti</td>
    </tr>
    <tr>
      <th>6560</th>
      <td>seguranca no trabalho</td>
      <td>seguranca do trabalho</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_cursos_ativos.loc[filtro_curso_deparado_tec, 'FLAG_NOME_CURSO_PADRONIZADO_DEPARADO'] = True
```

### Cursos com nome alterados pelo DE PARA


```python
df_cursos_ativos[filtro_curso_deparado_tec]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
      <th>curso_padronizado_old</th>
      <th>FLAG_NOME_CURSO_PADRONIZADO_DEPARADO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1126</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>770</td>
      <td>242</td>
      <td>13561</td>
      <td>1296032</td>
      <td>CST em Gestão de TI - M</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1127</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>770</td>
      <td>242</td>
      <td>13560</td>
      <td>1296032</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1240</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>643</td>
      <td>457</td>
      <td>15691</td>
      <td>1184727</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1882</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>653</td>
      <td>4878</td>
      <td>16127</td>
      <td>110038</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1884</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>636</td>
      <td>457</td>
      <td>14657</td>
      <td>1112719</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1918</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>663</td>
      <td>376</td>
      <td>16540</td>
      <td>1166894</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>671</td>
      <td>457</td>
      <td>17174</td>
      <td>63598</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2784</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>601</td>
      <td>376</td>
      <td>12708</td>
      <td>1166001</td>
      <td>CST em Gestão de TI - M</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3031</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>774</td>
      <td>15839</td>
      <td>85924</td>
      <td>1364474</td>
      <td>CST em Gestão da TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao da ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3215</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>PRESENCIAL</td>
      <td>601</td>
      <td>376</td>
      <td>12707</td>
      <td>1166001</td>
      <td>CST em Gestão de TI - N</td>
      <td>TEC</td>
      <td>gestao da tecnologia da informacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>OLIMPO</td>
      <td>True</td>
      <td>gestao de ti</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6560</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FNT</td>
      <td>671</td>
      <td>TSTRQUINI</td>
      <td>1382661</td>
      <td>Tecnologia em Segurança do Trabalho</td>
      <td>TEC</td>
      <td>seguranca no trabalho</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>seguranca do trabalho</td>
      <td>True</td>
    </tr>
    <tr>
      <th>6657</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FJK</td>
      <td>671</td>
      <td>TSTRQUINI</td>
      <td>1382661</td>
      <td>Tecnologia em Segurança do Trabalho</td>
      <td>TEC</td>
      <td>seguranca no trabalho</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>True</td>
      <td>seguranca do trabalho</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



#### Criação da flag de cursos enadistas


```python
filtro_curso_enade_ano = ((df_cursos_ativos['curso_padronizado'].isin(set(df_cursos_enade.nome_curso_edital))) &
                                          (df_cursos_ativos.area_padronizada.isin(GRAU_ENADE)))
```


```python
df_cursos_ativos[df_cursos_ativos.area_padronizada.isin(GRAU_ENADE)].loc[filtro_curso_enade_ano, 'flag_curso_nome_padronizado'] = True
```

    /home/ec2-user/anaconda3/envs/python3/lib/python3.6/site-packages/pandas/core/indexing.py:362: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
      self.obj[key] = _infer_fill_value(value)
    /home/ec2-user/anaconda3/envs/python3/lib/python3.6/site-packages/pandas/core/indexing.py:543: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
      self.obj[item] = s



```python
df_cursos_ativos[filtro_curso_enade_ano]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ano_enade</th>
      <th>marca</th>
      <th>modalidade</th>
      <th>iunicodempresa</th>
      <th>ies_mec</th>
      <th>espcod</th>
      <th>espcodmec</th>
      <th>espdesc</th>
      <th>area_padronizada</th>
      <th>curso_padronizado</th>
      <th>flag_no_ies_mec</th>
      <th>flag_no_espcodmec</th>
      <th>flag_no_espdesc</th>
      <th>flag_no_area_padronizada</th>
      <th>flag_not_implied_area_padronizada</th>
      <th>base_origem</th>
      <th>flag_not_found_curso_enade</th>
      <th>curso_padronizado_old</th>
      <th>FLAG_NOME_CURSO_PADRONIZADO_DEPARADO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>11</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>7MB</td>
      <td>1404111</td>
      <td>FISIOTERAPIA - BACHARELADO</td>
      <td>BCH</td>
      <td>fisioterapia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>fisioterapia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2ON</td>
      <td>1357953</td>
      <td>ENGENHARIA ELÉTRICA</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>22</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2OO</td>
      <td>1357883</td>
      <td>ENGENHARIA MECÂNICA</td>
      <td>BCH</td>
      <td>engenharia mecanica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia mecanica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>24</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>78</td>
      <td>1150782</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO HOSPITALAR</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>26</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2ON</td>
      <td>1357953</td>
      <td>ENGENHARIA ELÉTRICA</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>31</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2QM</td>
      <td>1374069</td>
      <td>EDUCAÇÃO FÍSICA - BACHARELADO</td>
      <td>BCH</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>38</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>7MA</td>
      <td>1420100</td>
      <td>AGRONOMIA - BACHARELADO</td>
      <td>BCH</td>
      <td>agronomia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>agronomia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>54</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>187</td>
      <td>1190160</td>
      <td>SUPERIOR DE TECNOLOGIA EM SEGURANÇA NO TRABALHO</td>
      <td>TEC</td>
      <td>seguranca no trabalho</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>seguranca no trabalho</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>60</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>61</td>
      <td>111094</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO AMBIENTAL</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>65</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>794</td>
      <td>1322923</td>
      <td>ENGENHARIA DE COMPUTAÇÃO</td>
      <td>BCH</td>
      <td>engenharia de computacao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia de computacao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>71</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>78</td>
      <td>1150782</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO HOSPITALAR</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>73</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2OK</td>
      <td>1341021</td>
      <td>ENFERMAGEM</td>
      <td>BCH</td>
      <td>enfermagem</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>enfermagem</td>
      <td>True</td>
    </tr>
    <tr>
      <th>74</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2OO</td>
      <td>1357883</td>
      <td>ENGENHARIA MECÂNICA</td>
      <td>BCH</td>
      <td>engenharia mecanica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia mecanica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>76</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2QI</td>
      <td>1370855</td>
      <td>NUTRIÇÃO</td>
      <td>BCH</td>
      <td>nutricao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>nutricao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>77</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2OM</td>
      <td>1344490</td>
      <td>ENGENHARIA CIVIL</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>80</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2QI</td>
      <td>1370855</td>
      <td>NUTRIÇÃO</td>
      <td>BCH</td>
      <td>nutricao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>nutricao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>83</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2OK</td>
      <td>1341021</td>
      <td>ENFERMAGEM</td>
      <td>BCH</td>
      <td>enfermagem</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>enfermagem</td>
      <td>True</td>
    </tr>
    <tr>
      <th>93</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2QM</td>
      <td>1374069</td>
      <td>EDUCAÇÃO FÍSICA - BACHARELADO</td>
      <td>BCH</td>
      <td>educacao fisica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>educacao fisica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>94</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>820</td>
      <td>1322867</td>
      <td>ENGENHARIA DE PRODUÇÃO</td>
      <td>BCH</td>
      <td>engenharia de producao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia de producao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>95</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2QH</td>
      <td>1373746</td>
      <td>ARQUITETURA E URBANISMO</td>
      <td>BCH</td>
      <td>arquitetura e urbanismo</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>arquitetura e urbanismo</td>
      <td>True</td>
    </tr>
    <tr>
      <th>103</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>2QH</td>
      <td>1373746</td>
      <td>ARQUITETURA E URBANISMO</td>
      <td>BCH</td>
      <td>arquitetura e urbanismo</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>arquitetura e urbanismo</td>
      <td>True</td>
    </tr>
    <tr>
      <th>107</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2OM</td>
      <td>1344490</td>
      <td>ENGENHARIA CIVIL</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>108</th>
      <td>2019</td>
      <td>DM</td>
      <td>EAD</td>
      <td>298</td>
      <td>298</td>
      <td>2QK</td>
      <td>1377566</td>
      <td>SUPERIOR DE TECNOLOGIA EM ESTÉTICA E COSMÉTICA</td>
      <td>TEC</td>
      <td>estetica e cosmetica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>estetica e cosmetica</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>115</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>671</td>
      <td>671</td>
      <td>61</td>
      <td>111094</td>
      <td>SUPERIOR DE TECNOLOGIA EM GESTÃO AMBIENTAL</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>COLABORAR</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>118</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>18</td>
      <td>2773</td>
      <td>26</td>
      <td>1200066</td>
      <td>Engenharia de Produção - N</td>
      <td>BCH</td>
      <td>engenharia de producao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>FAMA</td>
      <td>False</td>
      <td>engenharia de producao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>121</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>18</td>
      <td>2773</td>
      <td>52</td>
      <td>1284139</td>
      <td>Engenharia Ambiental - M</td>
      <td>BCH</td>
      <td>engenharia ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>FAMA</td>
      <td>False</td>
      <td>engenharia ambiental</td>
      <td>True</td>
    </tr>
    <tr>
      <th>122</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>18</td>
      <td>2773</td>
      <td>103</td>
      <td>85086</td>
      <td>Fisioterapia - N</td>
      <td>BCH</td>
      <td>fisioterapia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>FAMA</td>
      <td>False</td>
      <td>fisioterapia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>123</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>18</td>
      <td>2773</td>
      <td>115</td>
      <td>104538</td>
      <td>Odontologia - M</td>
      <td>BCH</td>
      <td>odontologia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>FAMA</td>
      <td>False</td>
      <td>odontologia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>125</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>18</td>
      <td>2773</td>
      <td>67</td>
      <td>1300267</td>
      <td>Farmácia - N</td>
      <td>BCH</td>
      <td>farmacia</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>FAMA</td>
      <td>False</td>
      <td>farmacia</td>
      <td>True</td>
    </tr>
    <tr>
      <th>126</th>
      <td>2019</td>
      <td>DM</td>
      <td>PRESENCIAL</td>
      <td>18</td>
      <td>2773</td>
      <td>57</td>
      <td>1284293</td>
      <td>Engenharia Civil - N</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>FAMA</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7176</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FSJ</td>
      <td>671</td>
      <td>ECVTERNPI</td>
      <td>1295689</td>
      <td>Engenharia Civil</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7179</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FST</td>
      <td>671</td>
      <td>EFSQUINPI</td>
      <td>111718</td>
      <td>Enfermagem</td>
      <td>BCH</td>
      <td>enfermagem</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>enfermagem</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7187</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FC4</td>
      <td>671</td>
      <td>AMBW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7190</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FRP</td>
      <td>671</td>
      <td>ECVQUINPI</td>
      <td>1295689</td>
      <td>Engenharia Civil</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7199</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FIZ</td>
      <td>671</td>
      <td>TAMBQW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7200</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FJA</td>
      <td>671</td>
      <td>AMBW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7207</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FTP</td>
      <td>671</td>
      <td>EGEQUANPI</td>
      <td>1296028</td>
      <td>Engenharia Elétrica</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7220</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FA5</td>
      <td>671</td>
      <td>AMBW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7227</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FA3</td>
      <td>671</td>
      <td>EGPTERNPI</td>
      <td>1295876</td>
      <td>Engenharia de Produção</td>
      <td>BCH</td>
      <td>engenharia de producao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia de producao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7235</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FC4</td>
      <td>671</td>
      <td>TGASW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7244</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FIS</td>
      <td>671</td>
      <td>AMBW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7251</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>EAD</td>
      <td>671</td>
      <td>EGMTERNPI</td>
      <td>1296068</td>
      <td>Engenharia Mecânica</td>
      <td>BCH</td>
      <td>engenharia mecanica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia mecanica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7257</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UAB</td>
      <td>671</td>
      <td>TESTERNPI</td>
      <td>1382662</td>
      <td>Tecnologia em Estética e Cosmética</td>
      <td>TEC</td>
      <td>estetica e cosmetica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>estetica e cosmetica</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7258</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPR</td>
      <td>671</td>
      <td>EGMQUANPI</td>
      <td>1296068</td>
      <td>Engenharia Mecânica</td>
      <td>BCH</td>
      <td>engenharia mecanica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia mecanica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7285</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FDO</td>
      <td>671</td>
      <td>TAMBQW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7286</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FPR</td>
      <td>671</td>
      <td>AMBW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7290</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAP</td>
      <td>671</td>
      <td>TAMBQW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7293</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UM2</td>
      <td>671</td>
      <td>TGHSW</td>
      <td>1107875</td>
      <td>Tecnologia em Gestão Hospitalar</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7295</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>CPL</td>
      <td>671</td>
      <td>TESTERNPI</td>
      <td>1382662</td>
      <td>Tecnologia em Estética e Cosmética</td>
      <td>TEC</td>
      <td>estetica e cosmetica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>estetica e cosmetica</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7306</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAV</td>
      <td>671</td>
      <td>TGHSW</td>
      <td>1107875</td>
      <td>Tecnologia em Gestão Hospitalar</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7310</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FGO</td>
      <td>671</td>
      <td>TGHSW</td>
      <td>1107875</td>
      <td>Tecnologia em Gestão Hospitalar</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7312</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FGO</td>
      <td>671</td>
      <td>TAMBQW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7317</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FAI</td>
      <td>671</td>
      <td>EGCVTERNI</td>
      <td>1295689</td>
      <td>Engenharia Civil</td>
      <td>BCH</td>
      <td>engenharia civil</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia civil</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7323</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FED</td>
      <td>671</td>
      <td>EGETERNPI</td>
      <td>1296028</td>
      <td>Engenharia Elétrica</td>
      <td>BCH</td>
      <td>engenharia eletrica</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>engenharia eletrica</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7328</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FBO</td>
      <td>671</td>
      <td>TAMBQW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7329</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UDP</td>
      <td>671</td>
      <td>AMBTERNI</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7332</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FED</td>
      <td>671</td>
      <td>NUTQMPI</td>
      <td>1382623</td>
      <td>Nutrição</td>
      <td>BCH</td>
      <td>nutricao</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>nutricao</td>
      <td>True</td>
    </tr>
    <tr>
      <th>7333</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FFA</td>
      <td>671</td>
      <td>TAMBQW</td>
      <td>1314992</td>
      <td>Tecnologia em Gestão Ambiental</td>
      <td>TEC</td>
      <td>gestao ambiental</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao ambiental</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7339</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>FCA</td>
      <td>671</td>
      <td>TGHSW</td>
      <td>1107875</td>
      <td>Tecnologia em Gestão Hospitalar</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7342</th>
      <td>2019</td>
      <td>AEDU</td>
      <td>EAD</td>
      <td>UM2</td>
      <td>671</td>
      <td>TGHTERNI</td>
      <td>1107875</td>
      <td>Tecnologia em Gestão Hospitalar</td>
      <td>TEC</td>
      <td>gestao hospitalar</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>SIAE</td>
      <td>False</td>
      <td>gestao hospitalar</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>2348 rows × 19 columns</p>
</div>



##### Verificação se a quantidade de observacoes da tabela tratada é igual a quantidade de observacoes da tabela original


```python
assert(df_cursos_ativos.shape[0] == df_cursos_ativos_observacoes), \
       'A quantidade de observações da base após o tratamento está diferente da quantidade de observações da base original'

print('Verificação de Base realizada com sucesso!')
```

    Verificação de Base realizada com sucesso!


### Salva resultados


```python
write_dataframe_to_csv_on_s3(df_cursos_ativos, OUTPUT_CURSOS_ATIVOS_ENADE)
```
