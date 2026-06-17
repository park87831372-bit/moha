import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import db
import asyncio

# --- 렌더(Render)용 웹서버 라이브러리 추가 ---
from flask import Flask
import threading

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

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    # 외부에서 접속 가능하도록 대기하며 충돌을 방지합니다.
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

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
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ {filename} 로드됨')

async def main():
    """봇 시작"""
    # 데이터베이스 연결 및 Cogs 로드를 봇 로그인 전에 완벽히 끝냅니다.
    await db.connect()
    await load_cogs()
    
    # 디스코드 봇 로그인 시작
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    # 1. 파이썬이 실행되자마자 Flask 웹 서버를 별도의 독립된 실(Thread)에서 먼저 가동합니다.
    # 이렇게 하면 렌더가 접속을 시도할 때 즉시 "Bot is alive!"를 응답해 줍니다.
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 2. 웹 서버와 상관없이 메인 흐름은 디스코드 봇을 작동시키는 데 전념합니다.
    asyncio.run(main())
