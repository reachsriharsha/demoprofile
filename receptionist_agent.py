import os
import logging
import threading
from datetime import datetime

from livekit import agents
from livekit.agents.llm import function_tool
from livekit.plugins import openai, sarvam, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import (
    NOT_GIVEN,
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    RunContext,
    AgentFalseInterruptionEvent
)

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)



class AIReceptionist(Agent):

    def __init__(self):
        self.tz = "Asia/Kolkata"  # Set your timezone here
        today = datetime.now().astimezone().strftime("%Y-%m-%d")

        super().__init__(
            instructions=
                f"""You are an AI receptionist PANDA. Today's date is {today}. Greet the user in English."
                    You eagerly assist users with their questions by providing information from your extensive knowledge.
                    Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
                    You are curious, friendly, and have a sense of humor.""",   
        )




    # Prewarm function to load VAD model
def prewarm(proc: JobProcess):
        proc.userdata["vad"] = silero.VAD.load()

    
async def entrypoint(ctx: JobContext):
        ctx.log_context_fields = {
            "room": ctx.room.name,
        }

        # Initialize the agent session with STT, LLM, TTS, and VAD
        session = AgentSession(
            stt=sarvam.STT(language="en-IN",api_key=os.environ.get("SARVAMAI_API_KEY")),  # or "en-IN" for Indian English
            llm=openai.LLM(model="gpt-4o-mini", temperature=0.5),
            turn_detection=MultilingualModel(),
            tts=sarvam.TTS(target_language_code="en-IN", speaker="anushka",api_key=os.environ.get("SARVAMAI_API_KEY")),  # or "abhilash
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
        )

        @session.on("agent_false_interruption")
        def _on_agent_false_interruption(ev: AgentFalseInterruptionEvent):
            session.generate_reply(instructions=ev.extra_instructions or NOT_GIVEN)

        await session.start(agent=AIReceptionist(),
                            room=ctx.room
        )

        await ctx.connect()


if __name__ == "__main__":
        agents.cli.run_app(
            agents.WorkerOptions(
                entrypoint_fnc=entrypoint,
                prewarm_fnc=prewarm
            )
        )

#Initialize and run the AI Receptionist worker
#agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
