import discord
from openai import OpenAI

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# OpenAI Client setting
openai_api_key = '####'  #OpenAI Api Key
openai_client = OpenAI(api_key=openai_api_key)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text = message.content
    if text.startswith('!bot '):
        prompt = text[6:]
        # OpenAI API response
        try:
            response = openai_client.completions.create(
                model="gpt-3.5-turbo-instruct",  # GPT-model
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            bot_response = response.choices[0].text.strip()
        except Exception as e:
            bot_response = f"An error occurred: {str(e)}"
        
        # send Discord message
        await message.channel.send(f"{bot_response}")

# Discord Bot Token
DISCORD_BOT_TOKEN = '####'  # Input Discord Token

# Discord Bot run
client.run(DISCORD_BOT_TOKEN)