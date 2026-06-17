import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import db
import asyncio

# --- 렌더(Render)용 웹서버 라이브러리 ---
from flask import Flask
import threading

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# --- 렌더 웹서비스 헬스체크용 Flask 설정 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # 렌더 웹서비스는 이 포트(기본 8080)로 신호가 들어왔을 때 대답을 해줘야 정상 작동합니다.
    port = int(os.environ.get("PORT", 8080))
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
    # 1. 렌더가 배포 직후 헬스체크를 보낼 때 즉각 대답할 수 있도록 Flask 스레드를 안전하게 먼저 구동합니다.
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 렌더 헬스체크용 백그라운드 웹서버 가동 완료")

    # 2. 웹서버가 안정적으로 자리를 잡은 직후 디스코드 봇과 데이터베이스를 가동합니다.
    async with bot:
        print("🗄️ 데이터베이스 연결 시도 중...")
        await db.connect()
        await load_cogs()
        print("🚀 디스코드 봇 로그인을 시도합니다...")
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    # 메인 비동기 루프 실행
    asyncio.run(main())
