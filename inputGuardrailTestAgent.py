from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    InputGuardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
)
import asyncio
from pydantic import BaseModel, Field

load_dotenv()


# STEP 1: definire un output strutturato (Pydantic) per il risultato del guardrail.
# Deve contenere almeno un campo booleano che indichi se il tripwire va scattato,
# e opzionalmente una stringa con la motivazione.
class DangerOutput(BaseModel):
    is_dangerous: bool = Field(
        description="True if the input is dangerous or unsafe, False otherwise"
    )
    reasoning: str = Field(
        description="Short justification of why it is or isn’t dangerous"
    )


# STEP 2: creare un agente dedicato al controllo del guardrail.
# Questo agente ha output_type impostato al modello Pydantic definito sopra,
# così restituisce sempre una risposta strutturata e interpretabile.
guardrail_agent = Agent(
    name="Guardrail Agent Check",
    instructions="Check if the user is asking about something dangerous.",
    model="gpt-4.1-nano",
    output_type=DangerOutput,
)


# STEP 3: scrivere la funzione guardrail asincrona.
# La firma deve essere: (ctx, agent, input_data) -> GuardrailFunctionOutput
# - Si esegue il guardrail_agent sull'input ricevuto.
# - Si restituisce un GuardrailFunctionOutput con:
#     output_info: informazione da loggare/mostrare (es. la motivazione)
#     tripwire_triggered: True blocca l'esecuzione dell'agente principale
async def dangerous_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output.reasoning,
        tripwire_triggered=result.final_output.is_dangerous,
    )


# STEP 4: creare l'agente principale e collegare il guardrail tramite InputGuardrail.
# input_guardrails accetta una lista, quindi si possono concatenare più guardrail.
# Se il tripwire scatta, viene sollevata InputGuardrailTripwireTriggered prima
# che l'agente principale venga eseguito.
agent = Agent(
    name="Agent",
    instructions="You are a helpful agent",
    model="gpt-4.1-nano",
    input_guardrails=[
        InputGuardrail(guardrail_function=dangerous_guardrail),
    ],
)


async def main():

    while True:
        # STEP 5: gestire l'eccezione InputGuardrailTripwireTriggered nel try/except.
        # Se il tripwire scatta, Runner.run() solleva questa eccezione invece di
        # eseguire l'agente principale. In e.guardrail_result.output.output_info
        # si trova il valore passato a output_info in GuardrailFunctionOutput.
        try:
            user_input = input("Tu: ")

            if user_input.lower() in ["exit", "quit"]:

                break

            result = await Runner.run(agent, user_input)

            print("Jarvis:", result.final_output)

        except InputGuardrailTripwireTriggered as e:
            print(
                "InputGuardrailTripwireTriggered exception caught: ",
                e.guardrail_result.output.output_info,
            )


asyncio.run(main())
