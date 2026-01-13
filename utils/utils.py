from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from pathlib import Path
import json

def load_document(file):
    
    path = Path(file.name)
    suffix = path.suffix.lower()
    
    document = ""
    
    if suffix == ".pdf":
        loader = PyMuPDFLoader(str(path))
        document = loader.load()
    elif suffix == ".txt":
        loader = TextLoader(str(path), encoding="utf-8")
        document = loader.load()
    else:
        raise ValueError(f"Formato no soportado: {suffix}")
    
    if document != "":
        return document[0].page_content;
    else:
        return "Error cargando documento"
    
    
def calculate_score(data: dict) -> dict:
    matching = data["matching_requirements"]
    unmatching = data["unmatching_requirements"]
    not_found = data["not_found_requirements"]
    
    total = len(matching) + len(unmatching) + len(not_found)
    
    if data["discarded"] or total == 0:
        score = 0
    else:
        score = round((len(matching) / total) * 100)
        
    data["score"] = score
    return data
        
    
def update_json(state):
    data = state["resultado"]
    requisitos = state["requisitos"]
    cumple_requisitos = state["cumple_requisito"]
    
    tuple_requisitos = tuple(zip(requisitos, cumple_requisitos))
   
    for requisito, result in tuple_requisitos:
        if result: 
            data["matching_requirements"].append(requisito)
            if requisito in data["not_found_requirements"]:
                data["not_found_requirements"].remove(requisito)

    state["resultado"] = data
    return data


            
    
        