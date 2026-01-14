
import gradio as gr
from utils.utils import load_document, calculate_score, update_json
from src.cv_evaluator import cv_evaluator
from src.interview_chain import interview_chain
from src.question_chain import question_chain
from src.greeting_chain import greeting_chain
from pathlib import Path
import json


css_path = Path("./styles/styles.css")

with open(css_path, "r", encoding="utf-8") as f:
    custom_css = f.read()
    

def get_initial_state():
    return {
        "oferta": "",
        "resultado": None,
        "requisitos": [],
        "cumple_requisito": [],
        "current_index": 0
    }


def evaluate_cv(cv_file, oferta_file, cv_text, oferta_text):
    
    state = get_initial_state()
    
    if cv_file:
        cv_content = load_document(cv_file)
    else:
        cv_content = cv_text 
        
    if oferta_file:
        oferta_content = load_document(oferta_file)
    else:
        oferta_content = oferta_text 

    resultado = cv_evaluator(oferta_content, cv_content)

    state["oferta"] = oferta_content
    state["resultado"] = resultado
    
    if resultado["discarded"] :
        return [
            json.dumps(resultado, indent=4, ensure_ascii=False),
            state,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False)
        ]
    elif resultado["not_found_requirements"]:
        return[
            json.dumps(resultado, indent=4, ensure_ascii=False),
            state,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False)
        ]
    else:
        return [
            json.dumps(resultado, indent=4, ensure_ascii=False),
            state,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True)
        ]


def start_interview(state):
    resultado = state["resultado"]
    oferta = state["oferta"]
    state["requisitos"] = resultado['not_found_requirements']
    
    saludo = greeting_chain(oferta)
    
    return saludo, state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)


def interview(pregunta, respuesta, state):
    
    index = state["current_index"]
    if index > 0:
      state = save_result(pregunta, respuesta, state)
    
    if index < len(state["requisitos"]):
        requisito = state["requisitos"][index]
        oferta = state["oferta"]
        pregunta = question_chain(requisito, oferta)
        state["current_index"] += 1
        return pregunta, state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="")
    else:
        return "", state, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(value="")
    
    
def save_result(pregunta, respuesta, state):
    resultado = interview_chain(pregunta, respuesta)
    state["cumple_requisito"].append(resultado.value)
    return state


def update_result(state):
    resultado_json = update_json(state)
    json_actualizado = calculate_score(resultado_json)
    state["resultado"] = json_actualizado
    
    return json.dumps(json_actualizado, indent=4, ensure_ascii=False), gr.update(visible=True), gr.update(visible=False)


def reset_app():
    return [
        get_initial_state(),
        None, None,              
        "", "",                 
        "", "",                  
        gr.update(visible=True),
        gr.update(visible=True), 
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False)
    ]



def toggle_button(cv_file, cv_text, oferta_file, oferta_text):
    if (cv_file or cv_text) and (oferta_file or oferta_text):
        return gr.update(interactive=True)
    else:
        return gr.update(interactive=False)


