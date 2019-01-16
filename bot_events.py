import discord
from discord.ext import events
from bot_config import CONFIG
from bot_utility import is_admin, is_mod, find_channel, \
                        find_role, send_notification, user_has_role


class BotEvents():
  def __init__(self, bot):
    self.bot = bot

  @events.event
  async def on_ready():
    """Logs connection message for the Megabot."""

    random.seed()
    print('Logged on as {0.user}.'.format(megabot))


  @events.event
  async def on_member_join(member):
    welcome_channel = find_channel(member.guild, CONFIG['WelcomeChannel'])
    rules_channel = find_channel(member.guild, CONFIG['RulesChannel'])

    new_role = find_role(member.guild, CONFIG['NewRole'])

    await member.add_roles(new_role)
    await welcome_channel.send( 'Hello and welcome to the Megachannel, {0}! '.format(member.display_name) +
                                'Please make sure you read the {0} first '.format(rules_channel.mention) +
                                '- they\'re short, simple, and easy to follow. ' +
                                'Once you have read and agreed to the rules, you will have access to ' +
                                'all the regular channels on the server!')


  @events.event
  async def on_command_error(ctx, e):
    """Command error handler.

    Args:
      ctx (Context)
        Context of the Exception.

      e (Exception)
        Exception object.

    Returns:
      None
    """
    await ctx.send('Error: {} Please use `!help` to list available commands '.format(e) +
                   'and `!help <command>` to see the complete docstring.')

  def setup(bot):
    bot.add_cog(BotEvents(bot))