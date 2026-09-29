import asyncio

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import load_memory
from google.genai.types import Content, Part


load_dotenv()


APP_NAME = "travel_memory_demo"
USER_ID = "akash"
MODEL = "gemini-3.5-flash-lite"


# ---------------------------------------------------------
# Agent used in Session 1
# ---------------------------------------------------------

capture_agent = Agent(
    name="capture_agent",
    model=MODEL,
    instruction="""
    Listen to the user's information and acknowledge it.

    Do not invent additional information.
    """,
)


# ---------------------------------------------------------
# Agent used in Session 2
# ---------------------------------------------------------

recall_agent = Agent(
    name="recall_agent",
    model=MODEL,
    instruction="""
    Answer the user's question.

    The answer may exist in a previous conversation.

    When information might come from a previous conversation, use the load_memory tool to search memory before answering.
    """,
    tools=[load_memory],
)


async def main():
    # -----------------------------------------------------
    # Shared services
    # -----------------------------------------------------

    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()


    # =====================================================
    # SESSION 1
    # =====================================================

    print("\n===== SESSION 1 =====\n")

    session1_id = "session_1"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session1_id,
    )

    runner1 = Runner(
        agent=capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    message1 = Content(
        parts=[
            Part(
                text=(
                    "I'm planning a 5-day trip to Tokyo with my parents. "
                    "We love history and culture and prefer minimal walking."
                )
            )
        ],
        role="user",
    )

    async for event in runner1.run_async(
        user_id=USER_ID,
        session_id=session1_id,
        new_message=message1,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)


    # -----------------------------------------------------
    # Add Session 1 to memory
    # -----------------------------------------------------

    completed_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session1_id,
    )

    await memory_service.add_session_to_memory(completed_session)

    print("\nSession 1 added to memory.")


    # =====================================================
    # SESSION 2
    # =====================================================

    print("\n===== SESSION 2 =====\n")

    session2_id = "session_2"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session2_id,
    )

    runner2 = Runner(
        agent=recall_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    message2 = Content(
        parts=[
            Part(
                text="What do you remember about my Tokyo trip?"
            )
        ],
        role="user",
    )

    async for event in runner2.run_async(
        user_id=USER_ID,
        session_id=session2_id,
        new_message=message2,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())