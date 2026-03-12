"""
Audio utilities for voice processing.

Provides microphone selection, VAD, and audio preprocessing.
"""

import logging
import sounddevice as sd
import numpy as np

logger = logging.getLogger(__name__)


class AudioUtils:
    """
    Utilities for audio processing and configuration.
    """
    
    @staticmethod
    def list_microphones():
        """
        List all available microphone devices.
        
        Returns:
            list: List of (index, name) tuples
        """
        devices = sd.query_devices()
        microphones = []
        
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                microphones.append((idx, device['name']))
                logger.debug(f"Microphone {idx}: {device['name']}")
        
        return microphones
    
    @staticmethod
    def get_default_microphone():
        """
        Get the default input device.
        
        Returns:
            int: Device index
        """
        try:
            device = sd.query_devices(kind='input')
            logger.info(f"Default microphone: {device['name']}")
            return device['index']
        except Exception as e:
            logger.error(f"❌ Error getting default microphone: {e}")
            return None
    
    @staticmethod
    def test_microphone(device_index=None, duration=3):
        """
        Test microphone recording.
        
        Args:
            device_index (int): Device to test (None for default)
            duration (int): Test duration in seconds
            
        Returns:
            bool: True if test successful
        """
        try:
            logger.info(f"Testing microphone for {duration} seconds...")
            
            # Record audio
            sample_rate = 16000
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                device=device_index
            )
            sd.wait()
            
            # Check if audio was captured
            max_amplitude = np.max(np.abs(recording))
            
            if max_amplitude > 0.01:
                logger.info(f"✅ Microphone test passed (amplitude: {max_amplitude:.3f})")
                return True
            else:
                logger.warning(f"⚠️ Very low audio detected (amplitude: {max_amplitude:.3f})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Microphone test failed: {e}")
            return False
    
    @staticmethod
    def calculate_rms(audio_data):
        """
        Calculate RMS (root mean square) of audio.
        
        Args:
            audio_data (np.array): Audio samples
            
        Returns:
            float: RMS value
        """
        return np.sqrt(np.mean(audio_data**2))
    
    @staticmethod
    def is_speech(audio_data, threshold=0.02):
        """
        Simple voice activity detection.
        
        Args:
            audio_data (np.array): Audio samples
            threshold (float): Energy threshold
            
        Returns:
            bool: True if speech detected
        """
        rms = AudioUtils.calculate_rms(audio_data)
        return rms > threshold


def select_microphone_interactive():
    """
    Interactive microphone selection.
    
    Returns:
        int: Selected device index
    """
    print("\n🎤 Available Microphones:")
    mics = AudioUtils.list_microphones()
    
    for idx, name in mics:
        print(f"  [{idx}] {name}")
    
    while True:
        try:
            choice = input("\nSelect microphone (or press Enter for default): ").strip()
            
            if not choice:
                return AudioUtils.get_default_microphone()
            
            choice = int(choice)
            if any(idx == choice for idx, _ in mics):
                print(f"✅ Selected: {choice}")
                return choice
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n⚠️ Cancelled")
            return None
