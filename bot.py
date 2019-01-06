import discord
from discord.ext.commands import Bot
from config import CONFIG
from secure import SECURE
from utility import is_admin, is_mod, find_channel, \
                    find_role, send_notification, user_has_role

megabot = Bot(command_prefix = CONFIG['Prefix'])


@megabot.event
async def on_ready():
  """Logs connection message for the Megabot."""

  print('Logged on as {0.user}.'.format(megabot))

@megabot.event
async def on_member_join(member):
  welcome_channel = find_channel(member.guild, CONFIG['WelcomeChannel'])
  rules_channel = find_channel(member.guild, CONFIG['RulesChannel'])

  new_role = find_role(member.guild, CONFIG['NewRole'])

  await member.add_roles(new_role)
  await welcome_channel.send( 'Hello and welcome to the Megachannel, {0}! '.format(member.name) +
                              'Please make sure you read the {0} first '.format(rules_channel.mention) +
                              '- they\'re short, simple, and easy to follow. ' +
                              'Once you have read and agreed to the rules, you will have access to ' +
                              'all the regular channels on the server!')



@megabot.command()
async def agree(ctx):
  """Agree to the rules and join the server."""

  member = ctx.author
  is_new = user_has_role(member, CONFIG['NewRole'])
  new_role = find_role(ctx.guild, CONFIG['NewRole'])
  confirmed_role = find_role(ctx.guild, CONFIG['ConfirmedRole'])
  notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])
  profiles_channel = find_channel(ctx.guild, CONFIG['ProfilesChannel'])

  if is_new and CONFIG['WelcomeChannel'] in ctx.message.channel.name:
    await member.remove_roles(new_role)
    await send_notification(ctx.guild, 'Please welcome our newest member {0} to the Megachannel!'.format(member.name))
    await member.send('You have agreed to the rules of the Megachannel! Please make sure you check back often ' +
                      'to keep up-to-date with changes.' +
                      '\n\nYou can now use any publicly-available channel; for example, you don\'t have to ' +
                      'be taking the course that corresponds to a course channel in order to chat there. ' +
                      'Feel free to head over to the {} channel '.format(profiles_channel.mention) +
                      'and introduce yourself - this is handy because the Megachannel has users who are in ' +
                      'different programs and courses who might not know each other! You can also add any ' +
                      'courses or game developer roles to yourself - type `!help` in a public channel ' +
                      'to see all available bot commands.' +
                      '\n\nLastly, you may want to mute any channels you\'re not particularly interested in ' +
                      'as we can get into spirited discussions that can blow up your notifications.')
    await member.add_roles(confirmed_role)
  else:
    await member.send('You have already agreed to the rules on this server.')


# Command: help

# Command: reset all to confirmed

# Command: add course or role

# Command: get profile

# Command: admin setname
@megabot.command()
async def setname(ctx, user, name):
  """Admin command: change a user's nickname on this server.

  Args:
    user (Member):
      The user whose nickname will be updated.

    name (String):
      String to set the user's nickname to - must be wrapped in
      quotation marks if longer than one word.
  """
  if is_admin(ctx.author) or is_mod(ctx.author):

    if len(ctx.message.mentions) == 0:
      await ctx.send("`!setname`: The user whose name you wish to change must be mentioned as the first argument.")
      return

    target_user = ctx.message.mentions[0]
    old_name = target_user.name
    await target_user.edit(nick = name)
    await send_notification(ctx.guild, "{} updated {}'s nickname to {}!".format(ctx.author.name, old_name, name))

  else:

    await ctx.send("`!setname`: You do not have the privileges to use this command.")


# Command: user setname
@megabot.command()
async def nick(ctx, name):
  """Change your nickname on this server.

  Args:
    name (String)
      String that you want the nickname set to - must be wrapped in
      quotation marks if longer than one word.

  Returns:
    None
  """
  old_name = ctx.author.name
  await ctx.author.edit(nick = name)
  await send_notification(ctx.guild, "{} updated their nickname to {}!".format(old_name, name))


# Command: cap

# Command: uncap

@megabot.command()
async def echo(ctx, message):
  """Admin command: make the bot say something.

  Args:
    message (String)
      The string to be said by the bot.

  Returns:
    None
  """
  if is_admin(ctx.author):
    await ctx.send(message)




megabot.run(SECURE['Token'])