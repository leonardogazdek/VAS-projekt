import spade
from asyncio import sleep as asleep
import json
from globals import totalServers, initialResourceUsage, xmppServer

class Gateway(spade.agent.Agent):
    def getServerWithLowestResourceUsage(self) -> int:
        minUsage = 100.0
        serverIndex = 0
        for idx, info in enumerate(self.serverInfo):
            if info["resourceUsage"] < minUsage:
                minUsage = info["resourceUsage"]
                serverIndex = idx

        print(f"Lowest usage: server {serverIndex} with a usage of {minUsage}%")
        return serverIndex

    class HandleMessage(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.get_metadata("ontology") == "request":
                    request = json.loads(msg.body)
                    print(f"Gateway received request with usage {request['resourceUsage']}% and a duration of {request['duration']}ms")
                    await asleep(1)
                    forwardMsg = msg.make_reply()
                    serverToSend = self.agent.getServerWithLowestResourceUsage()
                    forwardMsg.to = f"srv{serverToSend}@{xmppServer}"
                    await self.send(forwardMsg)
                elif msg.get_metadata("ontology") == "inquire":
                    requestedInfo = json.loads(msg.body)
                    self.agent.serverInfo[requestedInfo["serverId"]] = {
                        "resourceUsage": requestedInfo["resourceUsage"]
                    }
                    print(f"Gateway updated server resource info for server {requestedInfo['serverId']} (usage: {requestedInfo['resourceUsage']}%)")
        
    class InquireResourceUsage(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            for i in range(totalServers):
                por = spade.message.Message(
                    to = f"srv{i}@{xmppServer}", 
                    metadata = {
                        "performative": "inform",
                        "ontology": "inquire",
                        "language": "json",
                    }
                )
                await self.send(por)
    async def setup(self):
        self.serverInfo = [{
            "resourceUsage": initialResourceUsage,
        }] * totalServers
        print(f"Gateway listening for requests")
        self.add_behaviour(self.HandleMessage())
        self.add_behaviour(self.InquireResourceUsage(period=5))
        
