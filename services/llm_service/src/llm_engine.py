"""
LLM Engine - Text generation using llama.cpp

Handles:
- Loading models with llama.cpp
- Text generation with configurable parameters
- Streaming and batch generation
- Performance monitoring
"""

import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

# Import llama-cpp-python (will be installed via requirements.txt)
try:
    from llama_cpp import Llama
except ImportError:
    logger.error("llama-cpp-python not installed. Run: pip install llama-cpp-python")
    Llama = None


class LLMEngine:
    """LLM inference engine using llama.cpp"""

    def __init__(
        self,
        model_path: str,
        model_settings_path: str,
        n_ctx: int = 2048,
        n_threads: Optional[int] = None,
        n_gpu_layers: int = 0,
    ):
        """
        Initialize LLM engine

        Args:
            model_path: Path to the GGUF model file
            model_settings_path: Path to model_settings.yaml
            n_ctx: Context window size (tokens)
            n_threads: Number of threads (None = auto-detect)
            n_gpu_layers: Number of layers to offload to GPU (0 = CPU only)
        """
        if Llama is None:
            raise ImportError("llama-cpp-python is required but not installed")

        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        # Load model settings
        self.settings = self._load_settings(model_settings_path)
        self.generation_params = self.settings["generation"]
        self.model_params = self.settings["model"]

        # Override with provided parameters
        if n_ctx:
            self.model_params["n_ctx"] = n_ctx
        if n_threads is not None:
            self.model_params["n_threads"] = n_threads
        if n_gpu_layers:
            self.model_params["n_gpu_layers"] = n_gpu_layers

        logger.info(f"Loading model: {self.model_path}")
        logger.info(f"Context window: {self.model_params['n_ctx']} tokens")
        logger.info(f"GPU layers: {self.model_params['n_gpu_layers']}")

        # Load the model
        self.llm = self._load_model()

        logger.info("LLM engine initialized successfully")

    def _load_settings(self, settings_path: str) -> Dict[str, Any]:
        """Load model settings from YAML"""
        with open(settings_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_model(self) -> Llama:
        """Load the LLM model using llama.cpp"""
        try:
            llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.model_params["n_ctx"],
                n_batch=self.model_params["n_batch"],
                n_threads=self.model_params["n_threads"] or None,
                n_gpu_layers=self.model_params["n_gpu_layers"],
                use_mmap=self.model_params["use_mmap"],
                use_mlock=self.model_params["use_mlock"],
                seed=self.model_params.get("seed"),
                verbose=self.model_params.get("verbose", False),
            )
            logger.info("Model loaded successfully")
            return llm

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate text from a prompt

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (overrides config)
            temperature: Sampling temperature (overrides config)
            top_p: Nucleus sampling parameter (overrides config)
            top_k: Top-k sampling parameter (overrides config)
            repetition_penalty: Repetition penalty (overrides config)
            stop_sequences: Stop generation when these are encountered
            stream: Enable streaming (not fully implemented)

        Returns:
            Generated text
        """
        # Use provided parameters or fall back to defaults
        gen_params = {
            "max_tokens": max_tokens or self.generation_params["max_tokens"],
            "temperature": temperature if temperature is not None else self.generation_params["temperature"],
            "top_p": top_p if top_p is not None else self.generation_params["top_p"],
            "top_k": top_k or self.generation_params["top_k"],
            "repeat_penalty": repetition_penalty or self.generation_params["repetition_penalty"],
            "stop": stop_sequences or self.generation_params.get("stop_sequences", []),
        }

        logger.debug(f"Generating with params: {gen_params}")

        start_time = time.time()

        try:
            # Generate response
            response = self.llm(
                prompt,
                max_tokens=gen_params["max_tokens"],
                temperature=gen_params["temperature"],
                top_p=gen_params["top_p"],
                top_k=gen_params["top_k"],
                repeat_penalty=gen_params["repeat_penalty"],
                stop=gen_params["stop"],
                echo=False,  # Don't include prompt in output
            )

            generation_time = time.time() - start_time

            # Extract generated text
            generated_text = response["choices"][0]["text"].strip()

            # Log performance metrics
            tokens_generated = response["usage"]["completion_tokens"]
            tokens_per_sec = tokens_generated / generation_time if generation_time > 0 else 0

            logger.info(
                f"Generated {tokens_generated} tokens in {generation_time:.2f}s "
                f"({tokens_per_sec:.1f} tok/s)"
            )

            return generated_text

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def generate_with_character(
        self,
        prompt: str,
        character_name: str,
        scenario: str = "chat",
    ) -> str:
        """
        Generate text with character-specific parameters

        Args:
            prompt: Input prompt
            character_name: Name of the character
            scenario: Scenario type (chat, confirmation, etc.)

        Returns:
            Generated text
        """
        # Get character-specific overrides if available
        char_overrides = self.settings.get("character_overrides", {}).get(
            character_name.lower(), {}
        )

        # Get scenario-specific settings if available
        scenario_settings = self.settings.get("scenario_settings", {}).get(
            scenario, {}
        )

        # Merge settings (scenario > character > default)
        gen_params = {**self.generation_params}
        gen_params.update(char_overrides)
        gen_params.update(scenario_settings)

        logger.debug(f"Generating for character '{character_name}', scenario '{scenario}'")

        return self.generate(
            prompt=prompt,
            max_tokens=gen_params.get("max_tokens"),
            temperature=gen_params.get("temperature"),
            top_p=gen_params.get("top_p"),
            top_k=gen_params.get("top_k"),
            repetition_penalty=gen_params.get("repetition_penalty"),
        )

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        try:
            tokens = self.llm.tokenize(text.encode("utf-8"))
            return len(tokens)
        except Exception as e:
            logger.error(f"Failed to count tokens: {e}")
            # Rough approximation: ~4 characters per token
            return len(text) // 4

    def get_max_context_length(self) -> int:
        """
        Get the maximum context length

        Returns:
            Maximum context length in tokens
        """
        return self.model_params["n_ctx"]

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model

        Returns:
            Model information dictionary
        """
        return {
            "model_path": str(self.model_path),
            "n_ctx": self.model_params["n_ctx"],
            "n_threads": self.model_params["n_threads"],
            "n_gpu_layers": self.model_params["n_gpu_layers"],
            "generation_params": self.generation_params,
        }

    def benchmark(self, prompt: str = "Hello, how are you?", iterations: int = 3) -> Dict[str, float]:
        """
        Run a simple benchmark

        Args:
            prompt: Test prompt
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        logger.info(f"Running benchmark with {iterations} iterations...")

        times = []
        token_counts = []

        for i in range(iterations):
            start = time.time()
            response = self.generate(prompt, max_tokens=50)
            elapsed = time.time() - start

            times.append(elapsed)
            token_counts.append(self.count_tokens(response))

            logger.info(f"Iteration {i+1}: {elapsed:.2f}s, {token_counts[-1]} tokens")

        avg_time = sum(times) / len(times)
        avg_tokens = sum(token_counts) / len(token_counts)
        avg_tok_per_sec = avg_tokens / avg_time if avg_time > 0 else 0

        results = {
            "avg_time_sec": avg_time,
            "avg_tokens": avg_tokens,
            "avg_tokens_per_sec": avg_tok_per_sec,
            "min_time": min(times),
            "max_time": max(times),
        }

        logger.info(f"Benchmark results: {results}")
        return results


if __name__ == "__main__":
    # Test the LLM engine
    logging.basicConfig(level=logging.INFO)

    model_path = "/home/user/jarvis_manager/shared/models/llm/Phi-3-mini-4k-instruct-q4.gguf"
    settings_path = "/home/user/jarvis_manager/services/llm_service/config/model_settings.yaml"

    if Path(model_path).exists():
        engine = LLMEngine(model_path, settings_path)

        # Test generation
        test_prompt = "You are a helpful assistant. User: Hello! Assistant:"
        response = engine.generate(test_prompt, max_tokens=50)
        print(f"\nTest response: {response}")

        # Run benchmark
        engine.benchmark()
    else:
        print(f"Model not found: {model_path}")
        print("Download the model first using ModelManager")
