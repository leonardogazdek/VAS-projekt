import time
import spade
from secrets import choice as randChoice
from asyncio import sleep as asleep
import argparse
from server import Server
from gateway import Gateway
from generator import RequestGenerator
from globals import totalServers, xmppServer


if __name__ == "__main__":
    def startServers() -> list[Server]:
        runningServers: list[Server] = [None] * totalServers
        for i in range(len(runningServers)):
            runningServers[i] = Server(f"srv{i}@{xmppServer}", f"srv{i}")
            runningServers[i].start().result()

        return runningServers

    def startGateway():
        runningGateway = Gateway(f"Gateway@{xmppServer}", "Gateway")
        runningGateway.start().result() 
    
    def startRequestGenerator():
        runningRequestGenerator = RequestGenerator(f"RequestGenerator@{xmppServer}", "RequestGenerator")
        runningRequestGenerator.start().result()


    
    runningServers = startServers()
    startGateway()
    startRequestGenerator()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for server in runningServers:
            server.stop()