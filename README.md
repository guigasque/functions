# functions


# Extract, Transform and Load

*Neste documento estão definidos os objetivos, processos e metodologias do time de engenharia de dados.*

Última atualização:  <br>
Modificado por: 

## 1. Objetivo

### 1.1 ETL:
- Garantir a confiabilidade dos dados no Data Lake;
- Garantir que todos os dados estejam limpos e normalizados;
- Otimizar o armazenamento dos dados em um único local;
- Junção de dados provenientes de diversas fontes;
- <b>Valor de negócio:</b> otimizar análises exploratórias e desenvolvimento de modelos pelos cientistas de dados.

## 2. Metodologia de trabalho


### 2.1 Entregas:
- Termos um processo estruturado de ETLs baseado na quantidade de tempo disponível na Sprint vs prioridade para cada projeto;
- Todos os projetos de dados se prepararem para solicitar e terem conhecimento de quanto as tabelas estarão disponíveis para análise;
- Toda semana termos incrementos na nuvem;
- Termos um backlog de engenharia de dados sempre populado (ex: se identificarmos algo que deva ser ajustado mas não conseguiremos realizar naquela sprint, precisamos escreve-lo na nossa ferramenta de backlogs para garantir que não esqueçamos).


### 2.2 Definições:
- Não subirmos tabelas de maneira go-horse;
- Não termos problemas com chave de tabelas;
- Os dados na Trusted devem estar 100% confiáveis;
- Temos de separar os dados nas 4 camadas distintas de acordo com suas características.

### 2.3 Mapeamento do processo:

   <img src= https://analytics-academico-prod.notebook.us-east-1.sagemaker.aws/files/98_images/Processo.png align="center">
    
#### Descrição das atividades
    
1. <b>Estudar as hipóteses:</b> As equipes de cada produto, fazem o levantamento das próximas hipóteses que irão testar.
2. <b>Levantar datasets necessários:</b> A partir das hipóteses levantadas, é necessário definir quais os datasets serão utilizados para o estudo.
3. <b>Solicitar a ingestion no Data Lake:</b> Em uma reunião semanal de 30 minutos, as equipes devem se reunir com os engenheiros de dados para solicitar a carga dos datasets.
<br>
    * <b>Planning:</b> Definir o capacity do time de engenharia e priorizar os backlogs dos projetos.
4. <b>Mapear as tabelas:</b> Após a solicitação dos times, os datasets devem ser mapeados e analisados, sempre pensar como área, ou seja, se o dataset afetar mais de um produto, temos que mantê-lo genérico para todos os produtos. *(Trello: To Do (1 week))*
5. <b>Desenvolver ETL:</b> Desenvolvimento dos ETLs para a carga dos datasets, sempre respeitar as camadas do Data Lake e suas modificações descritas no tópico *Transformação* abaixo.
6. <b>Ingestion Data Lake:</b> Ingestion dos datasets no Data Lake na camada Trusted.
<br>
    * <b>Comunicação:</b> Deve ocorrer através de e-mail, skype ou pessoalmente, acordar um deadline para esta validação, os times precisam considerar esta validação em seu capacity da sprint. 
7. <b>Validar o dataset:</b> Revisar se os campos estão de acordo com o solicitado e se os dados estão de acordo com a necessidade. Caso não esteja correto, comunicar o time de engenharia com as correções que devem ser realizadas.
8. <b>Divulgar para equipe:</b> Todas as ingestions/alterações devem ser comunicadas para todo o time, seguindo um padrão. Só após a divuldação o processo é concluído. *(Review)*

## 3. Camadas de dados

<img src="https://analytics-academico-prod.notebook.us-east-1.sagemaker.aws/files/98_images/Layers.png" align="center">

## 4. Transformação

<img src="https://analytics-academico-prod.notebook.us-east-1.sagemaker.aws/files/98_images/ETL.png" align="center">

## 5. Diagrama da Infraestrutura (To Be)

<img src="https://analytics-academico-prod.notebook.us-east-1.sagemaker.aws/files/98_images/Arquitetura.png" align="center">
