from redbot.core import commands
from .core import TicketsCore

BaseCog = getattr(commands, "Cog", object)

class Tickets(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.core = TicketsCore(bot)

    @commands.group(name='ticket')
    async def ticket(self, context):
        '''
        Tickets!
        '''

    @ticket.command(name='new')
    async def ticket_new(self, context):
        '''
        Create a new ticket
        '''
        if context.invoked_subcommand is None:
            message = await self.core.create_ticket(context)
            if message:
                await context.send(message)

    @ticket.command(name='update')
    async def ticket_update(self, context, *, status: str):
        '''
        Update the status of a ticket
        '''
        await self.core.update_ticket(context, status)

    @ticket.command(name='close')
    async def ticket_close(self, context):
        '''
        Close a ticket, must be run in the ticket channel you want to close
        '''
        await self.core.close_ticket(context)

    @ticket.group(name='set')
    @commands.has_permissions(administrator=True)
    async def ticket_set(self, context):
        '''
        Settings
        '''

    @ticket_set.command(name='purge')
    async def ticket_set_purge(self, context):
        '''
        Delete all closed tickets
        '''
        message = await self.core.purge_tickets(context)
        await context.send(message)

    @ticket_set.command(name='message')
    @commands.has_permissions(administrator=True)
    async def ticket_set_message(self, context, *, message: str):
        '''
        Set the default message when a new ticket has been created (markdown safe)
        '''
        message = await self.core.set_default_message_ticket_channel(context, message)
        await context.send(message)

    @ticket_set.command(name='setup')
    async def ticket_setup(self, context):
        '''
        Automatic setup, will create two categories for open and closed tickets, and a ticket role for people to be able to manage tickets.
        '''
        message = await self.core.automatic_setup(context)
        await context.send(message)
