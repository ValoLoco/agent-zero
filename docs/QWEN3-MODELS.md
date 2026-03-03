# Qwen3 Models Guide

## Why Qwen3?

Agent Zero now defaults to Qwen3 models from Alibaba for superior performance, efficiency, and licensing.

### Key Advantages

**Apache 2.0 License**
- Free for commercial use
- No restrictions on deployment
- Enterprise-friendly

**Superior Performance**
- Qwen3:4B rivals Qwen2.5-72B (18x larger)
- Enhanced reasoning capabilities
- Excellent multilingual support (100+ languages)

**MoE Efficiency**
- Qwen3-Coder:30B only activates 3.3B parameters
- Massive 30B knowledge base
- Fast inference with small active footprint

## Default Models

### General LLM: qwen3:4b

```bash
docker exec agent-zero-unified ollama pull qwen3:4b
```

**Specifications:**
- **Parameters:** 4B
- **Context:** 128K tokens
- **RAM:** ~3GB
- **Speed:** Very fast
- **Use:** General tasks, conversations, reasoning

**Performance:**
- Rivals Qwen2.5-72B on benchmarks
- Better than Gemma2:9b (smaller, faster)
- Strong instruction following
- Excellent creative writing

### Coding LLM: qwen3-coder:30b

```bash
docker exec agent-zero-unified ollama pull qwen3-coder:30b
```

**Specifications:**
- **Total Parameters:** 30B
- **Active Parameters:** 3.3B (MoE)
- **Context:** 256K tokens
- **RAM:** ~18GB
- **Speed:** Fast (only 3.3B active)
- **Use:** Code generation, debugging, refactoring

**Performance:**
- Best coding model in its class
- Agentic coding workflows
- Tool integration expertise
- Multi-language support
- Long-horizon reasoning

### Embeddings: nomic-embed-text

```bash
docker exec agent-zero-unified ollama pull nomic-embed-text
```

**Specifications:**
- **Dimensions:** 768
- **Context:** 8K tokens
- **RAM:** ~500MB
- **Use:** Memory system, RAG, document search

## Docker Container Isolation

### Why Pull Inside Container?

Docker containers have **isolated filesystems**. The Ollama instance running inside the container cannot access models stored on your host system.

**Even if you already have Qwen3 models locally:**
```bash
# This won't work (host Ollama)
ollama list
qwen3:4b  # exists on host

# But inside container it doesn't exist yet
docker exec agent-zero-unified ollama list
# empty
```

**You must pull inside the container:**
```bash
docker exec agent-zero-unified ollama pull qwen3:4b
```

### Storage Location

Models pulled inside the container are stored in:
```
docker-volumes/ollama-models/
```

This Docker volume persists across container restarts, so you only need to pull models once.

## Alternative Models

### Ultra-Lightweight: qwen3:0.6b

```bash
docker exec agent-zero-unified ollama pull qwen3:0.6b
```

- **Parameters:** 600M
- **RAM:** ~1GB
- **Use:** IoT, mobile, edge devices
- **Trade-off:** Lower quality, very fast

### Balanced: qwen3:1.7b

```bash
docker exec agent-zero-unified ollama pull qwen3:1.7b
```

- **Parameters:** 1.7B
- **RAM:** ~2GB
- **Use:** Budget laptops, fast responses
- **Trade-off:** Better than 0.6b, still compact

### Flagship Coding: qwen3-coder:480b

```bash
docker exec agent-zero-unified ollama pull qwen3-coder:480b
```

- **Total Parameters:** 480B
- **Active Parameters:** 35B (MoE)
- **RAM:** ~250GB (unified memory)
- **Use:** Maximum coding performance
- **Trade-off:** Requires high-end hardware

## Model Comparison

