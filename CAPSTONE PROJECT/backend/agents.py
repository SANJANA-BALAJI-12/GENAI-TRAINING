import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from rag import FarmingRAG

# Ensure Environment variables are loaded in main.py before this is imported

def run_farming_crew(user_query: str) -> str:
    # Initialize the LLM via ChatGroq (using the Groq API key)
    # Using llama3-8b-8192 or miuxtral for speed/cost effectiveness inside CrewAI
    llm = ChatGroq(model="llama3-8b-8192", api_key=os.environ.get("GROQ_API_KEY"))

    # Initialize RAG for context
    rag_system = FarmingRAG()
    context_docs = rag_system.query(user_query)
    context_str = "\n".join(context_docs)

    # Agent 1: The Crop Advisor
    crop_advisor = Agent(
        role='Senior Agricultural Advisor',
        goal='Provide highly actionable, scientifically accurate farming advice based on user queries and RAG context.',
        backstory="An expert agronomist with decades of experience helping farmers maximize yield and manage soil health.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Task for the Crop Advisor
    advisor_task = Task(
        description=f'''
        Analyze the following farmer's query and provide a detailed, easy-to-understand recommendation.
        Incorporate the relevant RAG knowledge provided. Keep the tone friendly, encouraging, and highly professional.
        
        Farmer Query: {user_query}
        Local Knowledge Base Context: {context_str}
        ''',
        expected_output="A well-structured markdown response containing actionable farming advice, step-by-step instructions if applicable, and an encouraging closing.",
        agent=crop_advisor
    )

    crew = Crew(
        agents=[crop_advisor],
        tasks=[advisor_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)
