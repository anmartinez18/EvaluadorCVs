# Evaluador de CVs con IA Generativa

Este sistema implementa un pipeline basado en modelos llm para la evaluación de candidatos automáticamente según los requisitos de una oferta de empleo. La evaluación se realiza en dos fases:

1. Evaluación inicial automática: Se introduce el cv y la oferta de empleo, el sistema acepta archivos en formato pdf o txt, o simplmente texto libre. El sistema clasifica automáticamente que requisitos se cumplen y cuales no. Como resultado se obtiene una puntuación global ("score") y se indica si el candidato ha sido descartado o continua en el proceso.

2. Evaluación interactiva: Si el candidato no ha sido descartado y existen requisitos no mencionados en el CV, el sistema realiza una breve entrevista al candidato y actualiza el resultado final según las respuestas.

## Funcionalidades destacables
- Extracción automática de requisitos.
- Búsqueda y análisis de evidencias en el CV para contrastar el cumplimiento de los requisitos.
- Puntuación basada en el cumplimiento de requisitos. Si un requisito no se cumple se descarta al candidato automáticamente.
- Conversación interactiva con el candidato para completar el proceso.
- Sistema modular, permite cambiar el provedor del LLM de manera sencilla.


# Configurar LLM
