import asyncio
import base64
import os
import io
import soundfile as sf
import torch
import re
import ast
from datetime import datetime  as dt
from typing import Optional, Tuple
from infrastructure.models.model_loader import ModelLoader
from config.settings import ASSISTANT_BEHAVIOR, PROJECT_ROOT

class HearsonaService:
    """Main Hearsona service - handles audio processing and model inference"""

    def __init__(self):
        self.model_loader = ModelLoader()
        self.mistral_inst_7B_Q = None
        self.audioldm2 = None
        self.history = []
        self.parent_history = []
        self.start_over_flag = False
        self._initialized = False

    async def initialize(self):
        """Initialize models asynchronously"""
        if self._initialized:
            return
        
        loop = asyncio.get_event_loop()
        self.mistral_inst_7B_Q = await loop.run_in_executor(
            None, self.model_loader.load_llm_model
        )
        self.audioldm2 = await loop.run_in_executor(
            None, self.model_loader.load_audio_model
        )
        self._initialized = True

    def prompt_process(self, user_input: str, settings: 
                       dict) -> Tuple[Optional[str], str]:
        """User prompt processing logic"""
        attr_str = " | ".join(f"{k}: {v}" for k, v in settings.items()) if settings else ""

        full_prompt = f"{user_input} with the following attributes: {attr_str}" if attr_str else user_input

        prompt = ASSISTANT_BEHAVIOR.strip() + "\n\n"
        prompt += f"User: {full_prompt}\nAssisstant:"

        response = self.mistral_inst_7B_Q(
            prompt=prompt,
            max_tokens=520,
            stop=["User:", "Assistant:", "<|user|>", "<|assistant|>"],
        )

        llm_output = response['choices'][0]["text"]

        generation_result, assistant_reply = self._function_runner(llm_output)

        if assistant_reply != "Audio generation failed. Please Try again.":
            self.history.append({"user": full_prompt, "assistant": assistant_reply})

        return generation_result, assistant_reply
    
    
    def _generate_audio(self, prompt: str, audio_length: float = 5.2) -> str:
        """Audio generation logic"""
        try:
            generator = torch.Generator('mps').manual_seed(int(42))

            audio = self.audioldm2(
                prompt=prompt,
                negative_prompt="",
                num_inference_steps=20,
                audio_length_in_s=audio_length,
                guidance_scale=3.5,
                generator=generator
            ).audios[0]

            sample_rate = 16000

            buffer = io.BytesIO()
            sf.write(buffer, audio, samplerate=sample_rate, format='WAV')
            buffer.seek(0)
            audioBase64_str = base64.b64encode(buffer.read()).decode("utf-8")
            return audioBase64_str
        except Exception as e:
            raise RuntimeError(f"Audio generation failed: {str(e)}")


    def _function_runner(self, llm_output: str) -> Tuple[Optional[str], str]:
        """Function to call the audio generation process if applicable"""
        try:
            match = re.search(r"gen\((.*?)\)", llm_output)
            if not match:
                return None, self._strip_wrapped_quotes(llm_output.strip())
            
            args_str = match.group(1)
            args = ast.literal_eval(f"({args_str})")

            if not (isinstance(args,tuple) and len(args)==2):
                return None, "Audio generation failed. Please Try again."
            
            prompt, duration = args
            if not isinstance(prompt, str) or not prompt.strip():
                return None, "Audio generation failed. Please Try again."
            
            duration = 5.2 if duration == None else duration

            try:
                generation_result = self._generate_audio(prompt.strip(), duration)
            except Exception as e:
                return None, "Audio generation failed. Please Try again."

            natural_reply = llm_output.replace(match.group(0),"").strip()

            natural_reply = self._strip_wrapped_quotes(natural_reply)

            return generation_result, natural_reply

        except Exception as e:
            return None, "Audio generation failed. Please Try again."
        

    def start_over_context(self):
        """Restarts the context for the same user"""
        self.start_over_flag = True
        self.parent_history.extend(self.history.copy())
        self.parent_history.append({"user": "Invoked(Start Over)", "assistant": "(Start_over Mechanism Implemented)"})
        self.history = []

    def _new_session(self):
        """Clears context for new user session"""
        self.history = []
        self.parent_history = []
        self.start_over_flag = False
    
    def export_chat(self, id, path:str = PROJECT_ROOT/'server'/'app'/'convo_history'):
        """Exports the chat history for the current user session"""
        os.makedirs(str(path), exist_ok=True)
        filename = os.path.join(path, f"chat_{id}.txt")
        try: 
            with open(filename, 'w', encoding='utf-8') as file:
                if self.start_over_flag:
                    for convo in self.parent_history:
                        file.write(f"User: {convo['user']}\n")
                        file.write(f"Assistant: {convo['assistant']}\n\n") 
                    
                for convo in self.history:
                    file.write(f"User: {convo['user']}\n")
                    file.write(f"Assistant: {convo['assistant']}\n\n") 
                
        except Exception as e:
            print(f"[Export ERROR] Failed to export chat: {e}")
            return False
        
        return True

    def change_user(self):
        """Changes the user"""
        session_id = dt.now().strftime("%Y%m%d_%H%M%S")
        self.export_chat(session_id)
        self._new_session()

    def cleanup(self):
        """Cleans up resources"""
        print("[Hearsona] Cleaning up resources...")
        try:
            if hasattr(self, "mistral_inst_7B_Q"):
                del self.mistral_inst_7B_Q
                self.mistral_inst_7B_Q = None

            if hasattr(self, "audioldm2"):
                del self.audioldm2
                self.audioldm2 = None
            print("[Hearsona] Cleanup complete.")
        except Exception as e:
            print(f"[Hearsona Cleanup Error] {e}")
        pass

    def _strip_wrapped_quotes(self, text:str) -> str:
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or \
           (text.startswith("'") and text.endswith("'")):
            return text[1:-1].strip()
        return text





