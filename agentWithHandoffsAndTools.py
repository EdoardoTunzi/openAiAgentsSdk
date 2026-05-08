from dotenv import load_dotenv
import os
from agents import Agent, Runner, function_tool, SQLiteSession
import asyncio
from pydantic import BaseModel, Field

""" Esercizio semplice di agente con handoff di HR e agent as tool. 
Il triage agent decide se rispondere direttamente, usare il company directory tool o fare handoff all'hr_agent in base alla domanda dell'utente.
Il company directory agent è un semplice agente che fornisce numeri di telefono dei dipendenti tramite un tool.
L'hr_agent gestisce richieste di ferie e saldo ferie tramite i tool get_remaining_vacation_days e request_vacation."""

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
session = SQLiteSession("handoffs_conversation")


class MessageOutput(BaseModel):
    response: str = Field(description="Response to the user question")
    explanation: str = Field(description="Explanation for the given answer")


@function_tool
async def get_employee_phone_by_name(employee_name: str) -> str:
    """Returns the phone number of an employee given their name."""
    employee_directory = {
        "Alice Rossi": "555-1234",
        "Bob Bianchi": "555-5678",
        "Charlie Verdi": "555-9012",
    }
    return employee_directory.get(employee_name, "Employee not found")


@function_tool
async def get_remaining_vacation_days(employee_name: str) -> str:
    """Returns the remaining vacation days for an employee given their name."""
    employee_vacation_days = {
        "Alice Rossi": 23,
        "Bob Bianchi": 15,
        "Charlie Verdi": 30,
    }
    return employee_vacation_days.get(employee_name, "Employee not found")


@function_tool
async def request_vacation(days: int, employee_name: str) -> str:
    """Simulates a vacation request for a given number of days."""

    if days <= 0:
        return "Invalid number of days. Please enter a positive integer."
    elif days > 30:
        return "Vacation request denied. Maximum allowed vacation is 30 days."
    else:
        return f"Vacation request for {days} days has been submitted for approval for {employee_name}."


# Agent as tool che fornisce numeri di telefono dei dipendenti
company_directory_agent = Agent(
    name="Company Directory Agent",
    instructions="You are a helpful assistant that provides employee phone numbers. "
    "When the user asks for an employee's phone number, use the get_employee_phone_by_name tool to retrieve it. "
    "If the user asks for something else, respond that you can only provide employee phone numbers.",
    model="gpt-4.1-nano",
    output_type=MessageOutput,
    tools=[get_employee_phone_by_name],
)

company_directory_tool = company_directory_agent.as_tool(
    tool_name="company_directory",
    tool_description="Provides employee phone numbers based on their name",
)

# Handoff Agent HR
hr_agent = Agent(
    name="hr_agent",
    handoff_description="Use this agent for vacation requests, leave balances, time off policies, and HR-related employee support. ",
    instructions="You are a helpful assistant that manages HR-related questions. If the user asks about vacation balances, use get_remaining_vacation_days. "
    "If the user requests vacation days, first check remaining days, then use request_vacation if enough days are available. "
    "Always check remaining vacation days before submitting a vacation request. "
    "For any other HR-related questions, answer directly.",
    model="gpt-4.1-nano",
    tools=[request_vacation, get_remaining_vacation_days],
    output_type=MessageOutput,
)

# Triage
triage_agent = Agent(
    name="Triage Agent",
    instructions="You are a helpful assistant called Jarvis. Reply very concisely and politely. "
    "You are a company assistant chatbot. If the user asks for employee contact information, use company_directory tool. "
    "If the user asks HR-related questions, use the hr_agent. Otherwise, answer directly.",
    model="gpt-4.1-nano",
    output_type=MessageOutput,
    tools=[company_directory_tool],
    handoffs=[hr_agent],
)


async def main():

    while True:

        user_input = input("Tu: ")

        if user_input.lower() in ["exit", "quit"]:

            break

        result = await Runner.run(triage_agent, user_input, session=session)

        print("Jarvis:", result.final_output.response)
        print("Why:", result.final_output.explanation)


asyncio.run(main())
