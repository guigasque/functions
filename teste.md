
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
