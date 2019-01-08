from discord.ext.commands import Bot
import random

from config import CONFIG
from secure import SECURE
from utility import is_admin, is_mod, find_channel, \
                    find_role, send_notification, user_has_role

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
  await welcome_channel.send( 'Hello and welcome to the Megachannel, {0}! '.format(member.nick) +
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


@megabot.command()
async def agree(ctx):
  """Agree to the rules and join the server."""

  member = ctx.author
  is_new = user_has_role(member, CONFIG['NewRole'])
  new_role = find_role(ctx.guild, CONFIG['NewRole'])
  confirmed_role = find_role(ctx.guild, CONFIG['ConfirmedRole'])
  profiles_channel = find_channel(ctx.guild, CONFIG['ProfilesChannel'])

  if is_new and CONFIG['WelcomeChannel'] in ctx.message.channel.name:
    await member.remove_roles(new_role)
    await send_notification(ctx.guild,
                            'Please welcome our newest member {0} to the Megachannel!'.format(member.mention))
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


@megabot.command()
async def cap(ctx, mention):
  """Mod command: Dunce cap a mentioned user.

  Args:
    mention (User)
      The user to cap.

  Returns:
    None
  """
  if len(ctx.message.mentions) == 0:
    await ctx.send("`!cap`: The user to be capped must be @-mentioned as the first argument.")
    return

  target_user = ctx.message.mentions[0]
  cap_role = find_role(ctx.guild, CONFIG['CapRole'])
  staff_channel = find_channel(ctx.guild, CONFIG['StaffChannel'])
  notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])

  if not cap_role:
    await ctx.send('`!cap`: There was an error attempting to cap {}.'.format(target_user.mention))
    return

  # Attempt to cap the Admin
  if is_admin(target_user):
    await ctx.author.send('You have been dunce capped for attempting to dunce cap the admin. ' +
                          'While you are dunce capped, you will not be able to send messages, ' +
                          'but you will be able to add reactions to other users\' messages. ' +
                          'Your dunce cap will be removed after a certain amount of time.')
    await ctx.send('{} has been capped for trying to cap {} - hoisted by your own petard!'.format(
                                                          ctx.author.mention, target_user.mention))
    await staff_channel.send('{} has been capped for attempting to cap {}!'.format(
                                          ctx.author.mention, target_user.mention))
    return

  # Moderator uses !cap
  if is_admin(ctx.author) or is_mod(ctx.author):

    if user_has_role(target_user, CONFIG['CapRole']):
      await ctx.send('`!cap`: {} is already capped!'.format(target_user.mention))

    else:
      await target_user.add_roles(cap_role)
      await target_user.send('You have been dunce capped for violating a rule. While you are ' +
                             'dunce capped, you will not be able to send messages, but you will ' +
                             'be able to add reactions to other users\' messages. The offending ' +
                             'violation must be remediated, and your dunce cap will be removed ' +
                             'after a certain amount of time.')
      await staff_channel.send('{} has been dunce capped by {}!'.format(
                                                                          target_user.mention,
                                                                          ctx.author.mention))
      await notifications_channel.send('{} has been dunce capped by {}!'.format(
                                                                          target_user.nick,
                                                                          ctx.author.nick))
      return

  # Non-moderator uses !cap
  else:
    await ctx.send('`!cap`: You are not worthy to wield the mighty cap.')


@megabot.command()
async def course(ctx, course):
  """Add a course role to yourself so you can be mentioned by the role.

  Args:
    course (String)
      See !courses for a list of current courses.

  Returns:
    None
  """
  if course not in CONFIG['CourseRoles']:
    await ctx.send("`!course`: `{}` is not an active course role.".format(course))
    return

  course_role = find_role(ctx.guild, course)
  if not course_role:
    await ctx.send("`!course`: `{}` could not be found. Please check the spelling and punctuation.".format(course))

  if course_role in ctx.author.roles:
    await ctx.author.remove_roles(course_role)
    await send_notification(ctx.guild, "{} has removed themselves from `{}`.".format(ctx.author.mention, course_role))
  else:
    await ctx.author.add_roles(course_role)
    await send_notification(ctx.guild, "{} has added themselves to `{}`.".format(ctx.author.mention, course_role))
    await ctx.author.send('The course {0} was added. You will now be notified '.format(course_role) +
                          'when someone mentions `@{0}`.'.format(course_role))


@megabot.command()
async def courses(ctx):
  """List the current courses a user can add."""

  course_list = ''

  for course in CONFIG['CourseRoles']:
    course_list += '\n  * `{}`'.format(course)

  await ctx.author.send('The current courses you can add are: ' + course_list)


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
    await ctx.message.delete()
    await ctx.send(message)

