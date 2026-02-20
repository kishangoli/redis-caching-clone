import asyncio

STORE = {}

def handle_command(line: str) -> str:
    line = line.strip()

    if line == "":
        return "Empty command, try again"

    parts = line.split(" ", 2)
    cmd = parts[0].upper()

    if cmd == "SANITY":
        return "CHECK"
    
    if cmd == "SET":
        if len(parts) < 3:
            return "SET: Provide 3 arguments"
        
        key = parts[1]
        value = parts[2]

        STORE[key] = value
        return "DONE"
    
    if cmd == "GET":
        if len(parts) < 2:
            return "GET: Provide 2 arguments"
        
        key = parts[1]
        return STORE.get(key, "none")
    
    if cmd == "DEL":
        if len(parts) != 2:
            return "DEL: Provide 2 arguments"
        
        key = parts[1]
        if key in STORE:
            del STORE[key]
            return "1"
        
        return "0"
    
    if cmd == "EXISTS":
        if len(parts) != 2:
            return "EXISTS: Provide 2 arguments"
        
        key = parts[1]
        if key in STORE:
            return "1"
        else:
            return "0"
    
    return "Unknown Command"

async def handle_client(reader, writer): #reads incoming bytes, writes outgoing bytes
    writer.write(b"Mini-Redis Ready\n")
    await writer.drain()

    while True:
        data = await reader.readline()
        if not data:
            break

        line = data.decode("utf-8")
        response = handle_command(line)
        writer.write((response + "\n").encode("utf-8"))
        await writer.drain()

    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 5000) #opens the TCP port for comms
    print("Listening on 127.0.0.1:5000")
    async with server:
        await server.serve_forever()


asyncio.run(main())

