from routers.websocket import connected_clients


async def broadcast(message):

    for client in connected_clients:

        try:

            await client.send_json(message)

        except:

            pass