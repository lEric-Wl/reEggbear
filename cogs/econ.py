import discord
from discord.ext import commands

import random
import time

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.bot.file_manager.check_member(str(member.id))
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        member = str(message.author.id)

        self.bot.file_manager.check_member(member)
        self.bot.file_manager.saves['members'][member][0] += random.randint(5, 20) 
        self.bot.file_manager.save_saves()

    def getBalance(self, memberId):
        self.bot.file_manager.check_member(memberId)
        balance = self.bot.file_manager.saves['members'][memberId]

        return balance

    @commands.slash_command()
    async def check_balance(self, ctx, user: discord.User = None):  
        if user is None:
            user = ctx.author      
        member = user.id
        
        balance = self.getBalance(str(member))

        embed = discord.Embed(
            title=f'Currency Balances for {user.display_name}',
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name=f'**Holding:** {balance[0]} Hello Fresh Coupons \n**Bank:** {balance[1]} Hello Fresh Coupons',value='')
        embed.set_footer(text='Hello Fresh Coupons in the Bank earn interest!')


        await ctx.respond(embed=embed)

    @discord.slash_command()
    async def bank_deposit(self,ctx,amount:int):
        member = str(ctx.author.id)

        if amount > self.getBalance(member)[0]:
            await ctx.respond("You don't have that much, dingus")
            return

        balance = self.getBalance(member)
        balance[1] += amount
        balance[0] -= amount

        embed  = discord.Embed(
            title=f"You've successfully deposited {amount} Hello Fresh Coupons into your bank!"
        )

        self.bot.file_manager.save_saves()
        await ctx.respond(embed = embed)
        
    @discord.slash_command()
    async def bank_withdraw(self,ctx,amount:int):
        member = str(ctx.author.id)

        if amount > self.getBalance(member)[1]:
            await ctx.respond("You don't have that much in the bank, dingus")
            return 
        
        balance = self.getBalance(member)
        balance[0] += amount
        balance[1] -= amount

        embed  = discord.Embed(
            title=f"You've successfully withdrawn {amount} Hello Fresh Coupons from your bank!"
        )

        self.bot.file_manager.save_saves()
        await ctx.respond(embed = embed)

    @discord.slash_command()
    async def rob(self,ctx,user: discord.User):
        if user.bot:
            balance = self.getBalance(str(ctx.author.id))
            balance[0] -= 500
            await ctx.respond(f"{ctx.author.mention}, you can't rob a bot! Egg Bear fines you 500 coupons. Be better.")
            self.bot.file_manager.save_saves()
            return

        target = str(user.id)
        author = str(ctx.author.id)

        if target == author:
            await ctx.respond("You can't rob yourself, dingus!")
            return 
        
        target_balance = self.getBalance(target)
        author_balance = self.getBalance(author)
        
        if target_balance[0] < 200:
            fine = int((random.randint(1, 5)/100) * target_balance[0])
            print(fine)
            author_balance[0] -= fine
            await ctx.respond(f"{ctx.author.mention} tried to rob a poor person. That's just rude. Egg Bear fines you {fine} coupons.")
            self.bot.file_manager.save_saves()
            return

        rng = random.randint(0, 100)
        print(rng)
        if rng < 30: #Rob failed
            await ctx.respond(f'{ctx.author.mention} tried to rob {user.mention}, but failed.')
        elif rng < 50: #got caught
            fine = int((random.randint(1, 5)/100) * target_balance[0])
            author_balance[0] -= fine
            target_balance[0] += fine
            await ctx.respond(f"{ctx.author.mention} tried to rob {user.mention} but got caught in the act! Egg Bear gines you {fine} coupons for you thievery, with the coupons being granted to your victim.")
        elif rng < 95: #Success, tazzar!
            amount = int((random.randint(10, 20)/100) * target_balance[0])
            author_balance[0] += amount
            target_balance[0] -= amount
            await ctx.respond(f'{ctx.author.mention} succeeded in stealing {amount} from {user.mention}')
        else: #mega success, tazzaarr!!
            amount = int((random.randint(20, 50)/100) * target_balance[0])
            author_balance[0] += amount
            target_balance[0] -= amount
            await ctx.respond(f'{ctx.author.mention} succeeded in stealing {amount} from {user.mention}')
        
        self.save_saves()

    @discord.slash_command()
    async def daily(self,ctx):
        member = str(ctx.author.id)

        timestamp = int(time.time())
        
        self.bot.file_manager.check_member(member)
        saves = self.bot.file_manager.saves['timer']['daily']

        if member not in saves or saves[member] <= timestamp:
            self.getBalance(member)[0] += 500
            embed = discord.Embed(            
                description="You've claimed you daily bonus!\nRecieved 500 Hello Fresh Coupons"
            )

            self.bot.file_manager.saves['timer']['daily'][member] = timestamp + 86400
        else:
            embed = discord.Embed(
                title="You are on cooldown!",
                description=f"Please try again in <t:{saves[member]}:R>"
            )
            
            embed.set_footer(text=f'Daily Bonus - {ctx.author.display_name}')

        self.bot.file_manager.save_saves()
        await ctx.respond(embed=embed)


async def setup(bot):
    bot.add_cog(Economy(bot))
    