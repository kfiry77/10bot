from contextlib import asynccontextmanager
from fastapi import FastAPI
from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv
from neonize.utils import build_jid

whatsapp_client = NewAClient("fastapi_bot")
whatsapp_client.connect()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('connecting..')

    print('done')
    yield
    # Clean up the ML models and release the resources
    await whatsapp_client.disconnect()
    print('..')
app = FastAPI(lifespan=lifespan)

@whatsapp_client.event
async def on_message(client: NewAClient, event: MessageEv):
    # Handle WhatsApp messages in your FastAPI app
    if event.message.conversation == "/api_status":
        await client.reply_message("API is running! ✅", event.message)

@app.get("/send-message")
async def send_message(phone: str, message: str):
    jid = build_jid(phone)
    await whatsapp_client.send_message(jid, message)
    return {"status": "sent"}