# Llama 3.1 8B Instruct Service

This repository contains a Dockerized FastAPI service that provides an HTTP API to interact with Meta's Llama 3.1 8B Instruct model hosted on Hugging Face. The service allows you to generate text based on user inputs through a simple API endpoint.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Obtain Hugging Face API Token](#2-obtain-hugging-face-api-token)
  - [3. Create Environment Variables](#3-create-environment-variables)
  - [4. Verify Requirements](#4-verify-requirements)
- [Docker Setup](#docker-setup)
  - [1. Build the Docker Image](#1-build-the-docker-image)
  - [2. Run the Docker Container](#2-run-the-docker-container)
- [Usage](#usage)
  - [API Endpoint](#api-endpoint)
  - [Example Request](#example-request)
  - [Example Response](#example-response)
- [Troubleshooting](#troubleshooting)
  - [1. `pad_token_id` Warning](#1-pad_token_id-warning)
  - [2. `401 Unauthorized` Error](#2-401-unauthorized-error)
  - [3. `No space left on device`](#3-no-space-left-on-device)
  - [4. Other Common Issues](#4-other-common-issues)
- [Security Considerations](#security-considerations)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Features

- **Text Generation API**: Generate text responses using the Llama 3.1 8B Instruct model.
- **Dockerized Environment**: Simplifies setup and deployment using Docker.
- **Caching Mechanism**: Utilizes a mounted volume to cache model files, reducing download times and saving disk space.
- **Environment Variable Configuration**: Securely manage sensitive information like API tokens using environment variables.

## Prerequisites

1. **Access to the Model**:
   - Ensure you have access to the [meta-llama/Meta-Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct) model on Hugging Face. This is a gated (private) repository.

2. **Hugging Face API Token**:
   - Obtain a personal access token from your Hugging Face account.
   - Navigate to [Hugging Face Tokens](https://huggingface.co/settings/tokens) to create a new token with the necessary permissions.

3. **Docker**:
   - Install Docker on your machine. You can download it from [Docker Desktop](https://www.docker.com/products/docker-desktop).

4. **Git**:
   - Ensure Git is installed to clone the repository.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your_username/my-llama-service.git
cd my-llama-service
```

### 2. Obtain Hugging Face API Token

- Log in to your [Hugging Face account](https://huggingface.co/).
- Navigate to [API Tokens](https://huggingface.co/settings/tokens).
- Click on "New token" and generate a token with at least `read` access.

### 3. Create Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```env
HUGGINGFACE_API_KEY=your_hugging_face_api_token_here
```

**Important:** Ensure that the `.env` file is added to `.gitignore` to prevent accidental exposure of your API token.

### 4. Verify Requirements

Ensure your `requirements.txt` includes the necessary dependencies:

```txt
numpy<2
fastapi
uvicorn[standard]
transformers>=4.43.0
safetensors
torch==2.0.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
python-dotenv
accelerate>=0.26.0
```

## Docker Setup

### 1. Build the Docker Image

Run the following command to build the Docker image:

```bash
sudo docker build -t my-llama-service:latest .
```

**Note:** Depending on your Docker installation, you might not need to use `sudo`. To run Docker commands without `sudo`, add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Run the Docker Container

Use the provided `run.sh` script to build and run the Docker container with the necessary volume mappings.

#### `run.sh` Script

Create a `run.sh` file with the following content:

```bash
#!/usr/bin/env bash

# Get the current directory
CURRENT_DIR=$(pwd)

# Define the cache directory relative to the current directory
CACHE_DIR="$CURRENT_DIR/llama_cache"

# Create the cache directory if it doesn't exist
mkdir -p "$CACHE_DIR"

# Build the Docker image
docker build -t my-llama-service:latest .

# Run the Docker container with the volume mounted
docker run -it --rm -p 8002:8002 \
  -v "$CACHE_DIR":/root/.cache/huggingface/hub \
  --env-file .env \
  my-llama-service:latest
```

#### Make the Script Executable

```bash
chmod +x run.sh
```

#### Execute the Script

```bash
./run.sh
```

This script performs the following actions:

1. **Builds the Docker image** named `my-llama-service:latest` using the provided `Dockerfile`.
2. **Creates a `llama_cache` directory** in the current folder to store Hugging Face cache files.
3. **Runs the Docker container**, mounting the `llama_cache` directory to `/root/.cache/huggingface/hub` inside the container.
4. **Exposes the service** on port `8002`.

## Usage

Once the service is running, you can interact with it by sending POST requests to the `/generate` endpoint.

### API Endpoint

- **URL:** `http://localhost:8002/generate`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Body:**
  - `messages`: An array of message objects containing `role` and `content`.
  - `max_new_tokens`: (Optional) Maximum number of tokens to generate. Defaults to `256`.

### Example Request

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

### Example Response

```json
{
  "generated_text": "Arrr! I be yer trusty pirate chatbot, here to assist ye on the high seas. What can I do fer ye today?"
}
```

## Troubleshooting

### 1. `pad_token_id` Warning

**Warning Message:**

```
Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.
```

**Cause:**

The model does not have a `pad_token_id` defined. The Transformers library defaults `pad_token_id` to `eos_token_id`.

**Solution:**

Explicitly define a `pad_token` in your tokenizer and resize the model's token embeddings.

#### Steps:

1. **Update `main.py` to Add a `pad_token`:**

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)

# Check and add pad_token if necessary
if tokenizer.pad_token is None:
    print("Pad token not found. Adding a pad token.")
    tokenizer.add_special_tokens({'pad_token': '<|pad|>'})
    pad_token_id = tokenizer.pad_token_id
    print(f"Added pad token: {tokenizer.pad_token}, with id: {pad_token_id}")
else:
    pad_token_id = tokenizer.pad_token_id
    print(f"Pad token already set: {tokenizer.pad_token}, with id: {pad_token_id}")

# Load the model
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", use_auth_token=hf_token)

# Resize token embeddings if pad_token was added
if tokenizer.pad_token is not None and model.config.pad_token_id is None:
    print("Resizing model's token embeddings to include the new pad token.")
    model.resize_token_embeddings(len(tokenizer))
    model.config.pad_token_id = pad_token_id
    print(f"Model's pad_token_id set to: {model.config.pad_token_id}")
```

2. **Rebuild and Run Docker Container:**

```bash
./run.sh
```

### 2. `401 Unauthorized` Error

**Error Message:**

```
401 Client Error: Unauthorized
```

**Cause:**

Incorrect or insufficient Hugging Face API token.

**Solution:**

1. **Verify API Token:**
   - Ensure that the `HUGGINGFACE_API_KEY` in your `.env` file is correct and has the necessary permissions to access the model.

2. **Ensure `.env` is Loaded Correctly:**

   Check that the `.env` file is in the root directory and correctly formatted.

3. **Rebuild Docker Container:**

   After updating the `.env` file, rebuild and run the Docker container:

   ```bash
   ./run.sh
   ```

### 3. `No space left on device`

**Error Message:**

```
OSError: [Errno 28] No space left on device
```

**Cause:**

Insufficient disk space allocated for Docker or the host machine.

**Solution:**

1. **Check Disk Space:**

   Ensure that the `llama_cache` directory on your host machine has sufficient space (at least 10-20 GB).

   ```bash
   df -h
   ```

2. **Clean Up Docker Resources:**

   Remove unused Docker images, containers, and caches to free up space.

   ```bash
   docker system prune -a
   ```

   **Warning:** This will remove all stopped containers, unused networks, and dangling images.

3. **Adjust Docker Storage Settings (If Using Docker Desktop):**

   Increase the disk allocation for Docker via Docker Desktop settings/preferences.

4. **Verify Volume Mapping:**

   Ensure that the `llama_cache` directory is correctly mapped and points to a location with sufficient space.

### 4. Other Common Issues

#### a. **Environment Variables Not Loaded**

**Cause:**

The `.env` file is missing or not correctly formatted.

**Solution:**

- Ensure the `.env` file exists in the root directory.
- Verify the format is correct (e.g., no quotes around the token).
- Ensure the `--env-file .env` flag is used when running the Docker container.

#### b. **NumPy Compatibility Warning**

**Cause:**

Incompatible NumPy version.

**Solution:**

Ensure `requirements.txt` specifies `numpy<2` to avoid compatibility issues. Rebuild the Docker image after updating `requirements.txt`:

```bash
./run.sh
```

## Security Considerations

- **Protect Your API Token:** Do not expose your `.env` file or API token in public repositories. Ensure that `.env` is listed in `.gitignore` to prevent accidental commits.
  
- **Docker Permissions:** Running Docker commands with `sudo` is common but consider configuring Docker to run without `sudo` for convenience and security.

- **Data Privacy:** Ensure that any data processed by the service complies with relevant data privacy laws and guidelines.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Hugging Face](https://huggingface.co/) for providing the Llama models and the Transformers library.
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework.
- [Docker](https://www.docker.com/) for containerization.

## Contact

For any questions or support, please open an issue in the repository or contact the maintainer at [polribasrovira@gmail.com](mailto:polribasrovira@gmail.com).