@megabot.command()
async def invite(ctx, discord_user, *, desc):
  """Request an invite link for a new user.

  Args:
    discord_user (String)
      The full Discord username (with tag number) you wish to invite.

    desc (String)
      Quick introduction to the person, why you want to invite them,
      and whether they are in the Game Development Certificate.

  Returns:
    None
  """
  user = discord_user.split('#')
  if not len(user) == 2:
    await ctx.send('`!invite`: You must enter the full Discord username ' +
             'including tag number (e.g. Cipherkey#1762).')
    return

  if not len(desc.split()) > 1:
    await ctx.send('`!invite`: Your description requires more detail '
             '(e.g. "Jeff Cho, 4th year CS student, in Game Dev ' +
             'Certificate program, <additional description>...").')
    return

  admin_user = ctx.guild.owner
  await admin_user.send('{} has requested an invite for {}: {}'.format(
                                    ctx.author.nick, discord_user, desc))


@megabot.command()
async def nick(ctx, *, name):
  """Change your nickname on this server.

  Args:
    name (String)
      String to which you want your nickname set.

  Returns:
    None
  """
  old_name = ctx.author.nick
  await ctx.author.edit(nick=name)
  await send_notification(ctx.guild, "{} updated their nickname to {}!".format(old_name, name))


@megabot.command()
async def postcount(ctx):
  """Mod command: Get the top posters for the server."""

  if is_admin(ctx.author) or is_mod(ctx.author):

    members = ctx.guild.members
    count = {}

    for member in members:
      await ctx.send('Getting data for {}'.format(member.nick)) # DEBUG
      messages = await member.history(limit=None).flatten()
      count[member] = len(messages)
      await ctx.send('{} had {} posts.'.format(member.nick, count[member])) # DEBUG

    sorted_members = sorted(count.items(), key=lambda kv: kv[1])[:10]

    output_members = ['\n * {}: {}'.format(k, v) for k, v in sorted_members]

    await ctx.send(output_members) # DEBUG

    await ctx.send('The top posters to date are: {}'.format(''.join(output_members)))


  else:

    await ctx.send('`!postcount`: Only a mod or admin may use this command.')


@megabot.command()
async def profile(ctx, mention):
  """Look up a user's profile, if they have made a post in #profiles.

  Args:
    mention (String: user mention)
      The user's profile to look up.

  Returns:
    None
  """
  if user_has_role(ctx.author, CONFIG['ConfirmedRole']):
    if len(ctx.message.mentions) < 1 or len(ctx.message.mentions) > 1:
      await ctx.author.send('`!profile`: You must mention one user whose profile you wish to look up.')
      return

    target_user = ctx.message.mentions[0]
    profiles_channel = find_channel(ctx.guild, CONFIG['ProfilesChannel'])
    profile = None

    async for message in profiles_channel.history(limit = 100 + len(ctx.guild.members)):
      if message.author == target_user:
        profile = message
        await ctx.send('You can find {}\'s profile at: {}'.format(target_user.nick, message.jump_url))
        return

    if not profile:
      await ctx.send('{} has not yet posted to {}.'.format(target_user.nick, profiles_channel.mention))

  else:
    ctx.author.send('You must agree to the rules to view any profiles.')


@megabot.command()
async def reset(ctx):
  """Reset your courses, roles, and permissions back to defaults."""

  if user_has_role(ctx.author, CONFIG['ConfirmedRole']):
    for role in ctx.author.roles:
      if role.name != '@everyone' and role.name != CONFIG['ConfirmedRole'] and role.name != CONFIG['ModRole']:
        await ctx.author.remove_roles(role)

  await ctx.author.send('Your permissions to the server have been reset. ' +
                        'Please add back any roles and courses you want on your profile.')


@megabot.command()
async def role(ctx, role):
  """Add a game development role to yourself so you can be mentioned by the role.

  Args:
    role (String)
      See !roles for a list of current roles.

  Returns:
    None
  """

  if role == 'programmers':
    role = 'developers'

  if role not in CONFIG['GameDevRoles']:
    await ctx.send("`!role`: `{}` is not an active game development role.".format(role))
    return

  gamedev_role = find_role(ctx.guild, role)
  if not gamedev_role:
    await ctx.send("`!role`: `{}` could not be found. Please check the spelling and punctuation.".format(role))

  if gamedev_role in ctx.author.roles:
    await ctx.author.remove_roles(gamedev_role)
    await send_notification(ctx.guild, "{} has removed themselves from `{}`.".format(
                                                    ctx.author.mention, gamedev_role))
  else:
    await ctx.author.add_roles(gamedev_role)
    await send_notification(ctx.guild, "{} has added themselves to `{}`.".format(
                                                ctx.author.mention, gamedev_role))
    await ctx.author.send('The {0} role was added. You will now be notified '.format(gamedev_role) +
                          'when someone mentions `@{0}`.'.format(gamedev_role))


