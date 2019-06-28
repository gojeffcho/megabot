import discord

from collections import Counter
from time import time
from datetime import datetime, timedelta

from discord.ext import commands
from bot_config import CONFIG
from bot_secure import watch, unwatch
from bot_utility import is_admin, is_mod, find_channel, find_role, \
                        save_data, send_notification, user_has_role


class Admin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  
  @commands.command()
  async def addchannel(self, ctx, name, category):
    """Admin command: Create a new channel with the correct permissions.
    
    Args:
      name (String)
        The name of the new channel.
      
      category(String)
        The name of one of the existing categories to place the new channel in.
    
    Returns:
      None
    """
    if not is_admin(ctx.author):
      await ctx.send('`!addchannel`: Only admins may use this command.')
      return
    
    if not name:
      await ctx.send('`!addchannel`: You must specify a name for the new channel.')
      return
    
    if not category:
      await ctx.send('`!addchannel`: You must specify a category for the new channel.')
      return
      
    channel_list = ctx.guild.text_channels
    
    for channel in channel_list:
      if channel.name == name:
        await ctx.send('`!addchannel`: A channel with this name already exists.')
        return
    
    category_list = ctx.guild.categories
    target_category = None
    
    for cat in category_list:
      if cat.name == category:
        target_category = cat
    
    if not target_category:
      await ctx.send('`!addchannel`: This category could not be found.')
      return
        
    new_channel = await ctx.guild.create_text_channel(name, 
                                                      category=target_category)
    
    if not isinstance(new_channel, discord.TextChannel):
      await ctx.send('`!addchannel`: Unable to add new channel.')
    
    cap_role = find_role(ctx.guild, CONFIG['CapRole'])
    
    await new_channel.set_permissions(cap_role, send_messages=False)
    
    if not new_channel.overwrites_for(cap_role):
      await ctx.send('`!addchannel`: Cap role overwrite not effective.')
    
    await ctx.send('`!addchannel`: {} created in {}!'.format(name, category))
  
  
  @commands.command()  
  async def crap(self, ctx, mention, *, reason='no reason'):
    """Admin command: Crap a mentioned user.
    
    Args:
      mention (User)
        The user to crap.
    
    Returns:
      None
    """
    if not is_admin(ctx.author):
      if (ctx.author.id == 269214028209848321):
        pass
      else:
        await ctx.send('No.')
        return
    
    if len(ctx.message.mentions) == 0:
      await ctx.send("`!crap`: The user to be crapped must be @-mentioned as the first argument.")
      return
    
    target_user = ctx.message.mentions[0]
    crap_role = find_role(ctx.guild, CONFIG['CrapRole'])
    notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])
    
    if not crap_role:
      await ctx.send('`!crap`: There was an error attempting to crap {}.'.format(target_user.display_name))
      return
    
    if user_has_role(target_user, CONFIG['CrapRole']):
      await ctx.send('`!crap`: {} has been double-crapped!'.format(target_user.display_name))
    
    else:
      await target_user.add_roles(crap_role)
      await ctx.send('💩💩💩')
      await notifications_channel.send('{} has been crapped for {}'.format(
                                                                    target_user.display_name, 
                                                                    reason))
    

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
  async def uncrap(self, ctx, mention):
    """Admin command: Uncrap a mentioned user.
    
    Args:
      mention (User)
        The user to uncrap.
    
    Returns:
      None
    """
    if not is_admin(ctx.author):
      if ctx.author.id == 269214028209848321:
        pass  
      else:
        await ctx.send('Nope.')
        return
    
    if len(ctx.message.mentions) == 0:
      await ctx.send("`!uncrap`: The user to be uncrapped must be @-mentioned as the first argument.")
      return
    
    target_user = ctx.message.mentions[0]
    crap_role = find_role(ctx.guild, CONFIG['CrapRole'])
    notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])
    
    if not crap_role:
      await ctx.send('`!uncrap`: There was an error attempting to uncrap {}.'.format(target_user.display_name))
      return
    
    if user_has_role(target_user, CONFIG['CrapRole']):
      await target_user.remove_roles(crap_role)
      await ctx.send('🚫💩')
      await notifications_channel.send('{} has been uncrapped.'.format(target_user.display_name))
    
    else:
      await ctx.send('`!uncrap`: {} doesn\'t appear to be crapped.'.format(target_user.display_name))
                                                                    
                                                                    
  @commands.command()
  async def stats(self, ctx, num: int=5, range: str='month'):
    """Admin command: generate post stats.
    
    Args:
      num (Int, optional)
        The number of top posters to find. Defaults to 5.
        
      range (String, optional)
        One of {all, month}. Defaults to month.
    
    Returns:
      None
    """
    if not is_admin(ctx.author):
      await ctx.send('`!stats`: This is an admin-only command.')
      return
      
    if range != 'month' and range != 'all':
      await ctx.send('`!stats`: Range must be `month` or `all`.')
      return
      
    await ctx.send('`!stats`: Calculating post statistics. This will take some time.')
    
    start_time = time()
    
    channels = ctx.guild.channels
    count = Counter()    
    target_date = datetime.now() - timedelta(days=30)
    
    for channel in channels:
      if isinstance(channel, discord.TextChannel):      
        if channel.category.name not in CONFIG['StatsCategories']:
          continue
      
        if range == 'all':
          async for post in channel.history(limit=None):
            count[post.author] += 1

        elif range == 'month':
          async for post in channel.history(limit=None, after=target_date):
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
    
    if range == 'month':
      await ctx.send('The top posters for the past 30 days are: {} \n {}'.format(
                                  output_text, time_output))
    
    elif range == 'all':
      await ctx.send('The top posters of all time are: {} \n {}'.format(
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
