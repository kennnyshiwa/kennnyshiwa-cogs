from redbot.core import Config
from datetime import datetime
import discord
import random


class SafeMember:
    def __init__(self, member: discord.Member):
        self.name = member.name
        self.mention = member.mention

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        return ""


class TicketsCore:
    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=2134287593)
        default_guild = {
            "category": None,
            "closed_category": None,
            "ticket_role": None,
            "default_message_ticket_channel": None,
            "sessions": {},
        }
        self.config.register_guild(**default_guild)

        self.ticket_info_format = "\n\n**[{datetime}]** [{author}]\n{information}"

    async def create_ticket(self, context):
        guild = context.guild
        author = context.author

        ticket_role = [
            role
            for role in guild.roles
            if await self.config.guild(guild).ticket_role() == role.id
        ]

        if ticket_role:
            ticket_role = ticket_role[0]
        category_channel = await self.config.guild(guild).category()
        default_message_ticket_channel = await self.config.guild(
            guild
        ).default_message_ticket_channel()

        if category_channel and category_channel in [
            category.id for category in guild.categories
        ]:
            n1 = 10 ** 10
            n2 = n1 * 10 - 1
            ticket_id = int(random.randint(n1, n2))
            ticket_channel = await guild.create_text_channel(
                "{}-{}".format(author.display_name, ticket_id),
                category=self.bot.get_channel(category_channel),
            )

            await ticket_channel.set_permissions(
                author, read_messages=True, send_messages=True
            )
            await ticket_channel.set_permissions(
                guild.me, read_messages=True, send_messages=True, manage_channels=True
            )

            await ticket_channel.edit(
                topic=self.ticket_info_format.format(
                    ticket=ticket_id,
                    datetime=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),
                    author=author.display_name,
                    information="Ticket opened",
                )
            )

            if default_message_ticket_channel:
                try:
                    await ticket_channel.send(
                        default_message_ticket_channel.format(
                            member=SafeMember(author),
                            channel=ticket_channel,
                            origin=context.channel,
                            ticket_role=ticket_role,
                        )
                    )
                except:
                    return "Oops there has been an unexpected error with your new ticket message. Please contact the bot owner for assistance"

            async with self.config.guild(guild).sessions() as session:
                session.update({ticket_channel.id: author.id})

        else:
            return "Naughty! You need to run the setup first."

    async def update_ticket(self, context, status):
        try:
            await context.message.delete()
        except discord.Forbidden:
            pass

        guild = context.guild
        channel = context.channel
        author = context.author

        sessions = await self.config.guild(guild).sessions()

        if str(channel.id) in sessions and await self.config.guild(
            guild
        ).ticket_role() in [role.id for role in author.roles]:

            ticket_id = str(channel.name).split("-")[1]
            await channel.edit(
                topic=channel.topic
                + self.ticket_info_format.format(
                    ticket=ticket_id,
                    datetime=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),
                    author=author.display_name,
                    information=status,
                )
            )

    async def close_ticket(self, context):
        try:
            await context.message.delete()
        except discord.Forbidden:
            pass

        guild = context.guild
        channel = context.channel
        author = context.author

        sessions = await self.config.guild(guild).sessions()

        if str(channel.id) not in sessions:
            return await channel.send(
                "Make sure you are doing this within the ticket channel that you want to close."
            )
        if await self.config.guild(guild).ticket_role() not in [
            role.id for role in author.roles
        ]:
            return await channel.send(
                "You do not have the proper role to manage tickets"
            )
        else:
            member = guild.get_member(sessions[str(channel.id)])
            ticket_id = str(channel.name).split("-")[1]

            closed_category = await self.config.guild(guild).closed_category()
            closed_category = self.bot.get_channel(closed_category)

            await channel.set_permissions(
                member, read_messages=True, send_messages=False
            )
            await channel.edit(
                category=closed_category,
                topic=channel.topic
                + self.ticket_info_format.format(
                    ticket=ticket_id,
                    datetime=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),
                    author=author.display_name,
                    information="Ticket closed",
                ),
            )

            async with self.config.guild(guild).sessions() as session:
                session.pop(channel.id, None)

    async def purge_tickets(self, context):
        try:
            guild = context.guild
            closed_channels = [
                channel
                for channel in guild.channels
                if channel.category_id
                == await self.config.guild(guild).closed_category()
            ]
            for channel in closed_channels:
                await channel.delete()

            return "All closed tickets removed!"
        except discord.Forbidden:
            return "I need permissions to manage channels."

    async def set_default_message_ticket_channel(self, context, message):
        guild = context.guild

        await self.config.guild(guild).default_message_ticket_channel.set(message)

        return "Your default message has been set."

    async def automatic_setup(self, context):
        guild = context.guild

        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False, read_messages=False
                ),
            }

            category_channel = await guild.create_category(
                "Tickets", overwrites=overwrites
            )
            closed_category_channel = await guild.create_category(
                "Closed Tickets", overwrites=overwrites
            )

            ticket_role = await guild.create_role(name="Ticket")

            await category_channel.set_permissions(
                ticket_role, read_messages=True, send_messages=True
            )
            await closed_category_channel.set_permissions(
                ticket_role, read_messages=True, send_messages=True
            )

            await self.config.guild(guild).category.set(category_channel.id)
            await self.config.guild(guild).closed_category.set(
                closed_category_channel.id
            )
            await self.config.guild(guild).ticket_role.set(ticket_role.id)

            return ":tada: Fabulous! You're all done! Now add the `Ticket` role to anyone who you deem good enough to handle tickets. And if you care, you can change the name of the role and category if you _really_ want to."
        except discord.Forbidden:
            return "That didn't go well... I need permissions to manage channels and manage roles. :rolling_eyes:"
