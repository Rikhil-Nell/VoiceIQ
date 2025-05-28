from groq import AsyncGroq
from settings import Settings
from transcription import TranscriptionService
import asyncio

settings = Settings()

groq_client = AsyncGroq(api_key=settings.groq_api_key)

transcription_service = TranscriptionService(groq_client=groq_client)

async def main():

    files = ["external-9079-+16512383442-20250328-145316-1743191596.46379.mp3","in-14424172002-+13463059711-20250328-172122-1743200482.65970.mp3","in-14424172003-+12514593835-20250328-150727-1743192447.48406.mp3","in-14424172003-+13215871302-20250328-171150-1743199910.64811.mp3"]
    tasks = [transcription_service.transcribe_groq(file_path=file) for file in files] 
    results = await asyncio.gather(*tasks)
    for file, result in zip(files, results):
        print(f"\n=== Transcription result for: {file} ===")
        print(result)
        print("=" * 40)

if __name__ == "__main__":
    asyncio.run(main())