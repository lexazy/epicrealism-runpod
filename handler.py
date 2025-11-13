import runpod
import json
import urllib.request
import urllib.error
import time
import base64
import os

# URL de l'API ComfyUI locale
COMFYUI_URL = "http://127.0.0.1:8188"

def queue_prompt(prompt):
    """Envoie un prompt à ComfyUI"""
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    """Récupère une image depuis ComfyUI"""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{COMFYUI_URL}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    """Récupère l'historique d'un prompt"""
    with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
        return json.loads(response.read())

def wait_for_completion(prompt_id, timeout=300):
    """Attend que l'image soit générée"""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError("Image generation timeout")
        
        history = get_history(prompt_id)
        if prompt_id in history and history[prompt_id].get("status", {}).get("completed", False):
            return history[prompt_id]
        
        time.sleep(1)

def handler(job):
    """Handler principal pour RunPod"""
    job_input = job["input"]
    
    # Récupère le workflow depuis l'input
    workflow = job_input.get("workflow")
    
    if not workflow:
        return {"error": "No workflow provided"}
    
    try:
        # Envoie le workflow à ComfyUI
        prompt_response = queue_prompt(workflow)
        prompt_id = prompt_response["prompt_id"]
        
        # Attend la completion
        history = wait_for_completion(prompt_id)
        
        # Récupère les images générées
        images = []
        outputs = history.get("outputs", {})
        
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for image_info in node_output["images"]:
                    image_data = get_image(
                        image_info["filename"],
                        image_info.get("subfolder", ""),
                        image_info.get("type", "output")
                    )
                    
                    # Encode en base64
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    images.append({
                        "data": image_base64,
                        "filename": image_info["filename"],
                        "type": "base64"
                    })
        
        return {"images": images}
    
    except Exception as e:
        return {"error": str(e)}

# Démarre le serveur RunPod
runpod.serverless.start({"handler": handler})
