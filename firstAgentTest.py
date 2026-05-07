# --- Importazioni ---
# load_dotenv carica le variabili d'ambiente dal file .env (es. la API key)
from dotenv import load_dotenv
import os

# Agent è il "cervello" dell'AI, Runner è quello che lo esegue
from agents import Agent, Runner

# asyncio serve per usare le funzioni async/await (programmazione asincrona)
import asyncio

# BaseModel e Field di pydantic servono per definire la struttura dell'output in modo tipizzato
from pydantic import BaseModel, Field

# SQLiteSession permette di salvare la cronologia della conversazione in un database SQLite locale
from agents import SQLiteSession

# Carica le variabili dal file .env nella sessione corrente
load_dotenv()
# Legge la chiave API di OpenAI dalla variabile d'ambiente
api_key = os.getenv("OPENAI_API_KEY")
# Crea (o recupera) una sessione persistente chiamata "conversation"
# Questo fa sì che il modello ricordi i messaggi precedenti tra una run e l'altra
session = SQLiteSession("conversation")


# Definisco la struttura dell'output che voglio ricevere dall'agente
# Invece di una stringa libera, il modello deve rispondere con questi due campi
class MessageOutput(BaseModel):
    response: str = Field(description="Response to the user question")
    explanation: str = Field(description="Explanation for the given answer")


# Creo l'agente specificando:
# - name: nome identificativo
# - instructions: il "system prompt", cioè come si deve comportare
# - model: quale modello OpenAI usare
# - output_type: il formato strutturato che deve restituire (la classe sopra)
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant called Jarvis.Reply very concisely.",
    model="gpt-4.1-nano",
    output_type=MessageOutput,
)


# Esempio base (commentato): esegue l'agente una sola volta con un messaggio fisso
# e stampa l'output strutturato
""" async def main():
    result = await Runner.run(agent, "sai dirmi come mi chiamo?", session=session)
    print(result.final_output) """


# Funzione principale asincrona: gestisce una chat in loop con l'utente
async def main():

    # Loop infinito: continua a chiedere input finché l'utente non scrive "exit" o "quit"
    while True:

        user_input = input("Tu: ")

        # Condizione di uscita dal loop
        if user_input.lower() in ["exit", "quit"]:

            break

        # Esegue l'agente con il messaggio dell'utente e la sessione attiva
        # await sospende l'esecuzione finché il modello non risponde
        result = await Runner.run(agent, user_input, session=session)

        # Stampa i due campi dell'output strutturato
        print("Jarvis:", result.final_output.response)

        print("Why:", result.final_output.explanation)


# Punto di ingresso: lancia la funzione asincrona main() con asyncio
asyncio.run(main())
