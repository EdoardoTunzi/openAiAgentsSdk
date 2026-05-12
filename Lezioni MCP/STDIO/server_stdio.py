from math import sqrt

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("myServerStdio")

@mcp.tool()
def get_user_by_id(user_id:str) -> str:
    """Restituisce il nome dell'utente a partire dal suo ID"""
    if user_id == "0000":
        return "Mario Rossi"

    elif user_id == "0001":
        return "Lucia Bianchi"

    elif user_id == "0002":
        return "Carlo Verdi"

    else:
        return "Utente sconosciuto"
    
    
@mcp.tool()
def is_prime(n: int) -> bool:
    """Verifica se un certo numero n è primo"""
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

    
@mcp.tool()
def prompt_creative_writing(topic: str) -> str:
    """Template per scrittura creativa su un argomento specifico"""
    
    return f"""
    Sei un esperto scrittore creativo. Il tuo compito è aiutare l'utente a sviluppare una storia coinvolgente.

    ARGOMENTO: {topic} e Samurai. Racconta una storia che parla di {topic} e un Samurai
    
    STRUTTURA DA SEGUIRE:
    1. Inizia con un'ambientazione vivida e dettagliata
    2. Introduci un personaggio principale con una caratteristica distintiva
    3. Presenta un conflitto o mistero da risolvere
    4. Sviluppa la tensione narrativa
    5. Concludi con una risoluzione soddisfacente
    
    STILE:
    - Usa descrizioni sensoriali ricche
    - Varia il ritmo narrativo
    - Includi dialoghi autentici
    - Mantieni il lettore coinvolto
"""


if __name__ == "__main__":

    # -------------------------
    # Transport 'stdio' significa che il client e il server MCP comunicano tramite lo standard input/output (stdin/stdout) del sistema operativo.
    # In pratica, il server viene avviato come sottoprocesso e i messaggi MCP (in formato JSON-RPC) viaggiano direttamente tra i due processi,
    # senza passare per la rete. È ideale per l’integrazione locale o per testare rapidamente nuovi server MCP.
    # -------------------------
    mcp.run(transport="stdio")

    # -------------------------
    # transport="streamable-http" indica che il server MCP comunica tramite il protocollo HTTP,
    # utilizzando una connessione persistente che permette di inviare e ricevere dati in streaming.
    # Questo tipo di transport è pensato per collegare client e server che si trovano su macchine diverse (rete locale o Internet),
    # e supporta lo scambio continuo di messaggi (streaming) durante una singola sessione HTTP.
    # È la modalità consigliata per la comunicazione remota, scalabile e compatibile con firewall e cloud.
    # -------------------------
    # mcp.run(transport="streamable-http")

    # -------------------------
    # transport="sse" (Server-Sent Events) significa che il server MCP invia dati al client attraverso una connessione HTTP unidirezionale.
    # Il client si collega a un endpoint HTTP e rimane in ascolto di messaggi/eventi inviati dal server.
    # SSE è utile per ricevere aggiornamenti in tempo reale (notifiche, progressi, risposte parziali),
    # ma la comunicazione è principalmente dal server verso il client, non bidirezionale come WebSocket.
    # È spesso usato per implementare lo streaming di risposte da LLM o tool remoti.
    # -------------------------
    # mcp.run(transport="sse")
