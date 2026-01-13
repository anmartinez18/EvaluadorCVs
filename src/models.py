from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()


MODELS = {
    "mistral": ChatMistralAI(model_name="mistral-large-latest", temperature=0)
    # Añadir modelo deseado
}

# Modificar nombre del modelo a elegir 
model = "mistral"

def get_model():
    return MODELS.get(model, MODELS[model])
