from langchain_core.prompts import ChatPromptTemplate
from .models import get_model

model = get_model()

pregunta_template = """
Eres un entrevistador técnico de una empresa, tu objetivo es preguntar a los candidatos sobre los requisitos que no aparecen en su CV.

Formula una pregunta clara para confirmar experiencia o conocimientos con el siguiente requisito: 
{requisito}

Reglas importantes:
- La pregunta debe ser muy corta, simple y genérica.
- Utiliza la oferta de empleo como contexto para realizar la pregunta.
- No preguntes nada que no estea en la oferta.
- No uses cursivas, comillas, negritas ni ningún formato de Markdown, la salida debe ser solo texto plano.
- No muestres información ni explicaciones adicionales.

Oferta de empleo:
{oferta}

"""

pregunta_prompt = ChatPromptTemplate.from_template(template=pregunta_template)

pregunta_chain = pregunta_prompt | model

def question_chain(requisito, oferta):
    pregunta = pregunta_chain.invoke({"requisito": requisito, "oferta": oferta}).content
    return pregunta