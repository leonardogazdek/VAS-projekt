import spade
import json
from random import randint
from globals import xmppServer

class RequestGenerator(spade.agent.Agent):
    class GenerateRequest(spade.behaviour.PeriodicBehaviour):
        async def run(self) -> None:
            por = spade.message.Message(
                to = f"Gateway@{xmppServer}", 
                body = json.dumps({
                    "resourceUsage": randint(5, 40),
                    "duration": randint(1500, 30000),
                }), 
                metadata = {
                    "performative": "inform",
                    "ontology": "request",
                    "language": "json",
                }
            )
            await self.send(por)

    async def setup(self):
        print(f"Request generator started")
        self.add_behaviour(self.GenerateRequest(period=2))