from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Literal
from .models import get_model
from utils.utils import calculate_score

model = get_model()

class Requisitos(BaseModel):
    obligatorios: List[str] = Field(description="Requisitos obligatorios")
    opcionales: List[str] = Field(description="Requisitos opcionales")
    
requisitos_parser = JsonOutputParser(pydantic_object=Requisitos)

class Evidencias(BaseModel):
    requisito: str
    evidencia: str 

evidencias_parser = JsonOutputParser(pydantic_object=Evidencias)

class Evaluacion(BaseModel):
    requisito: str
    evidencia: str
    obligatorio: bool = Field(description="True si el requisito es obligatorio")
    estado: Literal["matched","unmatched","not_found"]
    
evaluacion_parser = JsonOutputParser(pydantic_object=Evaluacion)
    
# 1. Extracción de requisitos y división en obligatorios y opcionales
requisitos_template = """
Extrae y divide los requisitos de la siguiente oferta de empleo en obligatorios y opcionales:

Oferta de empleo:
{oferta}

Reglas importantes:
1. Considera únicamente lo escrito en la oferta.
2. Extrae únicamente requisitos técnicos o analíticos.
3. Trata los requisitos conectados con "y" o "," como requisitos individuales.
    Ejemplos:
        - "Experiencia en Python y Java" : ["Experiencia en Python", "Experiencia en Java"]
        - "Conocimientos en React, Vue, Angular" : ["Conocimientos en React", "Conocimientos en Vue", "Conocimientos en Angular"]

4. Trata los requisitos conectados con "o" como un único requisito.
     Ejemplos:
        - "Experiencia en Python o Java" : ['Experiencia en Python o Java']
        - "Formación en Ciencia de datos o Matemáticas" : ['Formación en Ciencia de datos o Matemáticas']
        
5. Divide los requisitos en obligatorios y opcionales según la oferta.
6. Los requisitos obligatorios deben estar indicados en la oferta de manera clara.
7. No asumas requisitos no mencionados explícitamente.
8. Una vez extraido cada requisito simplifica su descripción para añadirle un tono más natural.
    Ejemplos:
        - "Experiencia obligatoria de 2 años en HTML" : ['Experiencia de 2 años en HTML']
        - "Valorable experiencia utilizando React" : ['Experiencia en React']


Responde únicamente y obligatoriamente utilizando el siguiente formato JSON (sin texto adicional):
{format_instructions}

"""
requisitos_prompt = PromptTemplate(
    template=requisitos_template, 
    input_variables=["oferta"], 
    partial_variables={"format_instructions": requisitos_parser.get_format_instructions()}
    )

requisitos_chain = requisitos_prompt | model | requisitos_parser


# 2. Extracción de evidencias para contrastar cada requisito.
evidence_extraction_template = """
Evalúa detalladamente el CV frente a los requisitos proporcionados.

Tu objetivo es encontrar la evidencia del cumplimiento de estos requisitos.

Reglas de evaluación:
1. Debes evaluar todos los requisitos, tanto obligatorios como opcionales, uno por uno.
2. Considera solo la información presente o inferible del CV.
3. Para requisitos sobre conocimientos o experiencias básicos:
   - Busca si se mencionan en el CV, independientemente del contexto.
4. Para requisitos de años de experiencia:
   - Identifica las experiencias relevantes.
   - Deduce la duración a partir de las fechas.
   - Suma los periodos si hay varias experiencias.
5. No reformules ni modifiques la descripción de los requisitos.
   
CV:
{cv}

Requisitos:
{requisitos}   

Utiliza el siguiente ejemplo como guía para producir el resultado final:

Contexto:
- Contenido del CV:
    Desarrollador de IA Generativa - EMPRESA A (Abril 2023 - Actualidad) 
    Encargado de desarrollar sistemas de IA generativa en Python, diseñando prompts eficientes y sistemas escalables 
    Grado en Ingeniería Informática.
- Requisitos:
    - Formación mínima: Ingeniería informática o Máster en Inteligencia Artificial.
    - 5 años de experiencia en Python.
    - Experiencia en Java.
    
- Ejemplo de respuesta:
    [ 
        {{
            requisito: "Formación: Ingeniería informática o Máster en Inteligencia Artificial."
            evidencia: "Grado en ingeniería informática"
        }},
        {{
            requisito: "5 años de experiencia en Python."
            evidencia: "3 años de experiencia en Python"
        }},
        {{
            requisito: "Experiencia en Java."
            evidencia: "No se ha encontrado evidencia"
        }}
        
    ]

Responde únicamente y obligatoriamente utilizando el formato JSON (sin texto adicional):
{format_instructions}
     
"""
evidence_extraction_prompt = PromptTemplate(
    template=evidence_extraction_template, 
    input_variables=["cv","requisitos"], 
    partial_variables={"format_instructions": evidencias_parser.get_format_instructions()}
    )

evidence_extraction_chain = evidence_extraction_prompt | model | evidencias_parser

