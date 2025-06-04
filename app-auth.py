from pyrogram import Client

API_ID = int(input('Enter your Telegram API id: '))
API_HASH = input('Enter your Telegram API hash: ')

app = Client('_client', api_id=API_ID, api_hash=API_HASH, no_updates=True)

async def main():
    await app.start()
    await app.send_message("me", "Hi!")
    await app.stop()

app.loop.run_until_complete(main())
