FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y git curl build-essential && rm -rf /var/lib/apt/lists/*

# Instalar rust (por si tokenizers necesita compilar)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu torch==2.0.1 fastapi uvicorn[standard] transformers>=4.43.0 safetensors
RUN pip install -r requirements.txt
RUN pip install 'accelerate>=0.26.0'

COPY main.py .
COPY .env .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
