import discord
from discord.ext import commands, tasks
from database import db

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_tracking = {}  # user_id: start_time
        self.voice_xp_loop.start()

    @tasks.loop(minutes=5)
    async def voice_xp_loop(self):
        """5분마다 음성채널 사용자에게 100 XP 지급"""
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice and member.voice.channel:
                    if not member.bot:
                        await db.add_xp(member.id, 100)

    @voice_xp_loop.before_loop
    async def before_voice_xp_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        """메시지 발송 시 20 XP 지급"""
        if message.author.bot:
            return
        
        # 명령어가 아닌 일반 메시지만 처리
        if message.content.startswith('/'):
            return

        user = await db.get_user(message.author.id)
        if not user:
            await db.create_user(message.author.id, message.author.name)
        
        await db.add_xp(message.author.id, 20)

    @discord.app_commands.command(name="프로필", description="당신의 프로필을 확인합니다")
    async def profile(self, interaction: discord.Interaction):
        """사용자 프로필 표시"""
        await interaction.response.defer()

        user = await db.get_user(interaction.user.id)
        if not user:
            await db.create_user(interaction.user.id, interaction.user.name)
            user = await db.get_user(interaction.user.id)

        stats = await db.get_game_stats(interaction.user.id)

        embed = discord.Embed(
            title=f"📊 {interaction.user.name}의 프로필",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.add_field(name="레벨", value=f"Level {user['level']}", inline=True)
        embed.add_field(name="경험치", value=f"{user['xp']} XP", inline=True)
        
        # 다음 레벨까지 필요 경험치
        next_level_xp = (user['level']) * 1000
        remaining_xp = next_level_xp - user['xp']
        embed.add_field(name="다음 레벨까지", value=f"{remaining_xp} XP 필요", inline=False)

        if stats:
            embed.add_field(name="🎯 러시안룰렛", value=f"승: {stats['russian_roulette_wins']} / 패: {stats['russian_roulette_losses']}", inline=True)
            embed.add_field(name="🎰 복권", value=f"당: {stats['lottery_wins']} / 총 플레이: {stats['lottery_plays']}", inline=True)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="리더보드", description="상위 10명의 경험치 랭킹을 봅니다")
    async def leaderboard(self, interaction: discord.Interaction):
        """리더보드 표시"""
        await interaction.response.defer()

        users = await db.get_leaderboard(10)

        if not users:
            embed = discord.Embed(
                title="📊 리더보드",
                description="데이터가 없습니다",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="📊 XP 리더보드 - Top 10",
            color=discord.Color.gold()
        )

        leaderboard_text = ""
        for idx, user in enumerate(users, 1):
            leaderboard_text += f"{idx}. **{user['username']}** - Level {user['level']} ({user['xp']} XP)\n"

        embed.description = leaderboard_text
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(XP(bot))