# 3. Normalización de evidencias asociadas a requisitos para una mayor comprensión. 
evidence_normalization_template = """
Simplifica las evidencias asociadas a cada requisito de manera que se entiendan de manera clara.

Requisitos y evidencias:
{evidencias}

Reglas importantes:
1. No puedes reformular ni modificar las descripciones de los requisitos.
2. No puedes añadir ni crear nuevos requisitos.
3. Está prohibido usar verbos interpretativos (demuestra, indica, menciona, etc), frases compuestas o listas.
4. La nueva evidencia debe ser muy breve y precisa.

La evidencia debe cumplir estrictamente una de estas formas:
- "X meses/años de experiencia en Y"
- "(Formación exacta)"
- "Conocimientos en X"
- "Experiencia en X"

Utiliza el siguiente ejemplo como guía para producir el resultado final:

Entrada:
[
    {{
        "requisito": "Formación mínima requerida: Ingeniería/Grado en informática",
        "evidencia": "Grado en Ingeniería Informática (2018 - 2023)"          
    }},
    {{
        "requisito": "Experiencia mínima de 6 meses con Java",
        "evidencia": "Experiencia en Java en Empresa 1 (Octubre 2022 - Junio 2023), que suma 8 meses."
    }},
    {{
        "requisito": "Experiencia en React",
        "evidencia": "No se ha encontrado evidencia"
    }}
]

Salida (Respuesta): 
[
    {{
        "requisito": "Formación mínima requerida: Ingeniería/Grado en informática",
        "evidencia": "Grado en Ingeniería Informática"          
    }},
    {{
        "requisito": "Experiencia mínima de 6 meses con Java",
        "evidencia": "Experiencia de 8 meses con Java"
    }},
    {{
        "requisito": "Experiencia en React",
        "evidencia": "No se ha encontrado evidencia"
    }}
]

Responde únicamente y obligatoriamente utilizando el formato JSON (sin texto adicional):
{format_instructions}

"""
evidence_normalization_prompt = PromptTemplate(
    template=evidence_normalization_template, 
    input_variables=["evidencias"], 
    partial_variables={"format_instructions": evidencias_parser.get_format_instructions()}
    )

evidence_normalization_chain = evidence_normalization_prompt | model | evidencias_parser

# 4. Evaluación final y clasificación de requisitos.
eval_template = """
Eres un reclutador de talento de una empresa, analiza y clasifica cada requisito frente a su evidencia asociada.

Sigue estrictamente las siguientes reglas:
1. Verifica si el requisito se cumple viendo la evidencia proporcionada.
2. Evalúa y clasifica el requisito en tres categorías diferentes.
3. No reformules ni modifiques la descripción de los requisitos ni de las evidencias en el resultado final.  


Reglas para la clasificación:
1. Si un requisito se cumple, muestra su estado como "matched"
    - Para requisitos de experiencia o conicimientos, los siguientes casos serían suficientes:
        - "Conocimientos en X"
        - "Experiencia en X"
        - "Uso de X"
2. Si un requisito existe pero no se cumple, muestra su estado como "unmatched"
3. Si no se encuentran evidencias de un requisito, muestra su estado como "not_found"

Requisitos obligatorios (Utiliza esta información únicamente como contexto):
{requisitos}

Requisito y evidencia:
{evidencia}

Responde únicamente y obligatoriamente utilizando el formato JSON (sin texto adicional):
{format_instructions}

"""
eval_prompt = PromptTemplate(
    template=eval_template, 
    input_variables=["requisitos", "evidencia"], 
    partial_variables={"format_instructions": evaluacion_parser.get_format_instructions()}
    )

eval_chain = eval_prompt | model | evaluacion_parser


def create_result(evaluacion):
    
    resultado = {
        "score" : 0,
        "discarded" : False,
        "matching_requirements" : [],
        "unmatching_requirements" : [],
        "not_found_requirements" : []
    }
    
    for eval in evaluacion:
        if eval["estado"] == "matched":
            resultado["matching_requirements"].append(eval["evidencia"])
        elif eval["estado"] == "unmatched":
            resultado["unmatching_requirements"].append(eval["requisito"])
        elif eval["estado"] == "not_found":
            resultado["not_found_requirements"].append(eval["requisito"])
            if eval["obligatorio"]:
                resultado["discarded"] = True
                
    evaluacion = calculate_score(resultado)
    return evaluacion
    
    
def cv_evaluator(oferta, cv):
    requisitos = requisitos_chain.invoke({"oferta": oferta})
    evidencias = evidence_extraction_chain.invoke({"cv": cv, "requisitos": requisitos})
    evidencias_normalizadas = evidence_normalization_chain.invoke({"evidencias": evidencias})
    
    inputs_batch = [
        {"requisitos": requisitos["obligatorios"], "evidencia": evidencia}
        for evidencia in evidencias_normalizadas
    ]
    evaluaciones = eval_chain.batch(inputs_batch)
    
    resultado = create_result(evaluaciones)
    
    return resultado
            