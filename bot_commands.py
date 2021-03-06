import discord
from discord.ext import commands
from bot_config import CONFIG
from bot_database import conn, cursor, create_db_user, get_db_user
from bot_utility import is_admin, is_mod, find_channel, find_role, \
                        match_role, send_notification, user_has_role

import random
from time import sleep
from datetime import datetime, timedelta

class User(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.command()
  async def agree(self, ctx):
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



  @commands.command()
  async def ask(self, ctx, *, question):
    """Ask the Magic 8-Ball a question.
    
    Args:
      question (String)
        The question you wish to ask the Magic 8-Ball.
    """
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!ask`: You cannot use this command until you have agreed to the rules.')
      return
      
    if not question:
      await ctx.send('`!ask`: You must specify a question.')
      return
    
    msg_txt = '{} asks the Magic 8-Ball:\n"{}"\n\n'.format(ctx.author.display_name, question)
    
    msg = await ctx.send(msg_txt)
    
    for i in range(3):
      sleep(0.5)
      msg_txt = msg_txt + '.'
      await msg.edit(content=msg_txt)
    
    sleep(0.5)
    
    msg_txt = msg_txt + '\n\nThe Magic 8-Ball answers: `' + random.choice(CONFIG['8Ball']) + '`'
    
    await msg.edit(content=msg_txt)
  

  @commands.command()
  async def claim(self, ctx, *, event):
    """Claim an event channel, if it is not previously claimed."""

    channel = ctx.message.channel

    if not CONFIG['EventChannelPrefix'] in channel.name:
      await ctx.send('`!claim`: This command can only be used in an event channel.')
      return

    if await channel.pins():
      await ctx.send('`!claim`: This channel appears to have an active claim. Please check the pinned ' +
                     'messages and ask the person who claimed it to `!release` it if you believe their ' +
                     'event is finished.')
      return

    if not event:
      await ctx.send('`!claim`: You must specify the event and description for the claim.')
      return

    await ctx.message.pin()
    await ctx.send('{0} has claimed this event channel: {1}!'.format(ctx.author.display_name, event))


  @commands.command()
  async def course(self, ctx, course):
    """Add a course role to yourself so you can be mentioned by the role.

    Args:
      course (String)
        See !courses for a list of current courses.

    Returns:
      None
    """
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!course`: You cannot use this command until you have agreed to the rules.')
      return

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


  @commands.command()
  async def courses(self, ctx):
    """List the current courses a user can add."""

    course_list = ''

    for course in CONFIG['CourseRoles']:
      course_list += '\n  * `{}`'.format(course)

    await ctx.author.send('The current courses you can add are: ' + course_list)


  @commands.command()
  async def emote(self, ctx, emote):
    """Send an emote.
    
    Args:
      emote (String)
        The name of the emote you wish to send.
    """
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!emote`: You cannot use this command until you have agreed to the rules.')
      return
      
    if not emote:
      await ctx.send('`!emote`: You must specify the emote you wish to send.')
      return
    
    emotes = CONFIG['Emotes'].copy()
    if user_has_role(ctx.author, CONFIG['AdminRole']):
      emotes.update(CONFIG['SpecialEmotes'])
    
    if emote not in emotes.keys():
      await ctx.send('`!emote`: This emote is not recognized.  Use `!emotes` to see the current list of emotes.')
      return
      
    emote_file = CONFIG['EmotePath'] + emotes[emote]
    emote_embed = discord.Embed(type='rich')
    emote_embed.set_image(url=emote_file)
    
    await ctx.send(content=None, embed=emote_embed)
    return


  @commands.command()
  async def emotes(self, ctx):
    """See the current list of emotes for the !emote command."""
    
    emotes = list(CONFIG['Emotes'].keys())
    if user_has_role(ctx.author, CONFIG['AdminRole']):
      emotes += list(CONFIG['SpecialEmotes'].keys())
    emotes.sort()
    outstring = 'Emotes:\n'
    
    for emote in emotes:
      outstring += ' * ' + emote + '\n'
    
    await ctx.send(outstring)
    return
    

  @commands.command()
  async def invite(self, ctx, discord_user, *, desc):
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
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!invite`: You cannot use this command until you have agreed to the rules.')
      return

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

    if not ctx.author.joined_at < datetime.now() - timedelta(days=14):
      await ctx.send('`!invite`: You must have been on the Megachannel for at least two weeks to invite others.')
      return

    user = get_db_user(conn, cursor, ctx.author)

    if not user:
      create_db_user(conn, cursor, ctx.author)

    cmd = '''INSERT INTO notes
              VALUES (NULL, ?, ?, ?, 'invite', ?)'''
    params = (datetime.now(), ctx.author.id, ctx.author.name, discord_user + ': ' + desc)
    cursor.execute(cmd, params)
    conn.commit()

    admin_user = ctx.guild.owner
    await admin_user.send('{} has requested an invite for {}: {}'.format(
                                      ctx.author.display_name, discord_user, desc))
    await ctx.author.send('You have requested an invite for {}. '.format(discord_user) +
        'If approved, you will get a PM with the link to use.\n\n' +
        'Please remember that personality and fit are more important than convenience for server membership - ' +
        'there is a lot of personal and private information shared here, and we maintain a culture of respect ' +
        'and openness. Everyone must feel safe and comfortable.  The invited user is registered to you, and ' +
        'you are ultimately responsible for their behavior.\n\n' +
        'If you would like to retract your nomination, please send a DM to Jeff.')




  @commands.command()
  async def nick(self, ctx, *, name):
    """Change your nickname on this server.

    Args:
      name (String)
        String to which you want your nickname set.

    Returns:
      None
    """
    old_name = ctx.author.display_name
    await ctx.author.edit(nick=name)
    await send_notification(ctx.guild, "{} updated their nickname to {}!".format(old_name, name))


  @commands.command()
  async def profile(self, ctx, mention):
    """Look up a user's profile, if they have made a post in #profiles.

    Args:
      mention (String: user mention)
        The user's profile to look up.

    Returns:
      None
    """
    print('Context: {}'.format(ctx))

    if user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      if len(ctx.message.mentions) < 1 or len(ctx.message.mentions) > 1:
        await ctx.author.send('`!profile`: You must mention one user whose profile you wish to look up.')
        return

      target_user = ctx.message.mentions[0]
      print('User: {}'.format(target_user))

      profiles_channel = find_channel(ctx.guild, CONFIG['ProfilesChannel'])
      profile = None

      async for message in profiles_channel.history(limit = 100 + len(ctx.guild.members)):
        if message.author == target_user:
          profile = message
          await ctx.send('You can find {}\'s profile at: {}'.format(target_user.display_name, message.jump_url))
          return

      if not profile:
        await ctx.send('{} has not yet posted to {}.'.format(target_user.display_name, profiles_channel.mention))

    else:
      await ctx.author.send('You must agree to the rules to view any profiles.')


  @commands.command()
  async def release(self, ctx):
    """Claim an event channel, if it is not previously claimed."""

    channel = ctx.message.channel

    if not CONFIG['EventChannelPrefix'] in channel.name:
      await ctx.send('`!release`: This command can only be used in an event channel.')
      return

    pins = await channel.pins()

    if not pins:
      await ctx.send('`!release`: This channel does not appear to have an active claim to release.')
      return

    if pins[0].author == ctx.author or is_admin(ctx.author) or is_mod(ctx.author):
      await pins[0].unpin()
      await ctx.send('{0} has released this event channel!  It is now open to be claimed for other events'.
                format(ctx.author.display_name))
    
    else:
      await ctx.send('`!release`: You do not appear to be the user who claimed this channel.')
      return


  @commands.command()
  async def reset(self, ctx):
    """Reset your courses, roles, and permissions back to defaults."""

    if user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      for role in ctx.author.roles:
        if role.name != '@everyone' and role.name != CONFIG['ConfirmedRole'] and role.name != CONFIG['ModRole']:
          await ctx.author.remove_roles(role)
    else:
      await ctx.send('`!reset`: You cannot use this command until you have agreed to the rules.')

    await ctx.author.send('Your permissions to the server have been reset. ' +
                          'Please add back any roles and courses you want on your profile.')


  @commands.command()
  async def role(self, ctx, role):
    """Add a role to yourself so you can be mentioned by the role.

    Args:
      role (String)
        See !roles for a list of current roles.

    Returns:
      None
    """
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!role`: You cannot use this command until you have agreed to the rules.')
      return

    if role == 'programmers':
      role = 'developers'

    if role not in CONFIG['Roles']:
      await ctx.send("`!role`: `{}` is not an active role.".format(role))
      return

    target_role = find_role(ctx.guild, role)
    if not target_role:
      await ctx.send("`!role`: `{}` could not be found. Please check the spelling and punctuation.".format(role))
      return

    if target_role in ctx.author.roles:
      await ctx.author.remove_roles(target_role)
      await send_notification(ctx.guild, "{} has removed themselves from `{}`.".format(
                                                      ctx.author.mention, target_role))
    else:
      await ctx.author.add_roles(target_role)
      await send_notification(ctx.guild, "{} has added themselves to `{}`.".format(ctx.author.mention, target_role))
      await ctx.author.send('The {0} role was added. You will now be notified '.format(target_role) + 'when someone mentions `@{0}`.'.format(target_role))


  @commands.command()
  async def roles(self, ctx):
    """List the current roles a user can add."""

    role_list = ''

    for role in CONFIG['Roles']:
      role_list += '\n  * `{}`'.format(role)
    
    for role in CONFIG['CourseRoles']:
      role_list += '\n * `{}`'.format(role)

    await ctx.author.send('The current roles you can add are: ' + role_list)


  @commands.command()
  async def roll(self, ctx, dice):
    """Roll a die in the format XdY[+Z].

    Args:
      dice (String)
        String of format <X>d<Y>[+Z], where Z is an optional modifier - e.g. 3d6, to roll a d6 three times, or 3d6+2. You may roll a maximum of 20 dice.

    Returns:
      result (Int)
      The result of rolling the dice.
    """
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!roll`: You cannot use this command until you have agreed to the rules.')
      return

    if not dice:
      await ctx.send('`!roll`: You have not specified the dice to roll.')
      return

    dice_available = CONFIG['Dice']
    args = dice.split('d')

    if len(args) != 2:
      await ctx.send('`!roll`: Please check your dice syntax.')
      return

    if not args[0].isdigit():
      await ctx.send('`!roll`: Please check your dice syntax. It must be of the format #d#, e.g. `!roll 3d6`.')
      return
    else:
      num_dice = int(args[0])    

    dice_and_mods = args[1]
    mod_type = 0

    if '+' in dice_and_mods or '-' in dice_and_mods:
      if '+' in dice_and_mods:
        dice_and_mods = dice_and_mods.split('+')
    
      elif '-' in dice_and_mods:
        dice_and_mods = dice_and_mods.split('-')
        mod_type = -1
      
      if not dice_and_mods[0].isdigit() or not dice_and_mods[1].isdigit():
        await ctx.send('`!roll`: Please check your dice and modifier syntax.')
        return
        
      else: 
        die_type = int(dice_and_mods[0])
        mod = int(dice_and_mods[1])
      
    else:		
      die_type = int(dice_and_mods)
      mod = 0
    
    if num_dice > 20:
      await ctx.send('`!roll`: You can roll a maximum of 20 dice.')
      return

    if die_type not in dice_available:
      dice_output = ['d{}'.format(die) for die in dice_available]

      await ctx.send('`!roll`: Dice must be one of: ' + ', '.join(dice_output))
      return

    if num_dice < 1:
      await ctx.send('`!roll`: The first number must be >= 1.')
      return

    roll_total = 0
    rolls    = []

    for i in range(num_dice):
      roll = random.randint(1, die_type)
      rolls.append(roll)
      roll_total += roll
    
    if mod_type == -1:
      total = roll_total - mod
    else:
      total = roll_total + mod

    await ctx.send('{} rolls {} and gets... {}!\n\nRolls: {}\nRaw: {}\nMod: {}{}'.format(ctx.author.mention, dice, total, rolls, roll_total, '-' if mod_type == -1 else '+', mod))


  @commands.command()
  async def whois(self, ctx, role_or_course):
    """Look up who is in a course or role.

    Args:
      role_or_course (String)
        The role or course from which to list current members.

    Returns:
      None
    """
    if not user_has_role(ctx.author, CONFIG['ConfirmedRole']):
      await ctx.send('`!whois`: You cannot use this command until you have agreed to the rules.')
      return

    target_role = match_role(ctx.guild, role_or_course)

    if not target_role:
      await ctx.send('`!whois`: The role {} could not be found.'.format(role_or_course))
      return

    role_is_gamedev = target_role.name in CONFIG['Roles']
    role_is_course = target_role.name in CONFIG['CourseRoles']

    if not role_is_gamedev and not role_is_course:
      await ctx.send('`!whois`: This role is not eligible for lookup.')
      return

    matches = []

    for member in ctx.guild.members:
      if target_role in member.roles:
        matches.append(member)

    match_string = ''

    for member in matches:
      match_string += '\n * {}'.format(member.display_name)

    await ctx.send('`!whois`: The members who are in {} are: {}'.format(
                                target_role.name, match_string))


def setup(bot):
  bot.add_cog(User(bot))
