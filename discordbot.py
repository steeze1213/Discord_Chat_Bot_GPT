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

# Dictionary to store todo lists for each user
todo_list = {}

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
                max_tokens=300,
                temperature=0.7
            )
            bot_response = response.choices[0].text.strip()
        except Exception as e:
            bot_response = f"An error occurred: {str(e)}"
        
        # send Discord message
        await message.channel.send(f"{bot_response}")

    elif text == '!help':
        await message.channel.send("-bot-에게 명령을 하려면 '!bot + 명령'이라고 입력해보세요.")
        await message.channel.send("'!numbergame'을 입력하여 간단한 숫자 게임을 즐겨보세요.")
        await message.channel.send("'!hangman'을 입력하여 행맨 게임을 즐겨보세요.")
        await message.channel.send("'!timer + [초]'를 입력하여 타이머를 사용해보세요.")
        await message.channel.send("'!clean'을 입력하여 -bot-의 메시지를 삭제해보세요.")
        await message.channel.send("'!일정 추가 [일정]'을 입력하여 일정을 추가해보세요.")
        await message.channel.send("'!일정 보기'을 입력하여 일정 목록을 확인해보세요.")
        await message.channel.send("'!일정 삭제 [번호]'를 입력하여 일정을 삭제해보세요.")

    elif text == '!numbergame':
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

    elif text == '!clean':
        # Delete old messages
        await clean_messages(message.channel)

    elif text == '!hangman':
        await play_hangman(message)

    elif text.startswith('!일정 추가'):
        user = message.author.name
        task = text[len('!일정 추가 '):]
        if user not in todo_list:
            todo_list[user] = []
        todo_list[user].append(task)
        await message.channel.send(f"'{task}' 일정이 추가되었습니다.")

    elif text.startswith('!일정 확인'):
        user = message.author.name
        if user in todo_list and todo_list[user]:
            tasks = "\n".join([f"{idx + 1}. {task}" for idx, task in enumerate(todo_list[user])])
            await message.channel.send(f"{user}님의 일정 목록:\n{tasks}")
        else:
            await message.channel.send("일정 목록이 비어있습니다.")

    elif text.startswith('!일정 삭제'):
        try:
            user = message.author.name
            task_index = int(text[len('!일정 삭제 '):]) - 1
            if user in todo_list and 0 <= task_index < len(todo_list[user]):
                removed_task = todo_list[user].pop(task_index)
                await message.channel.send(f"'{removed_task}' 일정이 삭제되었습니다.")
            else:
                await message.channel.send("유효한 일정 번호를 입력해주세요.")
        except (ValueError, IndexError):
            await message.channel.send("유효한 형식으로 입력해주세요: !일정 삭제 [번호]")

async def timer_alert(channel, seconds):
    await asyncio.sleep(seconds)
    await channel.send("타이머가 종료되었습니다!")

async def clean_messages(channel):
    # Delete 10 messages sent
    async for message in channel.history(limit=100):
        if message.author == client.user:
            await message.delete()

# List of words for Hangman game
words = ['apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon',
         'kiwi', 'pineapple', 'lemon', 'peach', 'pear', 'blueberry',
         'cherry', 'plum', 'melon', 'raspberry', 'mango', 'coconut',
         'apricot', 'avocado', 'blackberry', 'cantaloupe', 'fig', 'grapefruit',
         'guava', 'honeydew', 'kumquat', 'lychee', 'nectarine', 'papaya',
         'passionfruit', 'persimmon', 'pomegranate', 'quince', 'tangerine']

# Choose a random word for Hangman
def choose_word():
    return random.choice(words)

# Hide the word for Hangman
def hide_word(word):
    return '_' * len(word)

# Display the word for Hangman
def display_word(word, guessed_letters):
    displayed_word = ''
    for letter in word:
        if letter in guessed_letters:
            displayed_word += letter
        else:
            displayed_word += '_'
    return displayed_word

# Run the Hangman game
async def play_hangman(message):
    word = choose_word()
    hidden_word = hide_word(word)
    guessed_letters = []
    attempts = len(word) + 2
    
    await message.channel.send("Hangman 게임을 시작합니다!\n단어를 맞춰보세요.(과일)")
    await message.channel.send(display_word(hidden_word, guessed_letters))
    
    while '_' in hidden_word and attempts > 0:
        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            guess_msg = await client.wait_for('message', check=check, timeout=60)
            guess = guess_msg.content.lower()
        except asyncio.TimeoutError:
            await message.channel.send("시간이 초과되었습니다. 게임 종료!")
            return

        if len(guess) != 1 or not guess.isalpha():
            await message.channel.send("한 글자만 입력하세요!")
            continue
        
        if guess in guessed_letters:
            await message.channel.send("이미 추측한 글자입니다!")
            continue
        
        guessed_letters.append(guess)
        
        if guess in word:
            await message.channel.send("정답입니다!")
        else:
            attempts -= 1
            await message.channel.send(f"틀렸습니다! 남은 기회: {attempts}번")
        
        hidden_word = display_word(word, guessed_letters)
        await message.channel.send(hidden_word)
    
    if '_' not in hidden_word:
        await message.channel.send(f"축하합니다! 정답은: {word}")
    else:
        await message.channel.send(f"기회를 모두 소진했습니다! 정답은: {word}")

# Discord Bot Token
DISCORD_BOT_TOKEN = '####################'  # Input Discord Token

# Discord Bot run
client.run(DISCORD_BOT_TOKEN)
