import pickle
from bot_config import CONFIG

admin_role_identifier = CONFIG['AdminRole']
mod_role_identifier = CONFIG['ModRole']

def is_admin(user):
  """Check whether a user is an admin.

  Args:
    user (Member)
      The user to check for admin privileges.

  Returns:
    is_admin (Bool)
    True if the message author has the admin role.
  """
  return user_has_role(user, admin_role_identifier)


def is_mod(user):
  """Check whether a user is a moderator.

  Args:
    user (Member)
      The user to check for mod privileges.

  Returns:
    is_mod (Bool)
    True if the message author has the mod role.
  """
  return user_has_role(user, mod_role_identifier)


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
  

def match_role(guild, role_string):
  """Utility function: given a role string, find the exact corresponding
  Role if it exists.

  Args:
    guild (Guild)
      The Guild to search for roles.

    role_string (String)
      The string that should be exactly the Role's name.

  Returns:
    result
    Role object if found, otherwise None.
  """
  for role in guild.roles:
    if role_string == role.name:
      return role

  return None
  

def load_data(file):
  """Loads the persistent data for the bot to use.
  
  Args:
    file (File)
      The pickle file to open.
    
  Returns:
    data (Dict) or None
    The Python object reconstructed from the pickle file.
  """
  try:
    with open(CONFIG['DATAFILE'], 'r+') as f:
      data = pickle.load(f)
  
  except:
    print('File could not be found or loaded.')
    return None
  
  return data


def save_data(file):
  """Write out the persistent data for the bot.
  
  Args:
    file (File)
      The pickle file to save.
    
  Returns:
    None
  """
  try:
    with open(CONFIG['DATAFILE'], 'w+') as f:
      pickle.dump(CONFIG['DATA'], f, protocol=4)
  
  except Exception as e:
    print('File could not be saved. {}'.format(e))
  

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

async def send_notification(guild, message):
  """Send a message to the notifications channel.

  Args:
    message (String)
      The message to send to the notifications channel.

  Returns:
    None
  """
  notifications_channel = find_channel(guild, CONFIG['NotificationsChannel'])
  await notifications_channel.send(message)
