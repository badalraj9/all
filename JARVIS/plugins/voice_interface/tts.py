import asyncio
import edge_tts
import pygame
import os
import tempfile
from loguru import logger
from JARVIS.core.event_bus import event_bus, Event

class TTSEngine:
    def __init__(self, voice="en-GB-RyanNeural"):
        self.voice = voice
        self.temp_dir = tempfile.mkdtemp()
        self.is_speaking = False

        # Initialize PyGame Mixer
        try:
            # We set frequency to match typical edge-tts output (24khz)
            pygame.mixer.init(frequency=24000, buffer=4096)
            logger.info(f"TTS Engine initialized with voice: {self.voice}")
        except Exception as e:
            logger.error(f"Failed to initialize PyGame mixer: {e}")

    async def speak(self, text: str):
        """
        Generates audio for the text and plays it.
        """
        if not text or len(text.strip()) == 0:
            return

        self.is_speaking = True
        logger.info(f"TTS Speaking: {text[:50]}...")

        try:
            # Generate unique filename
            output_file = os.path.join(self.temp_dir, f"speech_{hash(text)}.mp3")

            # Communicate with Edge TTS
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)

            # Play Audio
            if pygame.mixer.get_init():
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()

                # Wait for playback to finish (non-blocking wait)
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            else:
                logger.warning(f"Audio device not available. Saved speech to: {output_file}")

        except Exception as e:
            logger.error(f"TTS Error: {e}")
        finally:
            self.is_speaking = False

    async def stop(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.is_speaking = False

# Singleton
tts_engine = TTSEngine()
