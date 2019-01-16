from discord.ext.commands import Bot

import bot_events
import bot_admin_commands
import bot_mod_commands
import bot_commands

from bot_config import CONFIG
from bot_secure import SECURE

startup_extensions = ['bot_events', 'bot_admin_commands',
                      'bot_mod_commands', 'bot_commands']
                      
megabot = Bot(command_prefix = CONFIG['Prefix'])


if __name__ == '__main__':
  for extension in startup_extensions:
    try:
      bot.load_extension(extension)

    except Exception as e:
      exc = '{}: {}'.format(type(e).__name__, e)
      print('Failed to load extension {}\n{}'.format(extension, exc))

  megabot.run(SECURE['Token'])
