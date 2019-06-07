from unicodedata import normalize
import boto3

def clean_string(name):
    """Removes accents and lower case the string"""
    return normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII').lower()


def apply_depara(depara):
    """Returns a function that applies returns the depara dictionary value if the argument is key, otherwise returns key"""
    def inner(curso):
        return depara.get(curso, curso)
    return inner

def write_dataframe_to_csv_on_s3(dataframe, filename):
    """ Write a dataframe to a CSV on S3 """
    print("Writing {} records to {}".format(len(dataframe), filename))
    path = 'tmp/out.csv'
    dataframe.to_csv(path, sep=";", index=False, decimal = ',', encoding='ISO-8859-1')
    s3_resource = boto3.resource("s3")
    s3_resource.Object('krotonanalytics', filename).upload_file(path)
    print('Done')

def clean_float(value):
    """Converts float values to integer. If it's not convertable to integer, don't apply transformation"""
    try:
        return int(float(value))
    except ValueError:
        return value

def is_not_int(cell):
    return not isinstance(cell, int)

def get_flags(columns):
    return [column for column in columns if 'flag_' in column.lower()]

def get_filter(dataframe, flags):
    dataframe_filter = dataframe[flags.pop()]
    for flag in flags:
        dataframe_filter = dataframe_filter | dataframe[flag]
    return dataframe_filter

def get_rows_with_problems(dataframe):
    flags = get_flags(dataframe.columns)
    dataframe_filter = get_filter(dataframe, flags)
    return dataframe[dataframe_filter].reset_index()
    
from libs.generic_operator import clean_string

def ignore_description(espdesc):
    """Gets first element from split ' - '. This rule is Olimpo specific
        example: 'Nutrição - M' -> 'Nutrição'
    """
    return espdesc.split(' - ')[0]

def remove_prefix(curso):
    """Removes course name prefix to leave it with just the course name itself"""
    prefixos = ['superior de tecnologia em ',
                '2a licenciatura em ',
                'formacao pedagogica em ',
                'tecnologia em ', 'cst em ',
                'segunda licenciatura em ']
    for prefixo in prefixos:
        curso = curso.replace(prefixo, '')
    return curso

def clean_letras_course(row):
    """Returns a normalized letras course name.
       If the course does not contains letras in its name, no transformation is applied"""
    espdesc, curso_padronizado = row
    espdesc = clean_string(espdesc)
    output = curso_padronizado
    if 'letras' in espdesc:
        if 'portugues' in espdesc:
            if 'espanhol' in espdesc:
                output = "letras - portugues e espanhol"
            elif 'ingles' in espdesc:
                output = "letras - portugues e ingles"
            else:
                output = "letras - portugues"
        elif 'ingles' in espdesc:
            output = "letras - ingles"
        elif 'espanhol' in espdesc:
            output = "letras - espanhol"
    return output

