import asyncio
HOST = '0.0.0.0'
PORT = 5355

WRITERS = set()

async def handle_echo(reader, writer):
    WRITERS.add(writer)

    while True:
        data = await reader.read(100)
        if not data:
            writer.close()
            break

        for w in WRITERS:
            if w == writer:
                continue
            w.write(data)

        await asyncio.gather(*(w.drain() for w in WRITERS if w != writer))

async def main():
    server = await asyncio.start_server(
        handle_echo, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
