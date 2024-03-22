import discord
from openai import OpenAI
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# OpenAI Client setting
openai_api_key = '####################'  # OpenAI Api Key
openai_client = OpenAI(api_key=openai_api_key)

# Dictionary to store recent messages of users
recent_messages = {}

# Dictionary to store game state for each user
game_sessions = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]

        if added_roles:
            added_role_names = ', '.join([role.name for role in added_roles])
            await after.guild.system_channel.send(f'🛡️ {after.mention} 님이 역할 [{added_role_names}]을(를) 획득하셨습니다!')
        if removed_roles:
            removed_role_names = ', '.join([role.name for role in removed_roles])
            await after.guild.system_channel.send(f'❌ {after.mention} 님이 역할 [{removed_role_names}]을(를) 잃으셨습니다.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text = message.content
    if text.startswith('!bot '):
        prompt = text[9:]
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
        await message.channel.send("'!game'을 입력하여 간단한 숫자 게임을 즐겨보세요.")
        await message.channel.send("'!timer + [초]'를 입력하여 타이머를 사용해보세요.")
    
    elif text == '!game':
        if str(message.author.id) not in game_sessions:
            game_sessions[str(message.author.id)] = {
                'number': random.randint(1, 100),
                'attempts': 0
            }
            await message.channel.send("게임이 시작되었습니다! 1에서 100 사이의 숫자를 맞춰보세요.")
        else:
            await message.channel.send("이미 게임이 진행 중입니다!")
    
    elif text.isdigit():
        user_id = str(message.author.id)
        if user_id in game_sessions:
            guess = int(text)
            game_data = game_sessions[user_id]
            game_data['attempts'] += 1

            if guess < game_data['number']:
                await message.channel.send("그 숫자보다 큰 숫자를 입력해보세요.")
            elif guess > game_data['number']:
                await message.channel.send("그 숫자보다 작은 숫자를 입력해보세요.")
            else:
                await message.channel.send(f"축하합니다! {game_data['number']}을(를) {game_data['attempts']}번 만에 맞췄습니다!")
                del game_sessions[user_id]
        else:
            await message.channel.send("게임을 시작하려면 '!game'을 입력하세요.")

    elif text.startswith('!timer'):
        try:
            seconds = int(text.split()[1])
            await message.channel.send(f"타이머가 {seconds}초 후에 종료됩니다!")

            await timer_alert(message.channel, seconds)
        except (IndexError, ValueError):
            await message.channel.send("올바른 형식으로 시간을 입력해주세요: !timer [초]")

    # Store recent messages of users
    user_id = str(message.author.id)
    recent_messages.setdefault(user_id, []).append(message.content)
    if len(recent_messages[user_id]) > 10:
        recent_messages[user_id] = recent_messages[user_id][-10:]

async def timer_alert(channel, seconds):
    await asyncio.sleep(seconds)
    await channel.send("타이머가 종료되었습니다!")

# Discord Bot Token
DISCORD_BOT_TOKEN = '####################'  # Input Discord Token

# Discord Bot run
client.run(DISCORD_BOT_TOKEN)