courses = [
    (('agronomia', 'BCH'), 'ciclo I'),
    (('arquitetura e urbanismo', 'BCH'), 'ciclo I'),
    (('biomedicina', 'BCH'), 'ciclo I'),
    (('educacao fisica', 'BCH'), 'ciclo I'),
    (('enfermagem', 'BCH'), 'ciclo I'),
    (('engenharia', 'BCH'), 'ciclo I'),
    (('engenharia ambiental', 'BCH'), 'ciclo I'),
    (('engenharia civil', 'BCH'), 'ciclo I'),
    (('engenharia de alimentos', 'BCH'), 'ciclo I'),
    (('engenharia de computacao', 'BCH'), 'ciclo I'),
    (('engenharia de controle e automacao', 'BCH'), 'ciclo I'),
    (('engenharia de producao', 'BCH'), 'ciclo I'),
    (('engenharia eletrica', 'BCH'), 'ciclo I'),
    (('engenharia florestal', 'BCH'), 'ciclo I'),
    (('engenharia mecanica', 'BCH'), 'ciclo I'),
    (('engenharia quimica', 'BCH'), 'ciclo I'),
    (('farmacia', 'BCH'), 'ciclo I'),
    (('fisioterapia', 'BCH'), 'ciclo I'),
    (('fonoaudiologia', 'BCH'), 'ciclo I'),
    (('medicina', 'BCH'), 'ciclo I'),
    (('medicina veterinaria', 'BCH'), 'ciclo I'),
    (('nutricao', 'BCH'), 'ciclo I'),
    (('odontologia', 'BCH'), 'ciclo I'),
    (('zootecnia', 'BCH'), 'ciclo I'),

    (('tecnologia em agronegocio', 'TEC'), 'ciclo I'),
    (('tecnologia em estetica e cosmetica', 'TEC'), 'ciclo I'),
    (('tecnologia em gestao ambiental', 'TEC'), 'ciclo I'),
    (('tecnologia em gestao hospitalar', 'TEC'), 'ciclo I'),
    (('tecnologia em radiologia', 'TEC'), 'ciclo I'),
    (('tecnologia em seguranca no trabalho', 'TEC'), 'ciclo I'),

    (('sistema de informacao', 'BCH'), 'ciclo II'),
    (('ciencia da computacao', 'BCH'), 'ciclo II'),
    (('ciencias biologicas', 'BCH'), 'ciclo II'),
    (('ciencias sociais', 'BCH'), 'ciclo II'),
    (('filosofia', 'BCH'), 'ciclo II'),
    (('fisica', 'BCH'), 'ciclo II'),
    (('geografia', 'BCH'), 'ciclo II'),
    (('historia', 'BCH'), 'ciclo II'),
    (('letras - portugues', 'BCH'), 'ciclo II'),
    (('matematica', 'BCH'), 'ciclo II'),
    (('quimica', 'BCH'), 'ciclo II'),

    (('ciencia da computacao', 'LIC'), 'ciclo II'),
    (('ciencias biologicas', 'LIC'), 'ciclo II'),
    (('ciencias sociais', 'LIC'), 'ciclo II'),
    (('filosofia', 'LIC'), 'ciclo II'),
    (('fisica', 'LIC'), 'ciclo II'),
    (('geografia', 'LIC'), 'ciclo II'),
    (('historia', 'LIC'), 'ciclo II'),
    (('letras - portugues', 'LIC'), 'ciclo II'),
    (('matematica', 'LIC'), 'ciclo II'),
    (('quimica', 'LIC'), 'ciclo II'),
    (('artes visuais', 'LIC'), 'ciclo II'),
    (('educacao fisica', 'LIC'), 'ciclo II'),
    (('letras - portugues e espanhol', 'LIC'), 'ciclo II'),
    (('letras - portugues e ingles', 'LIC'), 'ciclo II'),
    (('letras - ingles', 'LIC'), 'ciclo II'),
    (('musica; ', 'LIC'), 'ciclo II'),
    (('pedagogia', 'LIC'), 'ciclo II'),

    (('analise e desenvolvimento de sistemas', 'TEC'), 'ciclo II'),
    (('gestao da producao industrial', 'TEC'), 'ciclo II'),
    (('redes de computadores', 'TEC'), 'ciclo II'),
    (('gestao da tecnologia da informacao', 'TEC'), 'ciclo II'),

    (('administracao', 'BCH'), 'ciclo III'),
    (('administracao publica', 'BCH'), 'ciclo III'),
    (('ciencias contabeis', 'BCH'), 'ciclo III'),
    (('ciencias economicas', 'BCH'), 'ciclo III'),
    (('comunicacao social - jornalismo', 'BCH'), 'ciclo III'),
    (('comunicacao social - publicidade e propaganda', 'BCH'), 'ciclo III'),
    (('design', 'BCH'), 'ciclo III'),
    (('direito', 'BCH'), 'ciclo III'),
    (('psicologia', 'BCH'), 'ciclo III'),
    (('relacoes internacionais', 'BCH'), 'ciclo III'),
    (('secretariado executivo', 'BCH'), 'ciclo III'),
    (('servico social', 'BCH'), 'ciclo III'),
    (('teologia', 'BCH'), 'ciclo III'),
    (('turismo', 'BCH'), 'ciclo III'),

    (('tecnologia em comercio exterior', 'TEC'), 'ciclo III'),
    (('tecnologia em design de interiores', 'TEC'), 'ciclo III'),
    (('tecnologia em design de moda', 'TEC'), 'ciclo III'),
    (('tecnologia em design grafico', 'TEC'), 'ciclo III'),
    (('tecnologia em gastronomia', 'TEC'), 'ciclo III'),
    (('tecnologia em gestao comercial', 'TEC'), 'ciclo III'),
    (('tecnologia em gestao da qualidade', 'TEC'), 'ciclo III'),
    (('tecnologia em gestao de recursos humanos', 'TEC'), 'ciclo III'),
    (('tecnologia em gestao financeira', 'TEC'), 'ciclo III'),
    (('tecnologia em gestao publica', 'TEC'), 'ciclo III'),
    (('tecnologia em logistica', 'TEC'), 'ciclo III'),
    (('tecnologia em marketing', 'TEC'), 'ciclo III'),
    (('tecnologia em processos gerenciais', 'TEC'), 'ciclo III'),
]

for index, course in enumerate(courses):
    for other_course in courses[index+1:]:
        if course[0] == other_course[0]:
            print(course, other_course)

COURSES_ENADE = dict(courses)

def get_ano_enade(row):
    """Given the name and degree gets ano Enade"""
    curso_padronizado, area_padronizada = row[0], row[1]
    return COURSES_ENADE.get((curso_padronizado, area_padronizada), 'NOT_FOUND')
    
 
 from libs.generic_operator import clean_string

def clean_area(row):
    """Returns a infered area, if the area is not TEC, LIC or BCH. If it can't infer raises an exception"""
    espdesc = clean_string(row[0])
    area = str(row[1])
    filled_area = area
    if area not in {'TEC', 'LIC', 'BCH'}:
        filled_area = infer_area(espdesc)
    return filled_area

def infer_area(espdesc):
    """Given an espdesc tries to infer which area the course is from"""
    espdesc = clean_string(espdesc)
    filled_area = None
    if 'tecnologia' in espdesc or 'cst' in espdesc:
        filled_area = 'TEC'
    elif '2a licenciatura' in espdesc or 'segunda licenciatura' in espdesc or 'formacao pedagogica' in espdesc:
        filled_area = 'NO_DEGREE'
    elif 'licenciatura' in espdesc or 'pedagogica' in espdesc:
        filled_area = 'LIC'
    elif 'engenharia' in espdesc or 'bacharelado' in espdesc:
        filled_area = 'BCH'
    elif espdesc in {'farmacia',
                     'enfermagem',
                     'publicidade e propaganda',
                     'biomedicina',
                     'teologia',
                     'arquitetura e urbanismo',
                     'nutricao'}:
        filled_area = 'BCH'
    elif espdesc == 'atualizacao de documentos provaveis formandos 2019/1 aesa':
        filled_area = 'ERRO'
    return filled_area
