import discord

from collections import Counter
from time import time

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
  async def stats(self, ctx, num: int=5):
    """Admin command: generate post stats.
    
    Args:
      num (Int, Optional)
        The number of top posters to find. Defaults to 5.
    
    Returns:
      None
    """
    await ctx.send('`!stats`: Calculating post statistics. This will take some time.')
    
    start_time = time()
    
    channels = ctx.guild.channels
    count = Counter()
    
    for channel in channels:
      if isinstance(channel, discord.TextChannel):
        async for post in channel.history(limit=None):
          count[post.author] += 1
    
    max_name_width = 0
    max_num_width = 0
    
    top_list = count.most_common(num)
    
    for member, posts_num in top_list:
      first_name = member.display_name.split()[0]
      
      if first_name[-1] == ':':
        first_name = first_name[:-1]
        
      name_len = len(first_name)
      if name_len > max_name_width:
        max_name_width = name_len
      
      num_len = len('{}'.format(posts_num))
      if num_len > max_num_width:
        max_num_width = num_len
      
    output_text = ''
    
    for member, posts_num in top_list:
      first_name = member.display_name.split()[0]
      
      if first_name[-1] == ':':
        first_name = first_name[:-1]
      
      output_text += '\n `{0:.<{name}}..{1:.>{num}d}`'.format(
        first_name, posts_num, 
        name=max_name_width, num=max_num_width)
    
    end_time = time()
    
    time_output = 'This command executed in {:.2f} seconds'.format(
                                              end_time - start_time)
    
    await ctx.send('The top posters are: {} \n {}'.format(
                                output_text, time_output))
    

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
        return

      else:
        watched = ''

      for member in CONFIG['DATA']['monitor']:
        if member == CONFIG['DATA']['monitor'][0]:
          watched += '{}'.format(member.display_name)
        else:
          watched += ', {}'.format(member.display_name)

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
