from transcription import TranscriptionService
from santization import SanitizationService
from agents import deps, call_log_agent, report_agent, database_agent, chat_agent, async_groq_client
from memory import MemoryHandler
from database import DatabaseHandler
from filename_parser import parse_call_filename

from pydantic_ai.messages import SystemPromptPart, ModelRequest
import traceback
from uuid import UUID
import re
from settings import Settings

settings = Settings()

transcription_service = TranscriptionService(groq_client=async_groq_client)

sanitization_service = SanitizationService(groq_client=async_groq_client)

memory = MemoryHandler(deps=deps)

db = DatabaseHandler(deps=deps)

async def main(file_path: str) -> str:
    try:
        transcript = await transcription_service.transcribe_groq(file_path=file_path)
        sanitized_transcript = await sanitization_service.sanitize(transcript=transcript)
        print("✅ Transcription and sanitization successful.")
        
        call_log_agent_response = await call_log_agent.run(user_prompt=sanitized_transcript)
        report_agent_response = await report_agent.run(user_prompt=sanitized_transcript)
        report_cleaned_response = re.sub(r'<think>.*?</think>', '', report_agent_response.output, flags=re.DOTALL)
        database_agent_response = await database_agent.run(user_prompt=sanitized_transcript)
        if not database_agent_response.output:
            raise ValueError("Database Agent failed to extract structured data")
        print("✅ Agents executed successfully.")
        
        metadata = await parse_call_filename(filename=file_path)
        
        payload : dict = {
            "responder_name": database_agent_response.output.responder_name,
            "caller_name": database_agent_response.output.caller_name,
            "request_type": database_agent_response.output.request_type,
            "issue_summary": database_agent_response.output.issue_summary,
            "caller_sentiment": database_agent_response.output.caller_sentiment,
            "report_generated": report_cleaned_response,
            "call_log": call_log_agent_response.output,
            "transcription": sanitized_transcript,
            "filename": metadata["filename"],
            "call_type": metadata["call_type"],
            "toll_free_did": metadata["toll_free_did"],
            "agent_extension": metadata["agent_extension"],
            "customer_number": metadata["customer_number"],
            "call_date": metadata["call_date"],
            "call_start_time": metadata["call_start_time"],
            "call_id": metadata["call_id"]
        }
        

        print("✅ Payload created successfully.")
        
        response = await db.create_call_log(data=payload)
        id = response.get("id")
        print("✅ Log inserted successfully.")

        return id
    
    except Exception as e:
        print(traceback.format_exc())


async def chat(user_prompt: str, uuid : UUID) -> str:

    user_id : str = "TestUser"

    messages = await memory.get_memory(user_id=user_id, limit=20)

    await memory.append_message(user_id=user_id, role="user", content=user_prompt)
    
    transcription = await db.get_transcription(uuid=uuid)
    messages.append(ModelRequest(parts=[SystemPromptPart(content=transcription["transcription"])]))
    
    response = await chat_agent.run(user_prompt=user_prompt, message_history=messages)
    bot_response = response.output
    
    await memory.append_message(user_id=user_id, role="bot", content=bot_response)

    return bot_response
