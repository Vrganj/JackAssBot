import logging
import subprocess

from discord.ext import commands
from discord import Activity


class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(
        aliases=('goodbye', 'die')
    )
    async def logout(self, ctx):
        """
        Disables bot.
        """
        await ctx.send('See ya bitch!')
        await self.client.logout()

    @commands.command()
    async def git(self, ctx, *process):
        """
        Powerfull git commands to manage the bot.
        """
        await ctx.trigger_typing()
        try:
            output = subprocess.check_output(
                ('git', *process)
            ).decode()
        except Exception as e:
            raise commands.BadArgument(f'```{e}```')
        if len(output) > 2000:
            output = f'{output[:2000]}...'
        await ctx.embed(
            title='Git',
            description=f'```git\n{output}\n```',
            color=0xeb6200
        )

    @commands.command(
        name='status',
        aliases=('activity',)
    )
    async def client_status(self, ctx, status=None, *, name=None):
        """
        Changes bot's status.
        """
        activities = ('playing', 'streaming', 'listening', 'watching')
        url = 'https://www.twitch.tv/twitchrivals'
        if not status:
            await self.client.change_presence(activity=None)
            return
        if status.lower() not in activities:
            raise commands.BadArgument(f'Invalid activity "{status}"')
        await self.client.change_presence(
            activity=Activity(
                name=name if name else 'some shit',
                url=url if status == activities[1] else None,
                type=activities.index(status)
            )
        )

    @commands.group(
        name='reload',
        invoke_without_command=True
    )
    async def _reload(self, ctx, *, ext):
        """
        Reloads an extension.
        """
        ext = f'cogs.{ext}'
        try:
            self.client.reload_extension(ext)
        except commands.ExtensionError as e:
            logging.exception(f'{ext}:')
            raise commands.BadArgument(str(e))
        await ctx.embed(
            title='Reload',
            description=f'```ini\n[{ext}] reloaded```'
        )

    @_reload.command(
        name='all'
    )
    async def reload_all(self, ctx):
        """
        Reloads all extensions.
        """
        ext = list(self.client.extensions)
        output = []
        for cog in ext:
            try:
                self.client.reload_extension(cog)
                output.append(f'[{cog}] reloaded')
            except commands.ExtensionError:
                output.append(f'{cog} failed to reload')
                logging.exception(f'{ext}:')
        output = '\n'.join(output)
        await ctx.embed(
            title='Reload',
            description=f'```ini\n{output}\n```'
        )

    @commands.group(
        name='load',
        invoke_without_command=True
    )
    async def _load(self, ctx, *, ext):
        """
        Loads a specified extension.
        """
        ext = f'cogs.{ext}'
        if ext not in self.client.module_list:
            raise commands.BadArgument("Extension doesn't exist.")
        try:
            self.client.load_extension(ext)
        except commands.ExtensionError as e:
            logging.exception(f'{ext}:')
            raise commands.BadArgument(str(e))
        await ctx.embed(
            title='Load',
            description=f'```ini\n[{ext}] loaded\n```'
        )

    @_load.command(
        name='all'
    )
    async def load_all(self, ctx):
        """
        Loads all extensions.
        """
        output = await self.client.load_modules()
        await ctx.embed(
            title='Load',
            description=f'```ini\n{output}\n```'
        )

    @commands.group(
        name='unload',
        invoke_without_command=True
    )
    async def _unload(self, ctx, *, ext):
        """
        Unloads a specified extension.
        """
        ext = f'cogs.{ext}'
        if ext not in list(self.client.extensions):
            raise commands.BadArgument('Extension not loaded.')
        try:
            self.client.unload_extension(ext)
        except commands.ExtensionError as e:
            logging.exception(f'{ext} failed to unload')
            raise commands.BadArgument(str(e))
        await ctx.embed(
            title='Unload',
            description=f'```ini\n[{ext}] unloaded\n```'
        )

    @_unload.command(
        name='all'
    )
    async def unload_all(self, ctx):
        """
        Unloads all extensions.
        """
        ext = list(self.client.extensions)
        ext.remove(__name__)
        output = []
        for cog in ext:
            try:
                self.client.unload_extension(cog)
                output.append(f'[{cog}] unloaded')
            except commands.ExtensionError:
                output.append(f'[{cog}] failed to unload')
                logging.exception(f'{ext}:')
        output = '\n'.join(output)
        await ctx.embed(
            title='Unload',
            description=f'```ini\n{output}\n```'
        )

    @commands.command(
        name='guilds'
    )
    async def list_guilds(self, ctx):
        bot_guilds = '\n'.join(
            f'Name: {i.name}, Id: {i.id}'
            for i in self.client.guilds
        )
        await ctx.send(f'```{bot_guilds}```')


def setup(client):
    client.add_cog(Owner(client))
