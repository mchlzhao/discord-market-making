from decouple import config
import os

import discord
from discord.ext import commands

from controller import Controller
from util import Side

import settings

TOKEN = config('DISCORD_TOKEN')
ADMINS = ['mzhao#1429']

SUCCESS_EMOJI = '✅'
FAILURE_EMOJI = '❌'

USER_LIMIT = 10
POSITION_LIMIT = 5

####################

controller = None

get_name = lambda author: author.name if author.nick == None else author.nick

def print_books():
    print('\nBooks:')
    controller.engine.print_order_books()

def print_accounts():
    print('\nAccounts:')
    for account in controller.accounts:
        account.print_account()
        print()

####################

bot = commands.Bot(command_prefix='$$')



@bot.event
async def on_ready():
    global controller
    controller = Controller('F1 Market', settings.PRODUCTS)
    controller.init_from_sheet()
    print_books()
    print_accounts()
    print('Bot Open')



@bot.command(name='test')
async def test_command(ctx):
    await ctx.message.add_reaction(SUCCESS_EMOJI)
    await ctx.send(get_name(ctx.author))



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
    if not controller.has_user(discord_id):
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

    result = controller.process_bid(discord_id, product_id, Side.BUY, price, True)

    if result[0] == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You cannot both buy and sell the same event at the same price')
        return
    if result[0] == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are at the position limit for this event. You can only sell')
        return
    if result[0] == -3:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Price must be between 0 and 100 inclusive')
        return
    if result[0] == -4:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Product does not exist')
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
    if not controller.has_user(discord_id):
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
    
    result = controller.process_bid(discord_id, product_id, Side.SELL, price, True)

    if result[0] == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You cannot both buy and sell the same event at the same price')
        return
    if result[0] == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are at the position limit for this event. You can only buy')
        return
    if result[0] == -3:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Price must be between 0 and 100 inclusive')
        return
    if result[0] == -4:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Product does not exist')
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
    if not controller.has_user(discord_id):
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
    
    result = controller.process_cancel(discord_id, product_id, side, True)

    if result == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You do not have such an order to cancel')
        return
    if result == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Product does not exist')
        return
    
    await ctx.message.add_reaction(SUCCESS_EMOJI)



@bot.command(name='adduser')
async def adduser_command(ctx, *args):
    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to access $$adduser')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return

    id = args[0]
    while not id[0].isdigit():
        id = id[1:]
    id = int(id[:-1])

    if controller.has_user(id):
        print(args[0], 'is already in the game')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return

    user = ctx.guild.get_member(id)
    result = controller.add_account(id, get_name(user))

    if result == -1:
        print('too many users already in the game')
        await ctx.message.add_reaction(FAILURE_EMOJI)
        return
    
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
    result = controller.mark_occurred(product_id, did_occur, True)

    if result == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Product does not exist')
        return

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