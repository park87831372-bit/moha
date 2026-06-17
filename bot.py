import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import db
import asyncio

# --- 렌더(Render)용 필수 라이브러리 ---
from flask import Flask
import threading
import time

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# --- 렌더 웹서비스 무조건 통과용 Flask 설정 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    # 렌더의 간섭을 막기 위해 서버 가동을 고정합니다.
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# 파이썬이 켜지자마자 "최우선 순위"로 웹서버부터 독립 스레드로 강제 가동합니다.
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
print("🌐 [1단계] 렌더 통과용 웹서버가 최우선 구동되었습니다.")
# 웹서버가 포트를 완전히 선점할 수 있도록 1초간 완벽한 대기 시간을 줍니다.
time.sleep(1) 

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
    print("🗄️ [2단계] 웹서버가 안정화되어 데이터베이스 연결을 시작합니다...")
    try:
        await db.connect()
    except Exception as e:
        print(f"⚠️ DB 연결 경고 (일단 진행): {e}")
        
    await load_cogs()
    print("🚀 [3단계] 디스코드 봇 로그인을 최종 시도합니다...")
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    # 메인 비동기 루프 가동
    asyncio.run(main())
