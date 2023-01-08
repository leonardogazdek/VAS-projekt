from asyncio import sleep as asleep
import spade
from globals import servers, initialResourceUsage
import json
import threading

class Server(spade.agent.Agent):
    class HandleRequest(spade.behaviour.CyclicBehaviour):
        def finishRequestProcessing(self, usage):
            print(f"Server {self.agent.serverId} finished processing request")
            self.agent.resourceUsage -= usage
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.get_metadata("ontology") == "inquire":
                    reply = msg.make_reply()
                    reply.body = json.dumps({
                        "serverId": self.agent.serverId,
                        "resourceUsage": self.agent.resourceUsage
                    })
                    await self.send(reply)
                elif msg.get_metadata("ontology") == "request":
                    request = json.loads(msg.body)
                    newUsage = self.agent.resourceUsage + request['resourceUsage']
                    if newUsage > 100.0:
                        print(f"Server {self.agent.serverId} has too many requests, request not processed")
                        return
                    else:
                        self.agent.resourceUsage = newUsage
                    print(f"Server {self.agent.serverId} received request with usage {request['resourceUsage']}% and a duration of {request['duration']}ms")
                    start_time = threading.Timer(request['duration'] * 0.001, self.finishRequestProcessing, [request['resourceUsage']])
                    start_time.start()


                    
    async def setup(self):
        self.resourceUsage = initialResourceUsage
        global servers
        self.serverId = servers
        servers = servers + 1
        print(f"Server ID {self.serverId} listening for requests")
        self.add_behaviour(self.HandleRequest())