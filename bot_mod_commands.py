import discord
from discord.ext import commands
from bot_config import CONFIG
from bot_database import conn, cursor, create_db_user, get_db_user
from datetime import datetime
from bot_utility import is_admin, is_mod, find_channel, \
                        find_role, send_notification, user_has_role


class Mod():
  def __init__(self, bot):
    self.bot = bot


  @commands.command()
  async def cap(self, ctx, mention, *, reason='N/A'):
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
        await ctx.send('`!cap`: {} is already capped!'.format(target_user.display_name))

      else:
        await target_user.add_roles(cap_role)
        await ctx.send('WEE WOO WEE WOO')
        await target_user.send('You have been dunce capped for violating a rule. While you are ' +
                               'dunce capped, you will not be able to send messages, but you will ' +
                               'be able to add reactions to other users\' messages. The offending ' +
                               'violation must be remediated, and your dunce cap will be removed ' +
                               'after a certain amount of time.')
        await staff_channel.send('{} has been dunce capped by {} for {}!'.format(
                                                                            target_user.mention,
                                                                            ctx.author.mention,
                                                                            reason))
        await notifications_channel.send('{} has been dunce capped by {}!'.format(
                                                                            target_user.display_name,
                                                                            ctx.author.display_name))
        
        user = get_db_user(conn, cursor, target_user)
        
        if not user:        
          cmd = '''INSERT INTO users 
                    VALUES (?, ?, 0, 0, 1)'''
          params = (target_user.id, target_user.name)
        
        else:
          cmd = '''UPDATE users 
                    SET times_capped = ?
                    WHERE id == ?'''
          params = (user[4] + 1, target_user.id)

        cursor.execute(cmd, params)
        conn.commit()
        
        cmd = '''INSERT INTO notes
                  VALUES (NULL, ?, ?, ?, ?, ?)'''
        params = (datetime.now(), target_user.id, target_user.name, 'cap', reason)
        cursor.execute(cmd, params)
        conn.commit()


    # Non-moderator uses !cap
    else:
      await ctx.send('`!cap`: You are not worthy to wield the mighty cap.')


    @commands.command()
    async def setname(self, ctx, user, *, name):
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
        old_name = target_user.display_name
        await target_user.edit(nick=name)
        await send_notification(ctx.guild, "{} updated {}'s nickname to {}!".format(ctx.author.display_name, old_name, name))

      else:
        await ctx.send("`!setname`: You do not have the privileges to use this command.")


  @commands.command()
  async def uncap(self, ctx, mention):
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
        await ctx.send('Are you blind, {}? You can\'t uncap {} '.format(ctx.author.mention, target_user.display_name) +
                       'if they\'re not wearing the Dunce Cap!')

      else:
        await target_user.remove_roles(cap_role)
        await target_user.send('Your dunce cap is lifted.')
        await staff_channel.send('{} has been uncapped by {}!'.format(
                                                                  target_user.mention,
                                                                  ctx.author.mention))
        await notifications_channel.send('{} has been uncapped by {}!'.format(
                                                                  target_user.display_name,
                                                                  ctx.author.display_name))
        return

    else:

      # Non-moderator attempts to use !uncap
      if not user_has_role(target_user, CONFIG['CapRole']):
        await ctx.send('`!uncap`: How can you uncap someone who isn\'t ' +
                       'wearing a cap to begin with? Reconsider your life choices.')
      else:
        await ctx.send('`!uncap`: You are not strong enough to discard the mighty cap.')


def setup(bot):
  bot.add_cog(Mod(bot))