| Model | Total | Active | RAM | Context | Speed | Quality |
|-------|-------|--------|-----|---------|-------|--------|
| qwen3:0.6b | 600M | 600M | 1GB | 128K | ⚡⚡⚡ | ★☆☆ |
| qwen3:1.7b | 1.7B | 1.7B | 2GB | 128K | ⚡⚡ | ★★☆ |
| **qwen3:4b** | **4B** | **4B** | **3GB** | **128K** | **⚡⚡** | **★★★** |
| gemma2:9b | 9B | 9B | 6GB | 8K | ⚡ | ★★☆ |
| **qwen3-coder:30b** | **30B** | **3.3B** | **18GB** | **256K** | **⚡⚡** | **★★★** |
| qwen3-coder:480b | 480B | 35B | 250GB | 256K | ⚡ | ★★★★ |

**Legend:**
- **Bold** = Default models
- Speed: ⚡⚡⚡ Very fast → ⚡ Slower
- Quality: ★☆☆ Basic → ★★★★ Exceptional

## Configuration

### Update .env

```bash
# General LLM
OLLAMA_MODEL=qwen3:4b

# Coding LLM
OLLAMA_CODER_MODEL=qwen3-coder:30b

# Embeddings
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### Switch Models

To use a different model:

1. Pull the model inside container:
```bash
docker exec agent-zero-unified ollama pull qwen3:1.7b
```

2. Update `.env`:
```bash
OLLAMA_MODEL=qwen3:1.7b
```

3. Restart Agent Zero:
```bash
docker-compose restart
```

## Troubleshooting

### Model Not Found

**Error:**
```
Error: model 'qwen3:4b' not found
```

**Solution:**
Pull inside container:
```bash
docker exec agent-zero-unified ollama pull qwen3:4b
```

### Out of Memory

**Error:**
```
Ollama: failed to allocate memory
```

**Solutions:**

1. Use smaller model:
```bash
OLLAMA_MODEL=qwen3:1.7b
```

2. Increase Docker memory:
```yaml
# docker-compose.yml
services:
  agent-zero-unified:
    deploy:
      resources:
        limits:
          memory: 8G  # increase this
```

3. Use quantized model:
```bash
docker exec agent-zero-unified ollama pull qwen3:4b-q4_0
```

### Check Available Models

```bash
# List models inside container
docker exec agent-zero-unified ollama list

# Check disk usage
docker exec agent-zero-unified du -sh /root/.ollama/models
```

### Model Pull Slow

**Qwen3:4b download:** ~2.5GB  
**Qwen3-Coder:30b download:** ~18GB

First-time pulls can take 5-30 minutes depending on network speed.

**Speed up:**
```bash
# Pull multiple models in parallel
docker exec agent-zero-unified ollama pull qwen3:4b &
docker exec agent-zero-unified ollama pull qwen3-coder:30b &
docker exec agent-zero-unified ollama pull nomic-embed-text &
wait
```

## Performance Tips

### CPU vs GPU

**CPU Only (default):**
- Works on any machine
- Slower inference
- Good for qwen3:4b and qwen3:1.7b

**GPU Acceleration:**

If you have NVIDIA GPU:

1. Install NVIDIA Container Toolkit on host
2. Update `docker-compose.yml`:
```yaml
services:
  agent-zero-unified:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

3. Rebuild:
```bash
docker-compose down
docker-compose up --build -d
```

### Optimize Context Window

Qwen3 supports 128K context, but you can limit it:

```bash
# In agent prompts or .env
A0_SET_CONTEXT_LENGTH=32768  # Use 32K instead of 128K
```

Smaller context = faster responses, lower memory.

## Resources

- [Qwen3 Official Blog](https://qwenlm.github.io/blog/qwen3/)
- [Qwen3-Coder GitHub](https://github.com/QwenLM/Qwen3-Coder)
- [Ollama Qwen3 Page](https://ollama.com/library/qwen3)
- [Ollama Qwen3-Coder Page](https://ollama.com/library/qwen3-coder)

## License

All Qwen3 models are licensed under **Apache 2.0**:
- Free commercial use
- Modification allowed
- Distribution allowed
- No warranty

Perfect for production deployments.