with gr.Blocks() as demo:
    gr.Markdown('<h1 style="text-align:center"> 🔍 Evaluador de CVs con IA 🧠✅</h1>', elem_classes="center-text")
    state = gr.State(value=get_initial_state())
    
    with gr.Group(visible=True) as evaluation_view:
        with gr.Row():
            
            cv_file = gr.File(
                label="CV (pdf o txt)",
                file_types=[".pdf", ".txt"],
                scale=1
            )
            
            cv_text = gr.Textbox(
                label="Contenido del CV",
                scale=2,
                lines=8,
                elem_classes="scroll-text"
            )
            
        with gr.Row():
            
            oferta_file = gr.File(
                label="Oferta (pdf o txt)",
                file_types=[".pdf", ".txt"],
                scale=1
            )
                
            oferta_text = gr.Textbox(
                label="Requisitos de la oferta",
                lines=8,
                scale=2,
                elem_classes="scroll-text"
            )
            
        
    cv_evaluation_btn = gr.Button("Iniciar evaluación",visible=True, interactive=False, elem_classes="button-primary")
            
    cv_file.upload(toggle_button, [cv_file, cv_text, oferta_file, oferta_text], cv_evaluation_btn)
    cv_text.change(toggle_button, [cv_file, cv_text, oferta_file, oferta_text], cv_evaluation_btn)
    oferta_file.upload(toggle_button, [cv_file, cv_text, oferta_file, oferta_text], cv_evaluation_btn)
    oferta_text.change(toggle_button, [cv_file, cv_text, oferta_file, oferta_text], cv_evaluation_btn)
        
       
    with gr.Column(visible=False, elem_classes="width-70") as results_view:     
        resultado = gr.Textbox(
            label="Resultado",
            type="text",
            lines=8
        )
                
    
    avanzar_btn = gr.Button("Avanzar", visible=False, elem_classes="button-primary")
    
    finalizar_eval_btn = gr.Button("Nueva evaluación", visible=False, elem_classes="button-primary")
            
    with gr.Group(visible=False) as discarded_view:
        gr.Markdown(
            "<h4 style='text-align:center; margin-top:20px; margin-bottom:20px; padding:10px;'>El candidato ha sido descartado por no cumplir con los requisitos obligatorios de la oferta</h4>",
               elem_classes="center-text"
            )
        discarded_btn = gr.Button("Nueva evaluación", elem_classes="button-primary")
        
    
    with gr.Column(visible=False,  elem_classes="interview-column") as greeting_view:
        
        greeting = gr.Markdown(elem_classes="interview-question")
        
        start_interview_btn = gr.Button("Avanzar", elem_classes="button-primary")
    
    
    with gr.Column(visible=False,  elem_classes="interview-column") as interview_view:
        
        question = gr.Markdown(elem_classes="interview-question")
        
        user_input = gr.Textbox(
            type="text",
            label="Respuesta",
            lines=2,
            elem_classes="interview-answer"
        )
        
        submit_answer = gr.Button("Enviar", elem_classes="button-primary")
        
    with gr.Row(visible=False,  elem_classes="width-70") as finish_view:
        
        finish_btn = gr.Button("Finalizar evaluación", elem_classes="button-primary")
        
    with gr.Column(visible=False, elem_classes="width-70") as results_interview_view:
        
        resultados_actualizados = gr.Textbox(
            label="Resultado final",
            type="text",
            lines=8
        )
        
        new_eval_btn = gr.Button("Nueva evaluación", elem_classes="button-primary")
            
    cv_evaluation_btn.click(
        fn=evaluate_cv, 
        inputs=[cv_file, oferta_file, cv_text, oferta_text], 
        outputs=[resultado,
                 state,
                 evaluation_view,
                 cv_evaluation_btn,
                 results_view,
                 avanzar_btn,
                 discarded_view,
                 finalizar_eval_btn
        ])
    
    avanzar_btn.click(
        fn=start_interview,
        inputs=[state],
        outputs=[greeting, state, greeting_view, results_view, avanzar_btn]
    )
    
    start_interview_btn.click(
        fn=interview,
        inputs=[gr.State(value=""), gr.State(value=""), state],
        outputs=[question, state, interview_view, finish_view, greeting_view, user_input]
    )
        
    submit_answer.click(
        fn=interview,
        inputs=[question, user_input, state],
        outputs=[question, state, interview_view, finish_view, greeting_view, user_input]
    )
    
    finish_btn.click(
        fn=update_result,
        inputs=[state],
        outputs=[resultados_actualizados, results_interview_view, finish_view]
    )
    
    finalizar_eval_btn.click(
        fn=reset_app,
        outputs=[
            state,
            cv_file, oferta_file,
            cv_text, oferta_text,
            resultado, resultados_actualizados,
            evaluation_view,
            cv_evaluation_btn,
            interview_view,
            finish_view,
            results_view, 
            results_interview_view,
            discarded_view,
            greeting_view,
            avanzar_btn,
            finalizar_eval_btn
        ]
    )
    
    discarded_btn.click(
        fn=reset_app,
        outputs=[
            state,
            cv_file, oferta_file,
            cv_text, oferta_text,
            resultado, resultados_actualizados,
            evaluation_view,
            cv_evaluation_btn,
            interview_view,
            finish_view,
            results_view, 
            results_interview_view,
            discarded_view,
            greeting_view,
            avanzar_btn,
            finalizar_eval_btn
        ]
    )
    
    new_eval_btn.click(
        fn=reset_app,
        outputs=[
            state,
            cv_file, oferta_file,
            cv_text, oferta_text,
            resultado, resultados_actualizados,
            evaluation_view,
            cv_evaluation_btn,
            interview_view,
            finish_view,
            results_view, 
            results_interview_view,
            discarded_view,
            greeting_view,
            avanzar_btn,
            finalizar_eval_btn
        ]
    )
    
    demo.load(
        fn=reset_app,
        outputs=[
            state,
            cv_file, oferta_file,
            cv_text, oferta_text,
            resultado, resultados_actualizados,
            evaluation_view,
            cv_evaluation_btn,
            interview_view,
            finish_view,
            results_view, 
            results_interview_view,
            discarded_view,
            greeting_view,
            avanzar_btn,
            finalizar_eval_btn
        ]
    )
  
demo.launch(theme=gr.themes.Base(), css=custom_css, server_port=7862, share=False)
