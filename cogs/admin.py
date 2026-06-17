import discord
from discord.ext import commands
from database import db
import os
from dotenv import load_dotenv

load_dotenv()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_id = int(os.getenv('ADMIN_ID', 0))

    def is_admin(self, user_id):
        """관리자 확인"""
        return user_id == self.admin_id

    @discord.app_commands.command(name="경험치_설정", description="[관리자] 사용자의 경험치를 설정합니다")
    async def set_xp(self, interaction: discord.Interaction, user: discord.User, xp: int):
        """사용자 경험치 설정"""
        if not self.is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 권한 없음",
                description="이 명령어는 관리자만 사용할 수 있습니다",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        target_user = await db.get_user(user.id)
        if not target_user:
            await db.create_user(user.id, user.name)

        await db.set_xp(user.id, xp)
        updated_user = await db.get_user(user.id)

        embed = discord.Embed(
            title="✅ 경험치 설정 완료",
            description=f"{user.mention}의 경험치를 설정했습니다",
            color=discord.Color.green()
        )
        embed.add_field(name="설정된 경험치", value=f"{xp} XP", inline=True)
        embed.add_field(name="현재 레벨", value=f"Level {updated_user['level']}", inline=True)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="경험치_추가", description="[관리자] 사용자에게 경험치를 추가합니다")
    async def add_xp_admin(self, interaction: discord.Interaction, user: discord.User, xp: int):
        """사용자 경험치 추가"""
        if not self.is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 권한 없음",
                description="이 명령어는 관리자만 사용할 수 있습니다",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        target_user = await db.get_user(user.id)
        if not target_user:
            await db.create_user(user.id, user.name)

        result = await db.add_xp(user.id, xp)

        embed = discord.Embed(
            title="✅ 경험치 추가 완료",
            description=f"{user.mention}에게 경험치를 추가했습니다",
            color=discord.Color.green()
        )
        embed.add_field(name="추가된 경험치", value=f"+{xp} XP", inline=True)
        embed.add_field(name="현재 경험치", value=f"{result['xp']} XP", inline=True)
        embed.add_field(name="현재 레벨", value=f"Level {result['level']}", inline=True)

        if result['old_level'] < result['level']:
            embed.add_field(name="🎉 레벨업!", value=f"Level {result['old_level']} → Level {result['level']}", inline=False)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="경험치_선물", description="[관리자] 사용자에게 경험치를 선물합니다")
    async def gift_xp(self, interaction: discord.Interaction, user: discord.User, xp: int):
        """사용자에게 경험치 선물"""
        if not self.is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 권한 없음",
                description="이 명령어는 관리자만 사용할 수 있습니다",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        target_user = await db.get_user(user.id)
        if not target_user:
            await db.create_user(user.id, user.name)

        result = await db.add_xp(user.id, xp)

        # 선물받은 사용자에게 DM 전송
        try:
            dm_embed = discord.Embed(
                title="🎁 경험치 선물을 받았습니다!",
                description=f"관리자로부터 {xp} XP를 받았습니다!",
                color=discord.Color.green()
            )
            dm_embed.add_field(name="현재 경험치", value=f"{result['xp']} XP", inline=True)
            dm_embed.add_field(name="현재 레벨", value=f"Level {result['level']}", inline=True)
            await user.send(embed=dm_embed)
        except:
            pass

        embed = discord.Embed(
            title="✅ 경험치 선물 완료",
            description=f"{user.mention}에게 경험치를 선물했습니다",
            color=discord.Color.green()
        )
        embed.add_field(name="선물한 경험치", value=f"+{xp} XP", inline=True)
        embed.add_field(name="현재 경험치", value=f"{result['xp']} XP", inline=True)
        embed.add_field(name="현재 레벨", value=f"Level {result['level']}", inline=True)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="확률_설정", description="[관리자] 게임 확률을 설정합니다")
    async def set_probability(self, interaction: discord.Interaction, game_type: str, probability: float):
        """게임 확률 설정"""
        if not self.is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 권한 없음",
                description="이 명령어는 관리자만 사용할 수 있습니다",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if probability < 0 or probability > 1:
            embed = discord.Embed(
                title="❌ 유효하지 않은 값",
                description="확률은 0 이상 1 이하여야 합니다 (예: 0.5 = 50%)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        game_type = game_type.lower()
        if game_type not in ['russian_roulette', 'lottery']:
            embed = discord.Embed(
                title="❌ 유효하지 않은 게임 타입",
                description="russian_roulette 또는 lottery 중 하나를 선택하세요",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        config_key = f"{game_type}_win_rate"
        await db.update_game_config(**{config_key: probability})

        embed = discord.Embed(
            title="✅ 확률 설정 완료",
            color=discord.Color.green()
        )
        
        game_name = "러시안룰렛" if game_type == "russian_roulette" else "복권"
        embed.add_field(name="게임", value=game_name, inline=True)
        embed.add_field(name="당첨 확률", value=f"{probability * 100}%", inline=True)

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="배수_설정", description="[관리자] 복권 당첨 배수를 설정합니다")
    async def set_multiplier(self, interaction: discord.Interaction, multiplier: float):
        """복권 배수 설정"""
        if not self.is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 권한 없음",
                description="이 명령어는 관리자만 사용할 수 있습니다",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if multiplier <= 0:
            embed = discord.Embed(
                title="❌ 유효하지 않은 값",
                description="배수는 0보다 커야 합니다 (예: 2.5 = 2.5배)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        await db.update_game_config(lottery_multiplier=multiplier)

        embed = discord.Embed(
            title="✅ 배수 설정 완료",
            description=f"복권 당첨 배수를 {multiplier}배로 설정했습니다",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="게임_설정_확인", description="[관리자] 현재 게임 설정을 확인합니다")
    async def check_config(self, interaction: discord.Interaction):
        """게임 설정 확인"""
        if not self.is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 권한 없음",
                description="이 명령어는 관리자만 사용할 수 있습니다",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        config = await db.get_game_config()

        embed = discord.Embed(
            title="⚙️ 게임 설정",
            color=discord.Color.blue()
        )
        embed.add_field(name="러시안룰렛 승률", value=f"{config['russian_roulette_win_rate'] * 100}%", inline=True)
        embed.add_field(name="복권 당첨확률", value=f"{config['lottery_win_rate'] * 100}%", inline=True)
        embed.add_field(name="복권 배수", value=f"{config['lottery_multiplier']}배", inline=True)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
