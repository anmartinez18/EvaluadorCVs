
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from .models import get_model

model = get_model()


class AnalisisRespuesta(BaseModel):
    value: bool = Field(description="True o false según la respuesta del modelo")
    

chat_template = """
Eres un entrevistador técnico de una empresa, debes analizar las respuestas obtenidas de los usuarios sobre preguntas acerca de los requisitos que no aparecen en su CV.

Responde únicamente con true o false (sin información adicional):
- true: si se cumple el requisito o se mencionan conocimientos o experiencia con esa tecnología o herramienta.
- false: si no cumple el requisito o se niega el uso o conocimiento de ese requisito.

La conversación es la siguiente:
Pregunta: {pregunta}
Respuesta: {respuesta}

Reglas importantes:
- Ten en cuenta que la respuesta puede ser breve o poco desarrollada.
- No trates una respuesta breve inicialmente como negativa.

"""
chat_prompt = ChatPromptTemplate.from_template(template=chat_template)
structured_output = model.with_structured_output(AnalisisRespuesta)

chat_chain = chat_prompt | structured_output

def interview_chain(pregunta, respuesta):
    resultado = chat_chain.invoke({"pregunta": pregunta, "respuesta": respuesta})
    return resultado
