import os
import logging
from typing import Dict, Any
from pathlib import Path
import tempfile
import wave


logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, output_dir: str = "./data/tts_outputs"):
        """
        Initialize TTS service with Piper TTS Python API
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if Piper is available
        self._check_piper_availability()
        
    def _check_piper_availability(self):
        """Check if Piper Python API is available"""
        try:
            import piper
            logger.info("Piper Python API found")
        except ImportError:
            logger.warning("Piper Python API not found. Please install: pip install piper-tts")
    
    def _get_model_paths(self) -> Dict[str, str]:
        """Get paths to the local ONNX model files"""
        # Look for model files in the same parent directory
        current_dir = Path(__file__).parent  # Go up to project root
        model_file = current_dir / "vi_VN-vais1000-medium.onnx"
        config_file = current_dir / "vi_VN-vais1000-medium.onnx.json"
        
        # Check if files exist
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        logger.info(f"Using local model files: {model_file}")
        
        return {
            "model_path": str(model_file),
            "config_path": str(config_file)
        }
    
    def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech using Piper TTS Python API
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Dictionary containing file path and metadata
        """
        try:
            # Import piper here to avoid import errors if not installed
            import piper 
            
            
            # Validate input
            if not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Get local model paths
            model_paths = self._get_model_paths()
            
            # Generate output filename
            import hashlib
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
            output_filename = f"tts_{text_hash}.wav"
            output_path = self.output_dir / output_filename
            
            # Initialize Piper TTS
            tts = piper.PiperVoice.load(
                model_paths['model_path'],
                config_path=model_paths['config_path']
            )


            # Generate speech
            logger.info(f"Generating speech for text: {text[:50]}...")
            
            syn_config = piper.SynthesisConfig(
                volume=1.5,  
                length_scale=1.8,  # twice as slow
                noise_scale=0.4,  # more audio variation
                noise_w_scale=0.5,  # more speaking variation
                normalize_audio=True, # use raw audio from voice
            )

            with wave.open(str(output_path), 'wb') as wf:
                tts.synthesize_wav(text, wf, syn_config=syn_config)
               
            
            logger.info(f"TTS generation successful: {output_path}")
            
            return {
                "success": True,
                "file_path": str(output_path),
                "file_name": output_filename
            }
            
        except ImportError:
            logger.error("Piper Python API not available")
            return {
                "success": False,
                "error": "Piper Python API not installed. Please run: pip install piper-tts"
            }
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            return {
                "success": False,
                "error": f"Model file not found: {e}"
            }
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 