import asyncio
import time

STORE = {}

def purge_if_expired(key: str) -> bool: #returns false is doesn't exist, true otherwise
    item = STORE.get(key)
    if not item:
        return False
    
    value, expires_at = item
    if expires_at is None:
        return True
    
    now = time.time()
    if now >= expires_at:
        del STORE[key]
        return False
    
    return True


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

        STORE[key] = (value, None)
        return "DONE"
    
    if cmd == "GET":
        if len(parts) < 2:
            return "GET: Provide 2 arguments"
        
        key = parts[1]
        
        if not purge_if_expired(key):
            return "none"

        item = STORE.get(key)
        
        value, expires_at = item
        return value
    
    if cmd == "DEL":
        if len(parts) != 2:
            return "DEL: Provide 2 arguments"
        
        key = parts[1]
        
        if not purge_if_expired(key):
            return "0"
        
        del STORE[key]
        return "1"
    
    if cmd == "EXISTS":
        if len(parts) != 2:
            return "EXISTS: Provide 2 arguments"
        
        key = parts[1]

        if not purge_if_expired(key):
            return "0"
        else:
            return "1"
    
    if cmd == "EXPIRE":
        parts2 = line.split(" ", 2)
        if len(parts2) != 3:
            return "EXPIRE: Provide 3 arguments"
        
        key = parts2[1]
        seconds_str = parts2[2]

        if not purge_if_expired(key):
            return "0"

        try:
            seconds = int(seconds_str)
        except ValueError:
            return "EXPIRE: seconds must be an integer"
        
        value, old_expires_at = STORE[key]
        expires_at = time.time() + seconds
        STORE[key] = (value, expires_at)
        return "1"

    if cmd == "TTL":
        if len(parts) != 2:
            return "TTL: Provide 2 arguments"
        
        key = parts[1]

        if not purge_if_expired(key):
            return "-2"

        value, expires_at = STORE[key]
        if expires_at is None:
            return "-1"

        remaining = int(expires_at - time.time())
        if remaining < 0:
            del STORE[key]
            return "-2"
        
        return str(remaining)



    
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

