from decouple import config
import os

import discord
from discord.ext import commands

import init
from util import Side

TOKEN = config('DISCORD_TOKEN')
ADMINS = ['mzhao#1429']

SUCCESS_EMOJI = '✅'
FAILURE_EMOJI = '❌'

USER_LIMIT = 10
POSITION_LIMIT = 5

####################

engine = None
id_to_product = dict()
discord_id_to_account = dict()
get_name = lambda author: author.name if author.nick == None else author.nick

def print_books():
    print('\nBooks:')
    engine.print_order_books()

def print_accounts():
    print('\nAccounts:')
    for account in engine.accounts:
        account.print_account()
        print()

####################

bot = commands.Bot(command_prefix='$$')


@bot.event
async def on_ready():
    global engine
    global id_to_product
    engine = init.main(POSITION_LIMIT)
    for product in engine.products:
        id_to_product[product.product_id] = product
    for account in engine.accounts:
        discord_id_to_account[account.discord_id] = account
    
    print('Bot Open')
    print_books()
    print_accounts()



@bot.command(name='test')
async def test_command(ctx):
    await ctx.send(get_name(ctx.author))
    await ctx.message.add_reaction(SUCCESS_EMOJI)



@bot.command(name='print')
async def print_command(ctx):
    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to access $$print')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return
    print_books()
    print_accounts()
    await ctx.message.add_reaction(SUCCESS_EMOJI)



@bot.command(name='buy')
async def buy_command(ctx, *args):
    async def usage(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('USAGE: $$buy [event number] [price between 0-100]')
    
    discord_id = ctx.author.id
    if discord_id not in discord_id_to_account:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are not registered in the game')
        return

    if len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
        await usage(ctx)
        return
    try:
        product_id = int(args[0])
        price = int(args[1])
    except ValueError:
        await usage(ctx)
        return
    if product_id not in id_to_product:
        await usage(ctx)
        return
    if price < 0 or price > 100:
        await usage(ctx)
        return
    
    account = discord_id_to_account[discord_id]
    product = id_to_product[product_id]
    result = engine.process_bid(account, product, Side.BUY, price, True)

    if result[0] == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You cannot both buy and sell the same event at the same price')
        return
    if result[0] == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are at the position limit for this event. You can only sell')
        return

    await ctx.message.add_reaction(SUCCESS_EMOJI)

    if result[1] != None:
        message = 'TRADE: %s sold to %s Event %d at $%d' % (result[1].seller_account.name,
            result[1].buyer_account.name, result[1].product.product_id, result[1].price)
        await ctx.send(message)
        print(message)



@bot.command(name='sell')
async def sell_command(ctx, *args):
    async def usage(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('USAGE: $$sell [event number] [price between 0-100]')

    discord_id = ctx.author.id
    if discord_id not in discord_id_to_account:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are not registered in the game')
        return

    if len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
        await usage(ctx)
        return
    try:
        product_id = int(args[0])
        price = int(args[1])
    except ValueError:
        await usage(ctx)
        return
    if product_id not in id_to_product:
        await usage(ctx)
        return
    if price < 0 or price > 100:
        await usage(ctx)
        return
    
    account = discord_id_to_account[discord_id]
    product = id_to_product[product_id]
    result = engine.process_bid(account, product, Side.SELL, price, True)

    if result[0] == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You cannot both buy and sell the same event at the same price')
        return
    if result[0] == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are at the position limit for this event. You can only buy')
        return

    await ctx.message.add_reaction(SUCCESS_EMOJI)

    if result[1] != None:
        message = 'TRADE: %s sold to %s Event %d at $%d' % (result[1].seller_account.name,
            result[1].buyer_account.name, result[1].product.product_id, result[1].price)
        await ctx.send(message)
        print(message)



@bot.command(name='cancel')
async def cancel_command(ctx, *args):
    async def usage(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('USAGE: $$cancel [buy/sell] [event number]')
    
    discord_id = ctx.author.id
    if discord_id not in discord_id_to_account:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are not registered in the game')
        return

    if len(args) < 2 or not args[1].isdigit() or args[0].lower() not in ['buy', 'sell', 'b', 's']:
        await usage(ctx)
        return
    side = Side.BUY if args[0].lower() in ['buy', 'b'] else Side.SELL
    try:
        product_id = int(args[1])
    except ValueError:
        await usage(ctx)
        return
    if product_id not in id_to_product:
        await usage(ctx)
        return
    
    account = discord_id_to_account[discord_id]
    product = id_to_product[product_id]
    result = engine.process_cancel(account, product, side, True)

    if result == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You do not have such an order to cancel')
        return
    
    await ctx.message.add_reaction(SUCCESS_EMOJI)



@bot.command(name='adduser')
async def adduser_command(ctx, *args):
    if len(discord_id_to_account) >= USER_LIMIT:
        print('too many users already in the game')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return
    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to access $$adduser')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return
    id = args[0]
    while not id[0].isdigit():
        id = id[1:]
    id = int(id[:-1])
    if id in discord_id_to_account:
        print(args[0], 'is already in the game')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return
    
    user = ctx.guild.get_member(id)
    init.add_account(engine.sheet_writer, id, get_name(user))
    discord_id_to_account[id] = engine.accounts[-1]
    await ctx.message.add_reaction(SUCCESS_EMOJI)

    print('ADDED USER')
    print_accounts()



@bot.command(name='mark')
async def mark(ctx, *args):
    async def failure(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)

    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to access $$occurred')
        await failure(ctx)
        return
    if len(args) < 2 or args[1] not in ['y', 'n']:
        await failure(ctx)
        return
    try:
        product_id = int(args[0])
    except ValueError:
        await failure(ctx)
        return
    
    did_occur = args[1] == 'y'
    engine.mark_occurred(id_to_product[product_id], did_occur)
    await ctx.message.add_reaction(SUCCESS_EMOJI)
    print('marked ' + str(product_id) + (' occurred' if did_occur else ' did not occur'))
    print_accounts()



@bot.command(aliases=["quit"])
@commands.has_permissions(administrator=True)
async def close(ctx):
    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to quit')
        return
    await ctx.message.add_reaction(SUCCESS_EMOJI)
    await bot.close()
    print("Bot Closed")



bot.run(TOKEN)