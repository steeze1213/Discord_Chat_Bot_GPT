import discord
from openai import OpenAI

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# OpenAI Client setting
openai_api_key = '####'  # OpenAI Api Key
openai_client = OpenAI(api_key=openai_api_key)

# Dictionary to store recent messages of users
recent_messages = {}

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

    elif text == '!help':
        await message.channel.send("bot에게 명령을 하려면 '!bot + 명령'이라고 입력해보세요.")

    # Store recent messages of users
    user_id = str(message.author.id)
    recent_messages.setdefault(user_id, []).append(message.content)
    if len(recent_messages[user_id]) > 10:
        recent_messages[user_id] = recent_messages[user_id][-10:]

# Discord Bot Token
DISCORD_BOT_TOKEN = '####'  # Input Discord Token

# Discord Bot run
client.run(DISCORD_BOT_TOKEN)
