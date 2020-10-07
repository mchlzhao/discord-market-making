from decouple import config
import os

import discord
from discord.ext import commands

from controller import Controller

TOKEN = config('DISCORD_TOKEN')
ADMINS = ['mzhao#1429']

SUCCESS_EMOJI = '✅'
FAILURE_EMOJI = '❌'

####################

controller = None

get_name = lambda author: author.name if author.nick == None else author.nick

####################

bot = commands.Bot(command_prefix='$$')



@bot.event
async def on_ready():
    global controller
    controller = Controller()
    print('Bot Open')



@bot.command(name='test')
async def test_command(ctx):
    await ctx.message.add_reaction(SUCCESS_EMOJI)
    id = str(ctx.author.id)
    await ctx.send('<@%s>' % id)



async def announce_trade(ctx, transaction_dict):
    if transaction_dict is None:
        return
    
    message2 = ' Event {display_order} at ${price}'.format(
        display_order = transaction_dict['display_order'],
        price = transaction_dict['price']
    )
    if transaction_dict['is_buyer_maker']:
        message1 = 'TRADE: <@{seller_id}> sold to <@{buyer_id}>'.format(
            buyer_id = transaction_dict['buyer_id'],
            seller_id = transaction_dict['seller_id']
        )
    else:
        message1 = 'TRADE: <@{buyer_id}> bought from <@{seller_id}>'.format(
            buyer_id = transaction_dict['buyer_id'],
            seller_id = transaction_dict['seller_id']
        )

    await ctx.send(message1 + message2)



@bot.command(name='buy')
async def buy_command(ctx, *args):
    async def usage(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('USAGE: $$buy [event number] [price between 0-100]')
    
    discord_id = str(ctx.author.id)

    if len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
        await usage(ctx)
        return
    try:
        display_order = int(args[0])
        price = int(args[1])
    except ValueError:
        await usage(ctx)
        return
    if price < 0 or price > 100:
        await usage(ctx)
        return

    result = controller.buy(discord_id, display_order, price)

    if result[0] == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are not registered in the game')
        return
    if result[0] == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Event does not exist')
        return
    if result[0] == -3:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You cannot both buy and sell the same event at the same price')
        return
    if result[0] == -4:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are at the position limit for this event. You can only sell')
        return

    await ctx.message.add_reaction(SUCCESS_EMOJI)
    await announce_trade(ctx, result[1])



@bot.command(name='sell')
async def sell_command(ctx, *args):
    async def usage(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('USAGE: $$sell [event number] [price between 0-100]')

    discord_id = str(ctx.author.id)

    if len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
        await usage(ctx)
        return
    try:
        display_order = int(args[0])
        price = int(args[1])
    except ValueError:
        await usage(ctx)
        return
    if price < 0 or price > 100:
        await usage(ctx)
        return

    result = controller.sell(discord_id, display_order, price)

    if result[0] == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are not registered in the game')
        return
    if result[0] == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Event does not exist')
        return
    if result[0] == -3:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You cannot both buy and sell the same event at the same price')
        return
    if result[0] == -4:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are at the position limit for this event. You can only buy')
        return

    await ctx.message.add_reaction(SUCCESS_EMOJI)
    await announce_trade(ctx, result[1])



@bot.command(name='cancel')
async def cancel_command(ctx, *args):
    async def usage(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('USAGE: $$cancel [buy/sell] [event number]')
    
    discord_id = str(ctx.author.id)

    if len(args) < 2 or not args[1].isdigit() or args[0].lower() not in ['buy', 'sell', 'b', 's']:
        await usage(ctx)
        return
    
    is_buy = args[0].lower() in ['buy', 'b']
    try:
        display_order = int(args[1])
    except ValueError:
        await usage(ctx)
        return
    
    if is_buy:
        result = controller.cancel_buy(discord_id, display_order)
    else:
        result = controller.cancel_sell(discord_id, display_order)

    if result == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You are not registered in the game')
        return
    if result == -2:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Event does not exist')
        return
    if result == -3:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: You do not have such an order to cancel')
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

    guild = ctx.guild
    user = ctx.guild.get_member(id)
    result = controller.add_account(str(id), get_name(user))

    if result == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: %s is already in the game' % get_name(user))
        return
    
    await ctx.message.add_reaction(SUCCESS_EMOJI)



@bot.command(name='mark')
async def mark_command(ctx, *args):
    async def failure(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)

    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to access $$mark')
        await failure(ctx)
        return

    if len(args) < 2 or args[1] not in ['y', 'n']:
        await failure(ctx)
        return
    try:
        display_order = int(args[0])
    except ValueError:
        await failure(ctx)
        return
    
    did_occur = args[1] == 'y'
    result = controller.mark_occurred(display_order, did_occur)

    if result == -1:
        await ctx.message.add_reaction(FAILURE_EMOJI)
        await ctx.send('ERROR: Event does not exist')
        return

    await ctx.message.add_reaction(SUCCESS_EMOJI)



@bot.command(name='paybonus')
async def paybonus_command(ctx, *args):
    async def failure(ctx):
        await ctx.message.add_reaction(FAILURE_EMOJI)

    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to access $$paybonus')
        await failure(ctx)
        return

    bonus_amounts = controller.pay_bonus()
    messages = []
    for account_id, bonus_amount in sorted(bonus_amounts.items(), key = lambda x: -x[1]):
        messages.append('<@%s> has earned a bonus of %d' % (account_id, bonus_amount))

    await ctx.message.add_reaction(SUCCESS_EMOJI)
    await ctx.send('\n'.join(messages))



@bot.command(aliases=["quit"])
async def close(ctx):
    if str(ctx.author) not in ADMINS:
        print(str(ctx.author), 'tried to quit')
        return

    global controller
    del controller

    await ctx.message.add_reaction(SUCCESS_EMOJI)
    await bot.close()
    print("Bot Closed")



bot.run(TOKEN)
