import discord
from discord.ext import commands
from bot_config import CONFIG
from bot_secure import watch
from bot_utility import is_admin, is_mod, find_channel, \
                        find_role, send_notification, user_has_role


class Admin():
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def echo(ctx, *, message):
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
  async def monitor(ctx, mention):
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
        cap(ctx, ctx.author)
        await ctx.send("`!monitor`: This is an admin-only command. {} has been capped for trying to use it.".format(ctx.author.display_name))

      return

    if len(ctx.message.mentions) == 0:
      await ctx.send("`!monitor`: The user to be monitored must be @-mentioned as the first argument.")
      return

    watch(ctx, target_user)
    await ctx.send("`!monitor`: {} has been placed on watch.".format(target_user.display_name))


def setup(bot):
  bot.add_cog(Admin(bot))