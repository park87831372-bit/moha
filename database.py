import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """데이터베이스 연결"""
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            async with self.pool.acquire() as conn:
                # 테이블 생성
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username VARCHAR(255),
                        xp BIGINT DEFAULT 0,
                        level INT DEFAULT 1,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS game_stats (
                        user_id BIGINT PRIMARY KEY,
                        russian_roulette_wins INT DEFAULT 0,
                        russian_roulette_losses INT DEFAULT 0,
                        lottery_wins INT DEFAULT 0,
                        lottery_plays INT DEFAULT 0,
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS game_config (
                        config_id INT PRIMARY KEY,
                        russian_roulette_win_rate FLOAT DEFAULT 0.5,
                        lottery_win_rate FLOAT DEFAULT 0.3,
                        lottery_multiplier FLOAT DEFAULT 2.5
                    )
                ''')
                
                # 기본 설정 삽입
                try:
                    await conn.execute('''
                        INSERT INTO game_config (config_id, russian_roulette_win_rate, lottery_win_rate, lottery_multiplier)
                        VALUES (1, 0.5, 0.3, 2.5)
                    ''')
                except:
                    pass  # 이미 존재하면 스킵
            
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")

    async def get_user(self, user_id):
        """사용자 정보 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)

    async def create_user(self, user_id, username):
        """새 사용자 생성"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username, xp, level)
                VALUES ($1, $2, 0, 1)
                ON CONFLICT (user_id) DO NOTHING
            ''', user_id, username)
            
            await conn.execute('''
                INSERT INTO game_stats (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO NOTHING
            ''', user_id)

    async def add_xp(self, user_id, amount):
        """경험치 추가"""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow('SELECT xp, level FROM users WHERE user_id = $1', user_id)
            if not user:
                return None
            
            new_xp = user['xp'] + amount
            new_level = 1 + (new_xp // 1000)  # 1000 XP마다 1레벨
            
            await conn.execute('''
                UPDATE users SET xp = $1, level = $2 WHERE user_id = $3
            ''', new_xp, new_level, user_id)
            
            return {'xp': new_xp, 'level': new_level, 'old_level': user['level']}

    async def remove_xp(self, user_id, amount):
        """경험치 제거"""
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow('SELECT xp, level FROM users WHERE user_id = $1', user_id)
            if not user:
                return None
            
            new_xp = max(0, user['xp'] - amount)
            new_level = 1 + (new_xp // 1000)
            
            await conn.execute('''
                UPDATE users SET xp = $1, level = $2 WHERE user_id = $3
            ''', new_xp, new_level, user_id)
            
            return {'xp': new_xp, 'level': new_level}

    async def set_xp(self, user_id, amount):
        """경험치 설정 (관리자용)"""
        async with self.pool.acquire() as conn:
            new_level = 1 + (amount // 1000)
            await conn.execute('''
                UPDATE users SET xp = $1, level = $2 WHERE user_id = $3
            ''', amount, new_level, user_id)

    async def get_leaderboard(self, limit=10):
        """리더보드 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT user_id, username, xp, level FROM users 
                ORDER BY xp DESC LIMIT $1
            ''', limit)

    async def update_game_stats(self, user_id, game_type, result):
        """게임 통계 업데이트"""
        async with self.pool.acquire() as conn:
            if game_type == 'russian_roulette':
                if result == 'win':
                    await conn.execute('''
                        UPDATE game_stats SET russian_roulette_wins = russian_roulette_wins + 1
                        WHERE user_id = $1
                    ''', user_id)
                else:
                    await conn.execute('''
                        UPDATE game_stats SET russian_roulette_losses = russian_roulette_losses + 1
                        WHERE user_id = $1
                    ''', user_id)
            
            elif game_type == 'lottery':
                if result == 'win':
                    await conn.execute('''
                        UPDATE game_stats SET lottery_wins = lottery_wins + 1, lottery_plays = lottery_plays + 1
                        WHERE user_id = $1
                    ''', user_id)
                else:
                    await conn.execute('''
                        UPDATE game_stats SET lottery_plays = lottery_plays + 1
                        WHERE user_id = $1
                    ''', user_id)

    async def get_game_stats(self, user_id):
        """게임 통계 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM game_stats WHERE user_id = $1', user_id)

    async def get_game_config(self):
        """게임 설정 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM game_config WHERE config_id = 1')

    async def update_game_config(self, **kwargs):
        """게임 설정 업데이트 (관리자용)"""
        async with self.pool.acquire() as conn:
            update_fields = []
            values = []
            for idx, (key, value) in enumerate(kwargs.items(), 1):
                update_fields.append(f"{key} = ${idx}")
                values.append(value)
            
            if update_fields:
                values.append(1)
                query = f"UPDATE game_config SET {', '.join(update_fields)} WHERE config_id = ${len(values)}"
                await conn.execute(query, *values)

    async def close(self):
        """데이터베이스 연결 종료"""
        if self.pool:
            await self.pool.close()

db = Database()
