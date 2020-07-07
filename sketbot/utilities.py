import discord
from discord.ext import commands, tasks


async def wait_for_message(bot, ctx, message=None, delete_after=None, timeout=None):
    if message is None:
        return await bot.wait_for(event='message', check=lambda message: ctx.author == message.author, timeout=timeout)
    else:
        await ctx.send(message, delete_after=delete_after)
        msg = await bot.wait_for(event='message', check=lambda message: ctx.author == message.author, timeout=timeout)
        if delete_after != None:
            await msg.delete(delay=delete_after)
        return msg


async def wait_for_query(bot, ctx, message, delete_after=None, timeout=None):
    accept_emoji = "✅"
    decline_emoji = "❌"

    msg = await ctx.send(message, delete_after=delete_after)
    await msg.add_reaction(accept_emoji)
    await msg.add_reaction(decline_emoji)
    reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user and reaction.message.id == msg.id, timeout=timeout)
    if delete_after != None:
        await msg.delete(delay=delete_after)

    if reaction.emoji == accept_emoji:
        return True
    else:
        return False


async def wait_for_reaction(bot, ctx, message=None, delete_after=None, timeout=None):
    reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user and reaction.message.id == message.id, timeout=timeout)
    return reaction

async def choose_channel(bot, ctx, msg="Choose channel index"):
    await ctx.send(msg)
    response = "```"
    for index, channel in enumerate(ctx.guild.text_channels):
        response += f"{index + 1}: {channel.name}\n"
    response += "```"

    await ctx.send(response)

    msg = await wait_for_message(bot, ctx, 20)
    index = int(msg.content)

    return ctx.guild.text_channels[index - 1]
    
async def choose_role(bot, ctx, msg="Choose role index"):
    await ctx.send(msg)
    response = "```"
    for index, role in enumerate(ctx.guild.roles):
        response += f"{index + 1}: {role.name}\n"
    response += "```"

    await ctx.send(response)

    msg = await wait_for_message(bot, ctx, 20)
    index = int(msg.content)

    return ctx.guild.roles[index - 1]

async def has_role(member:discord.Member, roles):
    if member.guild_permissions.administrator:
        return True

    for role in member.roles:
        if (role.name, role.id) in roles:
            return True

    return False
