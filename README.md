# 🎮 Moha Discord Bot

경험치 시스템과 게임을 제공하는 디스코드 봇입니다.

## ✨ 기능

### 📊 경험치 시스템
- **음성채널**: 5분마다 100 XP 자동 지급
- **채팅**: 메시지 발송 시 20 XP 지급
- **레벨 시스템**: 경험치로 레벨 업

### 🎮 게임
- **러시안룰렛** (`/러시안룰렛`): 경험치를 걸고 도박 (1.5배 보상)
- **복권** (`/복권`): 경험치를 걸고 복권 플레이

### 👤 프로필 & 랭킹
- **프로필** (`/프로필`): 개인 프로필 조회
- **리더보드** (`/리더보드`): 상위 10명 랭킹

### ⚙️ 관리자 명령어
- `/경험치_설정 @사용자 숫자`: 경험치 설정
- `/경험치_추가 @사용자 숫자`: 경험치 추가
- `/경험치_선물 @사용자 숫자`: 경험치 선물
- `/확률_설정 game_type 숫자`: 게임 확률 설정 (0~1)
- `/배수_설정 숫자`: 복권 배수 설정
- `/게임_설정_확인`: 현재 설정 확인

## 🛠️ 설치

### 필수 요구사항
- Python 3.8+
- PostgreSQL
- Discord Bot Token

### 설정

1. `.env` 파일 생성:
```
DISCORD_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://username:password@localhost:5432/moha
ADMIN_ID=관리자_디스코드_ID
```

2. 필수 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 데이터베이스 초기화:
```bash
python database.py
```

4. 봇 실행:
```bash
python bot.py
```

## 📦 배포 (Render)

`Procfile`을 통해 Render에 자동 배포 가능합니다.

## 📄 라이센스

MIT License

## 👨‍💻 개발자

박도영 (@park87831372-bit)
