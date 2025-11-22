# LLM Models Directory

This directory stores the local LLM models used by the Jarvis LLM service.

## Current Model

**Phi-3-mini-4k-instruct (Q4_K_M quantization)**
- Size: ~2.3 GB
- Parameters: 3.8B
- Context: 4096 tokens
- Format: GGUF (for llama.cpp)
- Quantization: Q4_K_M (balanced quality/size)

## Model Selection Rationale

### Why Phi-3-mini?

1. **Size**: At ~2.3GB quantized, it's well within our 5GB preference
2. **Performance**: Excellent instruction following capabilities
3. **Speed**: Fast inference on CPU (~10-20 tokens/sec on average hardware)
4. **Quality**: High-quality responses with good coherence
5. **Multi-language**: Strong support for both English and Russian
6. **Context**: 4K context window is sufficient for conversation history
7. **Quantization**: Q4_K_M offers best quality/size ratio

### Model Comparison

| Model | Size | Speed | Quality | Memory |
|-------|------|-------|---------|--------|
| Phi-3-mini-q4 | 2.3GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 3-4GB |
| Gemma-2-2b-q4 | 1.5GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2-3GB |
| TinyLlama-q4 | 700MB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 1-2GB |

**Selected: Phi-3-mini** for best balance of quality and performance.

## Downloading the Model

### Automatic Download (Recommended)

The model will be automatically downloaded on first run if `auto_download: true` is set in the configuration.

```bash
# Start the LLM service - it will download the model automatically
cd /home/user/jarvis_manager/services/llm_service/src
python main.py
```

### Manual Download

#### Option 1: Using the Model Manager

```python
from model_manager import ModelManager

config_path = "/home/user/jarvis_manager/services/llm_service/config/llm_config.yaml"
manager = ModelManager(config_path)

# Download the model
model_path = manager.download_model()
print(f"Model downloaded to: {model_path}")

# Verify the model
if manager.verify_model():
    print("Model verified successfully!")
```

#### Option 2: Using the Download Script

```bash
cd /home/user/jarvis_manager/shared/models/llm
python download_model.py
```

#### Option 3: Manual Download from HuggingFace

```bash
# Install huggingface-hub if not already installed
pip install huggingface-hub

# Download using huggingface-cli
huggingface-cli download \
  microsoft/Phi-3-mini-4k-instruct-gguf \
  Phi-3-mini-4k-instruct-q4.gguf \
  --local-dir /home/user/jarvis_manager/shared/models/llm
```

## Model File Structure

```
shared/models/llm/
├── README.md                              # This file
├── download_model.py                      # Download script
├── Phi-3-mini-4k-instruct-q4.gguf        # The model file (downloaded)
└── .gitignore                            # Ignore model files in git
```

## Model Information

### Phi-3-mini-4k-instruct

- **Developer**: Microsoft
- **Repository**: microsoft/Phi-3-mini-4k-instruct-gguf
- **License**: MIT
- **Architecture**: Transformer
- **Training Data**: High-quality web data, books, code
- **Special Features**:
  - Excellent instruction following
  - Good reasoning capabilities
  - Strong multilingual support
  - Efficient tokenization

### Quantization: Q4_K_M

- **Method**: 4-bit K-quant (mixed precision)
- **Size Reduction**: ~75% smaller than FP16
- **Quality**: Minimal quality loss (<3% perplexity increase)
- **Speed**: 2-3x faster than FP16
- **Recommended**: Best balance for production use

## Performance Benchmarks

### Expected Performance (on average hardware)

- **CPU**: Intel i5/AMD Ryzen 5 or better
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space

**Metrics**:
- Response time: 1-3 seconds for typical responses (50-100 tokens)
- Tokens per second: 10-25 tok/s (CPU)
- Memory usage: 3-4GB during inference
- Startup time: 2-5 seconds to load model

### Optimization Tips

1. **Use CPU with AVX2**: 2x faster inference
2. **Increase threads**: Set `n_threads` to number of CPU cores
3. **Use mmap**: Faster model loading (enabled by default)
4. **Reduce context**: Use smaller context window if not needed
5. **Adjust batch size**: Tune `n_batch` for your hardware

## Alternative Models

If Phi-3-mini doesn't meet your needs:

### Smaller/Faster Alternative: Gemma-2-2b

```yaml
# In llm_config.yaml, change to:
model:
  name: "gemma-2-2b-instruct"
  variant: "q4_k_m"
  repo_id: "google/gemma-2-2b-it-gguf"
  filename: "gemma-2-2b-it-q4_k_m.gguf"
```

### Larger/Better Quality Alternative: Llama-3.2-3B

```yaml
# In llm_config.yaml, change to:
model:
  name: "llama-3.2-3b-instruct"
  variant: "q4_k_m"
  repo_id: "meta-llama/Llama-3.2-3B-Instruct-gguf"
  filename: "llama-3.2-3b-instruct-q4_k_m.gguf"
```

## Troubleshooting

### Model Download Fails

```bash
# Check internet connection
ping huggingface.co

# Try manual download with verbose output
huggingface-cli download \
  microsoft/Phi-3-mini-4k-instruct-gguf \
  Phi-3-mini-4k-instruct-q4.gguf \
  --local-dir /home/user/jarvis_manager/shared/models/llm \
  --resume-download
```

### Model Loading Fails

1. Check file exists: `ls -lh Phi-3-mini-4k-instruct-q4.gguf`
2. Verify file size: Should be ~2.3GB
3. Check file integrity: Not corrupted or partially downloaded
4. Check RAM: Need at least 4GB free
5. Check llama-cpp-python: `pip install --upgrade llama-cpp-python`

### Slow Inference

1. Check CPU usage: Should be near 100% during generation
2. Reduce `n_ctx` to 1024 for faster inference
3. Increase `n_threads` to match CPU cores
4. Use a smaller model if needed

## Storage Requirements

- Model file: ~2.3 GB
- Runtime memory: ~3-4 GB
- Total recommended: 10 GB free space (for safety)

## Security Considerations

- Models are downloaded from official HuggingFace repositories
- Files are verified after download
- Models run entirely offline after download
- No data is sent to external servers during inference

## License

The Phi-3-mini model is released under the MIT License.
See: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf

## Support

For issues or questions:
1. Check this README
2. Review logs in `/home/user/jarvis_manager/logs/llm_service.log`
3. See model documentation: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
4. Contact Agent 2 (LLM Service maintainer)

---

Last updated: 2025-11-22
Agent 2 - LLM Service
