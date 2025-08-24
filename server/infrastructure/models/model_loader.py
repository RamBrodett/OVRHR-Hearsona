import torch
import os
from pathlib import Path
from llama_cpp import Llama
from diffusers import AudioLDM2Pipeline, DPMSolverMultistepScheduler
from server.config import PROJECT_ROOT

class ModelLoader:
    """Simple utility class for loading pre-trained models."""
    def __init__(self, models_base_path:str = PROJECT_ROOT/'server'/'models'):
        self.models_path = Path(models_base_path)

    def load_llm_model(self) -> Llama:
        """Load Mistral model."""
        model_path = self.models_path/'llm'/'Mistral-7B-Instruct-v0.3.Q4_K_M.gguf'

        max_threads = os.cpu_count()
        n_threads = max(2, max_threads - 2)

        return Llama(
            model_path=str(model_path),
            n_ctx=16384,
            n_gpu_layers=32,
            n_threads=n_threads,
            verbose=False,
            use_mps=True
        )
    
    def load_audio_model(self) -> AudioLDM2Pipeline:
        """Load AudioLDM2 model."""
        model_path = self.models_path/'audio'/'audioldm2'

        pipe = AudioLDM2Pipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
        )
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.to("mps")
        pipe.unet.eval()
        
        return pipe