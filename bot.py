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
    # Werkzeug 웹서버의 자체 스레드로 인한 중복 실행 및 충돌 방지 설정을 추가했습니다.
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def keep_alive():
    # daemon=True를 넣어 메인 프로그램(디스코드 봇)이 켜질 때 웹서버가 방해하지 않고 독립된 백그라운드에서 돌게 합니다.
    t = Thread(target=run, daemon=True)
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
    # 1. 렌더가 웹서비스 점검(Health Check)을 들어올 때 바로 응답할 수 있도록 백그라운드 서버를 가장 먼저 깨웁니다.
    keep_alive() 
    
    # 2. 비동기 루프 안에서 안전하게 데이터베이스와 디스코드 봇을 연결합니다.
    async with bot:
        await db.connect()
        await load_cogs()
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
