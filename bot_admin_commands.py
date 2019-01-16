import discord

from discord.ext import commands
from bot_config import CONFIG
from bot_secure import watch, unwatch
from bot_utility import is_admin, is_mod, find_channel, find_role, \
                        save_data, send_notification, user_has_role


class Admin():
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def echo(self, ctx, *, message):
    """Admin command: make the bot say something.

    Args:
      message (String)
        The string to be said by the bot.

    Returns:
      None
    """
    if is_admin(ctx.author):
      await ctx.message.delete()
      await ctx.send(message)


  @commands.command()
  async def monitor(self, ctx, mention):
    """Admin command: monitor a user.  No reason, don't worry.

    Args:
      ctx (Context)

      mention (Member)

    Returns:
      None
    """
    target_user = ctx.message.mentions[0]

    if not is_admin(ctx.author):
      if ctx.author == target_user:
        notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])
        cap(ctx, ctx.author)
        await ctx.send("`!monitor`: This is an admin-only command. {} has been capped for trying to use it.".format(ctx.author.display_name))
        await notifications_channel.send('{} was capped by the `!monitor` command!')

      return

    if len(ctx.message.mentions) == 0:
      await ctx.send("`!monitor`: The user to be monitored must be @-mentioned as the first argument.")
      return

    if not target_user in CONFIG['DATA']['monitor']:
      watch(ctx, target_user)
      await ctx.send('`!monitor`: {} has been placed on watch.'.format(target_user.display_name))
      CONFIG['DATA']['monitor'].append(target_user)
      save_data(CONFIG['DATAFILE'])
    
    else:
      await ctx.send('`!monitor`: {} is already on watch.')
    

  @commands.command()
  async def unmonitor(self, ctx, mention):
    """Admin command: unmonitor a user.

    Args:
      ctx (Context)

      mention (Member)

    Returns:
      None
    """
    target_user = ctx.message.mentions[0]

    if not is_admin(ctx.author):
      if ctx.author == target_user:
        notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])
        cap(ctx, ctx.author)
        await ctx.send("`!unmonitor`: This is an admin-only command. {} has been capped for trying to use it.".format(ctx.author.display_name))
        await notifications_channel.send('{} was capped by the `!unmonitor` command!')

      return

    if len(ctx.message.mentions) == 0:
      await ctx.send("`!unmonitor`: The user to be monitored must be @-mentioned as the first argument.")
      return

    if target_user in CONFIG['DATA']['monitor']:
      unwatch(ctx, target_user)
      await ctx.send('`!unmonitor`: {} has been removed from watch.'.format(target_user.display_name))
      CONFIG['DATA']['monitor'].remove(target_user)
      save_data(CONFIG['DATAFILE'])
    
    else:
      await ctx.send('`!unmonitor`: {} is not on watch.'.format(target_user.display_name))
    
    
  @commands.command()
  async def watchlist(self, ctx):
    """Admin command: list users on the watchlist."""
  
    if not is_admin(ctx.author):
      await ctx.send('`!watchlist`: This is an admin-only command.')
  
    else:
    
      if CONFIG['DATA']['monitor'] == []:
        await ctx.send('`!watchlist`: No users currently on watch.')
      
      else:
        watched = ''
    
        [watched + ' {}'.format(member.display_name)
        for member 
        in CONFIG['DATA']['monitor']]
    
        await ctx.send('`!watchlist`: {}'.format(watched))
  
  @commands.command()
  async def write(self, ctx):
    """Admin command: write out current state of persistent data."""
    
    if not is_admin(ctx.author):
      await ctx.send('`!write`: This is an admin-only command.')
    
    else:
      save_data(CONFIG['DATAFILE'])
      await ctx.send('`!write`: Persistent store updated.')


def setup(bot):
  bot.add_cog(Admin(bot))