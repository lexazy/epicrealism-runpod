# Utilise une image NVIDIA CUDA comme base
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Variables d'environnement
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crée le répertoire de travail
WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Installe les dépendances Python de ComfyUI
WORKDIR /app/ComfyUI
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install --no-cache-dir -r requirements.txt

# Crée les dossiers nécessaires
RUN mkdir -p /app/ComfyUI/models/checkpoints
RUN mkdir -p /app/ComfyUI/input
RUN mkdir -p /app/ComfyUI/output

# Télécharge le modèle epiCRealismXL
RUN wget -O /app/ComfyUI/models/checkpoints/epicrealismXL_v7.safetensors \
    https://civitai.com/api/download/models/277058

# Copie le handler
COPY handler.py /app/handler.py

# Installe RunPod SDK
RUN pip3 install --no-cache-dir runpod

# Expose le port
EXPOSE 8000

# Commande de démarrage
CMD ["python3", "/app/handler.py"]
