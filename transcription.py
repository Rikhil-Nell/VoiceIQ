import os
import mimetypes
import requests
from groq import Groq

class TranscriptionService:
    def __init__(self, groq_client: Groq):
        self.groq_client = groq_client
        self.remote_url = "https://guest1.indominuslabs.in/transcribe"

    def _load_audio_file(self, file_path: str) -> tuple[str, bytes, str]:
        """Returns filename, file bytes, and MIME type."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        return os.path.basename(file_path), file_bytes, mime_type

    async def transcribe_local(self, file_path: str) -> str:
        """Uses external transcription API via HTTP POST."""
        filename, file_bytes, mime_type = self._load_audio_file(file_path)
        files = {'file': (filename, file_bytes, mime_type)}
        response = requests.post(self.remote_url, files=files)

        if response.ok:
            return response.text
        else:
            raise RuntimeError(f"Transcription failed: {response.status_code} - {response.text}")

    async def transcribe_groq(self, file_path: str, prompt: str = "Specify context or spelling") -> str:
        """Uses Groq's Whisper API to transcribe audio."""
        _, file_bytes, _ = self._load_audio_file(file_path)
        print(f"Processing: {file_path}")
        with open(file_path, "rb") as f:
            transcription = await self.groq_client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3-turbo",
                prompt=prompt,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language="en",
                temperature=0.0
            )
        return transcription.text
