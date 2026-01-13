# Evaluador de CVs con IA Generativa

Este sistema implementa un pipeline basado en modelos llm para la evaluación de candidatos automáticamente según los requisitos de una oferta de empleo. La evaluación se realiza en dos fases:

1. **Evaluación inicial automática**: Se introduce el cv y la oferta de empleo, se aceptan archivos en formato pdf o txt, o simplemente texto libre. Si se carga un archivo y se incluye texto libre a la vez, el fichero adjuntado tendrá prioridad. A continuación, el sistema clasifica automáticamente que requisitos se cumplen y cuales no. Como resultado se obtiene una puntuación global ("score") y se indica si el candidato ha sido descartado o continua en el proceso gracias al valor de ("discarded").

2. **Evaluación interactiva**: Si el candidato no ha sido descartado y existen requisitos no mencionados en el CV ("not_found_requirements"), que no sean obligatorios, el sistema realizará una breve entrevista al candidato y actualizará el resultado final en base a las respuestas proporcionadas. En caso contrario se finalizará la evaluación.

## Funcionalidades destacables
- Extracción automática de requisitos.
- Búsqueda y análisis de evidencias en el CV para contrastar el cumplimiento de los requisitos.
- Puntuación basada en el cumplimiento de requisitos. Si un requisito no se cumple se descarta al candidato automáticamente.
- Conversación interactiva con el candidato para completar el proceso.
- Sistema modular, permite cambiar el provedor del LLM de manera sencilla.

## Configurar LLM

Para el desarrollo del sistema se ha utilizado un LLM de Mistral, concretamente el modelo llamado "mistral-large-latest".

En el carpeta 'src' existen los dos archivos necesarios para la configuración del llm: 

- **"models.py"**: Aquí se añade o se modifica el modelo LLM que se utilizará.

- **".env"**: En este fichero se debe incluir la api_key necesaria para instanciar el modelo.


 ## Ejemplo de uso

 ```shell

# Situarse la siguiente ruta
cd EvaluadorCVs

# 1. Instalar poetry (sino está ya instalado)
pip install poetry

# 2. Configurar entorno de ejecución
poetry lock
poetry install

# 3. Activar entorno
.\.venv\Scripts\activate

# 4. Lanzar la aplicación web con Gradio
python app.py

```
## Aclaraciones
- La applicación web servirá por defecto en la URL local: http://127.0.0.1:7860
- El puerto se puede modificar desde el fichero app.py añadiendo la opción 'server_port=XXXX' en la última linea de código.
- Para crear un enlace totalmente público añadir la opción 'shared=True'.
