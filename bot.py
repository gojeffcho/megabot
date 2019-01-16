from discord.ext.commands import Bot

from bot_config import CONFIG
from bot_secure import SECURE
import random

startup_extensions = ['bot_admin_commands', 'bot_mod_commands',
                      'bot_commands']

megabot = Bot(command_prefix = CONFIG['Prefix'])


@megabot.event
async def on_ready():
  """Logs connection message for the Megabot."""

  random.seed()
  print('Logged on as {0.user}.'.format(megabot))


@megabot.event
async def on_member_join(member):
  welcome_channel = find_channel(member.guild, CONFIG['WelcomeChannel'])
  rules_channel = find_channel(member.guild, CONFIG['RulesChannel'])

  new_role = find_role(member.guild, CONFIG['NewRole'])

  await member.add_roles(new_role)
  await welcome_channel.send('Hello and welcome to the Megachannel, {0}! '.format(member.display_name) +
                             'Please make sure you read the {0} first '.format(rules_channel.mention) +
                             '- they\'re short, simple, and easy to follow. ' +
                             'Once you have read and agreed to the rules, you will have access to ' +
                             'all the regular channels on the server!')


@megabot.event
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


if __name__ == '__main__':
  for extension in startup_extensions:
    try:
      megabot.load_extension(extension)

    except Exception as e:
      exc = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\n{}'.format(extension, exc))

  megabot.run(SECURE['Token'])
