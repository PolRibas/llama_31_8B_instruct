# My meta-llama/Llama-3.1-8B-Instruct

Este repositorio contiene un servicio Dockerizado que expone una API HTTP para interactuar con el modelo Llama 3.1-8B-Instruct de Meta alojado en Hugging Face.

## Requisitos Previos

1. **Acceso al modelo**: Debes tener acceso al repositorio privado "meta-llama/Meta-Llama-3.1-8B-Instruct". Ve a la página del modelo en Hugging Face y solicita acceso.

2. **Token de Hugging Face**:  
   Obtén un token personal desde tu cuenta de Hugging Face (en [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)).

3. **Docker y Python**:  
   Debes tener Docker instalado. No necesitas Python localmente ya que el build se hace en la imagen Docker.

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto con tu token:
   ```env
   HUGGINGFACE_API_KEY=hf_xxx_tu_token
    ```

2. Construye la imagen Docker y ejecuta:
    ```bash
    chmod +x run.sh
    sudo ./run.sh
    ```

## Uso

El servicio expone una API HTTP en el puerto 8002. Puedes interactuar con el modelo haciendo peticiones POST a la ruta `/generate` con el siguiente payload:

```json
{
  "text": "Escribe aquí tu texto de entrada."
}
``` 

Por ejemplo, usando `curl`:

```bash
curl -X POST http://localhost:8002/generate \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"}
  ],
  "max_new_tokens": 100
}'
``` 