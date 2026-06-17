import discord
from discord.ext import commands
from database import db
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="러시안룰렛", description="경험치를 걸고 러시안룰렛을 플레이합니다")
    async def russian_roulette(self, interaction: discord.Interaction, bet: int):
        """러시안룰렛 게임"""
        await interaction.response.defer()

        user = await db.get_user(interaction.user.id)
        if not user:
            await db.create_user(interaction.user.id, interaction.user.name)
            user = await db.get_user(interaction.user.id)

        if user['xp'] < bet:
            embed = discord.Embed(
                title="❌ 경험치 부족",
                description=f"보유 경험치: {user['xp']} XP\n필요 경험치: {bet} XP",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        if bet <= 0:
            embed = discord.Embed(
                title="❌ 유효하지 않은 베팅",
                description="0 이상의 경험치를 베팅해주세요",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        config = await db.get_game_config()
        win_rate = config['russian_roulette_win_rate']

        # 게임 진행
        result = random.random() < win_rate
        
        if result:
            # 승리
            reward = int(bet * 1.5)
            await db.add_xp(interaction.user.id, reward)
            await db.update_game_stats(interaction.user.id, 'russian_roulette', 'win')
            
            embed = discord.Embed(
                title="🎉 승리!",
                description=f"+{reward} XP 획득!",
                color=discord.Color.green()
            )
        else:
            # 패배
            await db.remove_xp(interaction.user.id, bet)
            await db.update_game_stats(interaction.user.id, 'russian_roulette', 'loss')
            
            embed = discord.Embed(
                title="💀 패배!",
                description=f"-{bet} XP 손실",
                color=discord.Color.red()
            )

        user_after = await db.get_user(interaction.user.id)
        embed.add_field(name="현재 경험치", value=f"{user_after['xp']} XP", inline=False)
        embed.add_field(name="현재 레벨", value=f"Level {user_after['level']}", inline=False)
        
        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="복권", description="경험치를 걸고 복권을 플레이합니다")
    async def lottery(self, interaction: discord.Interaction, bet: int):
        """복권 게임"""
        await interaction.response.defer()

        user = await db.get_user(interaction.user.id)
        if not user:
            await db.create_user(interaction.user.id, interaction.user.name)
            user = await db.get_user(interaction.user.id)

        if user['xp'] < bet:
            embed = discord.Embed(
                title="❌ 경험치 부족",
                description=f"보유 경험치: {user['xp']} XP\n필요 경험치: {bet} XP",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        if bet <= 0:
            embed = discord.Embed(
                title="❌ 유효하지 않은 베팅",
                description="0 이상의 경험치를 베팅해주세요",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        config = await db.get_game_config()
        win_rate = config['lottery_win_rate']
        multiplier = config['lottery_multiplier']

        # 게임 진행
        result = random.random() < win_rate

        if result:
            # 당첨
            reward = int(bet * multiplier)
            await db.add_xp(interaction.user.id, reward)
            await db.update_game_stats(interaction.user.id, 'lottery', 'win')
            
            embed = discord.Embed(
                title="🎰 당첨!",
                description=f"+{reward} XP 획득! (x{multiplier})",
                color=discord.Color.gold()
            )
        else:
            # 낙첨
            await db.remove_xp(interaction.user.id, bet)
            await db.update_game_stats(interaction.user.id, 'lottery', 'loss')
            
            embed = discord.Embed(
                title="🎰 낙첨",
                description=f"-{bet} XP 손실",
                color=discord.Color.red()
            )

        user_after = await db.get_user(interaction.user.id)
        embed.add_field(name="현재 경험치", value=f"{user_after['xp']} XP", inline=False)
        embed.add_field(name="현재 레벨", value=f"Level {user_after['level']}", inline=False)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))
