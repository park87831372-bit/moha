import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import db
import asyncio

# --- 렌더(Render)용 필수 라이브러리 ---
from flask import Flask
import threading

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# --- 렌더 웹서비스 프리패스용 Flask 설정 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    # 렌더의 헬스체크 신호를 즉시 받아내기 위해 설정을 고정합니다.
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

async def start_bot():
    """디스코드 봇과 DB를 구동하는 비동기 함수"""
    async with bot:
        print("🗄️ 데이터베이스 연결 중...")
        try:
            await db.connect()
        except Exception as e:
            print(f"⚠️ DB 연결 경고: {e}")
            
        await load_cogs()
        print("🚀 디스코드 봇 로그인 시도 중...")
        await bot.start(os.getenv('DISCORD_TOKEN'))

def main():
    # [핵심] 렌더가 배포 확인을 하러 들어오는 즉시 대답할 수 있도록 Flask를 데몬 스레드로 먼저 가동합니다.
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 [1단계] 렌더 통과용 웹서버 백그라운드 가동 완료")

    # [핵심] Flask가 포트를 잡고 대기하는 동안, 메인 비동기 루프를 열어 디스코드 봇을 로그인시킵니다.
    # 두 프로세스가 스레드와 비동기로 완벽히 분리되어 렌더의 타임아웃에 걸리지 않습니다.
    asyncio.run(start_bot())

if __name__ == '__main__':
    main()