@megabot.command()
async def roles(ctx):
  """List the current roles a user can add."""

  role_list = ''

  for role in CONFIG['GameDevRoles']:
    role_list += '\n  * `{}`'.format(role)

  await ctx.author.send('The current roles you can add are: ' + role_list)


@megabot.command()
async def roll(ctx, dice):
  """Roll a die in the format #d#.

  Args:
    dice (String)
      String of format #d#, e.g. 3d6, to roll a d6 three times.

  Returns:
    result (Int)
    The result of rolling the dice.
  """
  if not dice:
    await ctx.send('`!roll`: You have not specified the dice to roll.')
    return

  dice_available = CONFIG['Dice']
  args = dice.split('d')

  if len(args) != 2:
    await ctx.send('`!roll`: Please check your dice syntax.')
    return

  if not args[0].isdigit() or not args[1].isdigit():
    await ctx.send('`!roll`: Please check your dice syntax. It must be of the format #d#, e.g. `!roll 3d6`.')
    return

  num_dice = int(args[0])
  die_type = int(args[1])

  if die_type not in dice_available:
    dice_output = ['d{}'.format(die) for die in dice_available]

    await ctx.send('`!roll`: Dice must be one of: ' + ', '.join(dice_output))
    return

  if num_dice < 1:
    await ctx.send('`!roll`: The first number must be >= 1.')

  roll_total = 0
  for i in range(num_dice):
    roll_total += random.randint(1, die_type)

  await ctx.send('{} rolls {} and gets... {}!'.format(ctx.author.mention, dice, roll_total))


@megabot.command()
async def setname(ctx, user, *, name):
  """Mod command: change a user's nickname on this server.

  Args:
    user (Member):
      The user whose nickname will be updated.

    name (String):
      String to which to set the user's nickname.
  """
  if is_admin(ctx.author) or is_mod(ctx.author):

    if len(ctx.message.mentions) == 0:
      await ctx.send("`!setname`: The user whose name you wish to change must be mentioned as the first argument.")
      return

    target_user = ctx.message.mentions[0]
    old_name = target_user.nick
    await target_user.edit(nick = name)
    await send_notification(ctx.guild, "{} updated {}'s nickname to {}!".format(ctx.author.nick, old_name, name))

  else:

    await ctx.send("`!setname`: You do not have the privileges to use this command.")


@megabot.command()
async def uncap(ctx, mention):
  """Mod command: Remove the dunce cap from a mentioned user.

    Args:
      mention (User)
        The user to uncap.

    Returns:
      None
  """
  if len(ctx.message.mentions) == 0:
    await ctx.send("`!uncap`: The user to be uncapped must be @-mentioned as the first argument.")
    return

  target_user = ctx.message.mentions[0]
  cap_role = find_role(ctx.guild, CONFIG['CapRole'])
  staff_channel = find_channel(ctx.guild, CONFIG['StaffChannel'])
  notifications_channel = find_channel(ctx.guild, CONFIG['NotificationsChannel'])

  if not cap_role:
    await ctx.send('`!uncap`: There was an error attempting to uncap {}.'.format(target_user.mention))
    return

  # Moderator uses !cap
  if is_admin(ctx.author) or is_mod(ctx.author):

    if not user_has_role(target_user, CONFIG['CapRole']):
      await ctx.send('Are you blind, {}? You can\'t uncap {} '.format(ctx.author.mention, target_user.nick) +
                     'if they\'re not wearing the Dunce Cap!')

    else:
      await target_user.remove_roles(cap_role)
      await target_user.send('Your dunce cap is lifted.')
      await staff_channel.send('{} has been uncapped by {}!'.format(
                                                                target_user.mention,
                                                                ctx.author.mention))
      await notifications_channel.send('{} has been uncapped by {}!'.format(
                                                                target_user.nick,
                                                                ctx.author.nick))
      return

  else:

    # Non-moderator attempts to use !uncap
    if not user_has_role(target_user, CONFIG['CapRole']):
      await ctx.send('`!uncap`: How can you uncap someone who isn\'t ' +
                     'wearing a cap to begin with? Reconsider your life choices.')
    else:
      await ctx.send('`!uncap`: You are not strong enough to discard the mighty cap.')



megabot.run(SECURE['Token'])