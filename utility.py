from config import CONFIG

admin_role_identifier = CONFIG['AdminRole']
mod_role_identifier = CONFIG['ModRole']

def is_admin(ctx):
  """Check whether the author of a message is an admin.

  Args:
    ctx (Context)
      The Context of the message which is being examined.

  Returns:
    is_admin (Bool)
    True if the message author has the admin role.
  """
  return user_has_role(ctx.author, admin_role_identifier)


def is_mod(ctx):
  """Check whether the author of a message is a moderator.

  Args:
    ctx (Context)
      The Context of the message which is being examined.

  Returns:
    is_mod (Bool)
    True if the message author has the mod role.
  """
  return user_has_role(ctx.author, mod_role_identifier)


def find_channel(guild, channel_string):
  """Utility function: given a channel string, find the corresponding
  Channel if it exists.

  Args:
    guild (Guild)
      The Guild to search for channels.

    channel_string (String)
      The string that should be part of the Channel's name.

  Returns:
    result
    Channel object if found, otherwise None.
  """
  for channel in guild.channels:
    if channel_string in channel.name:
      return channel

  return None


def find_role(guild, role_string):
  """Utility function: given a role string, find the corresponding
  Role if it exists.

  Args:
    guild (Guild)
      The Guild to search for roles.

    role_string (String)
      The string that should be part of the Role's name.

  Returns:
    result
    Role object if found, otherwise None.
  """
  for role in guild.roles:
    if role_string in role.name:
      return role

  return None


def user_has_role(user, role_string):
  """Utility function: given a user and a role string, check if that
  user has a role containing that role string.

  Args:
    user (Member)
      The user being examined for the role.

    role_string (String)
      The string being checked in the user's roles.

  Returns:
    has_role (Bool)
    True if the user has a role containing the role string.
  """
  has_role = False

  for role in user.roles:
    if role_string in role.name:
      has_role = True
      break

  return has_role