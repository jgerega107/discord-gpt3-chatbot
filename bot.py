import openai
import discord
import time
import threading
import os

client = discord.Client()

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")

global timeleft
global currtemp
currtemp = 0.9

def brainwash():
    aiprompt = open("prompt.txt", "w")
    bprompt = open("baseprompt.txt", "r")
    aiprompt.write(bprompt.read())
    aiprompt.close()
    bprompt.close()
    print("----Prompt reset.----")

def timer():
    global timeleft
    timeleft = 60
    while timeleft != 0:
        time.sleep(1)
        timeleft-=1
    brainwash()
    print("----Timer finished, prompt reset.----")

async def generate():
    global currtemp
    aiprompt = open("prompt.txt", "r+")
    response = openai.Completion.create(
        engine="davinci",
        prompt=aiprompt.read(),
    temperature=currtemp,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=["\n", "AI:"])
    gptmsg = response.choices[0]
    aiprompt.write(gptmsg.text)
    aiprompt.close()
    return gptmsg.text

timerthread = threading.Thread(target=timer)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global timeleft
    global timerthread
    global currtemp
    if message.author == client.user:
        return

    if message.channel.id == CID:
        if message.content == "$RESET":
            brainwash()
            await message.add_reaction("✅")
            return
        if "$TEMP" in message.content:
            if float(message.content[5::]) > 1 or float(message.content[5::]) < 0:
                await message.reply("Temperature must be between 0.0 and 1.0")
            else:
                currtemp = float(message.content[5::])
                print("New temperature: " + str(currtemp))
                await message.add_reaction("✅")
            return
        elif message.content == "$SHUTDOWN" and message.author.id == ADMINID:
            await message.add_reaction("✅")
            quit()
        if not timerthread.is_alive():
            timerthread = threading.Thread(target=timer)
            timerthread.start()
        else:
            timeleft = 60
        aiprompt = open("prompt.txt", "a")
        res = "\n" + message.author.nick + ": " + message.content + "\nAI:"
        print(message.author.nick + ": " + message.content)
        aiprompt.write(res)
        aiprompt.close()
        response = await generate()
        print("AI:" + response)
        await message.channel.send(response)

client.run(os.getenv("DISCORD_API_KEY"))