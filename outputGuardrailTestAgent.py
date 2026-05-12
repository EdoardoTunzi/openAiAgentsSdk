from agents import (
    Agent,
    Runner,
    GuardrailFunctionOutput,
    OutputGuardrail,
    OutputGuardrailTripwireTriggered,
)
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio

load_dotenv()


# STEP 1: definire un output strutturato (Pydantic) per il risultato del guardrail.
# Deve contenere almeno un campo booleano che indichi se il tripwire va scattato,
# e opzionalmente una stringa con la motivazione.
class MathOutput(BaseModel):
    is_math: bool = Field(
        description="True if the input is a math-related question, False otherwise"
    )
    reasoning: str = Field(
        description="Short justification of why it is or isn’t math-related"
    )


# STEP 2: creare un agente dedicato al controllo del guardrail.
# Questo agente ha output_type impostato al modello Pydantic definito sopra,
# così restituisce sempre una risposta strutturata e interpretabile.
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the input includes any math",
    output_type=MathOutput,
    model="gpt-4.1-nano",
)


# STEP 3: scrivere la funzione guardrail asincrona.
# La firma deve essere: (ctx, agent, output) -> GuardrailFunctionOutput
# A differenza dell'input guardrail, qui il terzo parametro è l'OUTPUT dell'agente principale.
# - Si esegue il guardrail_agent sull'output ricevuto.
# - Si restituisce un GuardrailFunctionOutput con:
#     output_info: informazione da loggare/mostrare (es. la motivazione)
#     tripwire_triggered: True blocca la restituzione dell'output all'utente
async def math_guardrail(ctx, agent, output):
    result = await Runner.run(guardrail_agent, output, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output.reasoning,
        tripwire_triggered=result.final_output.is_math,
    )


# STEP 4: creare l'agente principale e collegare il guardrail tramite OutputGuardrail.
# output_guardrails accetta una lista, quindi si possono concatenare più guardrail.
# Il guardrail viene eseguito DOPO che l'agente principale ha prodotto l'output;
# se il tripwire scatta, viene sollevata OutputGuardrailTripwireTriggered.
agent = Agent(
    name="Agent",
    instructions="You are a helpful agent",
    model="gpt-4.1-nano",
    output_guardrails=[
        OutputGuardrail(guardrail_function=math_guardrail),
    ],
)


async def main():

    while True:
        # STEP 5: gestire l'eccezione OutputGuardrailTripwireTriggered nel try/except.
        # Se il tripwire scatta, Runner.run() solleva questa eccezione invece di
        # eseguire l'agente principale. In e.guardrail_result.output.output_info
        # si trova il valore passato a output_info in GuardrailFunctionOutput.
        try:
            user_input = input("Tu: ")

            if user_input.lower() in ["exit", "quit"]:

                break

            result = await Runner.run(agent, user_input)

            print("Jarvis:", result.final_output)

        except OutputGuardrailTripwireTriggered as e:
            print(
                "OutputGuardrailTripwireTriggered exception caught: ",
                e.guardrail_result.output.output_info,
            )


asyncio.run(main())
