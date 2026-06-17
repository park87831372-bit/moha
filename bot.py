import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import db
import asyncio

# --- 렌더(Render)용 웹서버 라이브러리 추가 ---
from flask import Flask
from threading import Thread

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# --- 렌더(Render)용 가짜 웹서버 설정 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # 렌더가 자동으로 지정해 주는 포트(PORT)를 가져옵니다. 없으면 기본 8080 사용
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------------

@bot.event
async def on_ready():
    print(f'✅ {bot.user}로 로그인했습니다')
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)}개의 슬래시 명령어를 동기화했습니다')
    except Exception as e:
        print(f'❌ 동기화 실패: {e}')

@bot.event
async def on_member_join(member):
    """새 멤버 가입 시 사용자 정보 생성"""
    await db.create_user(member.id, member.name)

async def load_cogs():
    """Cogs 로드"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'✅ {filename} 로드됨')

async def main():
    """봇 시작"""
    # 봇이 로그인하기 직전에 웹서버를 백그라운드에서 실행합니다.
    keep_alive() 
    
    async with bot:
        await db.connect()
        await load_cogs()
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
