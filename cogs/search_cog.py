import boto3.exceptions
import botocore.exceptions
from discord.ext import commands
from discord import app_commands
import discord
from discord import ui
import boto3
import botocore

class Event():
    def __init__(self, name, date, time, image_url):
        self.name = name
        self.date = date
        self.time = time
        self.image_url = image_url

class Club():
    def __init__(self, name, image_url):
        self.name = name
        self.image_url = image_url

class EventView(discord.ui.View):
    def __init__(self, results: list[Event]):
        super().__init__()
        self.results = results
        self.current_result = 0
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def prev_result_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_result > 0:
            self.current_result -= 1
            embed = create_event_embed(self.results[self.current_result], self.current_result + 1)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(ephemeral=True, content="No more results", delete_after=3)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next_result_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_result < len(self.results) - 1:
            self.current_result += 1
            embed = create_event_embed(self.results[self.current_result], self.current_result + 1)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(ephemeral=True, content="No more results", delete_after=3)
    
    #TODO: engage button
    # @discord.ui.button(label="Engage", style=discord.ButtonStyle.link)
    # async def engage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.send_message("Not implemented!")

class ClubView(discord.ui.View):
    def __init__(self, results: list[Club]):
        super().__init__()
        self.results = results
        self.current_result = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def prev_result_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_result > 0:
            self.current_result -= 1
            embed = create_club_embed(self.results[self.current_result], self.current_result + 1)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(ephemeral=True, content="No more results", delete_after=3)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next_result_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_result < len(self.results) - 1:
            self.current_result += 1
            embed = create_club_embed(self.results[self.current_result], self.current_result + 1)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(ephemeral=True, content="No more results", delete_after=3)


class SearchCog(commands.GroupCog, name="search", description="Search for clubs or events"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="club", description="Search for a club")
    async def search_club_handler(self, interaction: discord.Interaction, name: str) -> None:
        club_list = await self.get_clubs()
        embed = create_club_embed(club_list[0], 1)
        view = ClubView(results=club_list)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="event", description="Search for an event")
    async def search_event_handler(self, interaction: discord.Interaction, name: str) -> None:
        event_list = await self.get_events()
        embed = create_event_embed(event_list[0], 1)
        view = EventView(results=event_list)
        await interaction.response.send_message(embed=embed, view=view)
    
    async def get_events(self) -> list[Event]:
        events = []
        # this is where we would actually fetch events from ddb
        for i in range(5):
            events.append(Event(name=f"event{i}", date="1/2/25", time="9:00PM", image_url="https://se-images.campuslabs.com/clink/images/3f63b266-ed37-4070-8678-6aae47084b5008aa61af-5d5d-499e-8c9e-7ed5ce127541.jpeg?preset=med-sq"))
        return events
    
    async def get_clubs(self) -> list[Club]:
        clubs = []
        #this is where we would actually fetch clubs from ddb
        ddb = boto3.resource('dynamodb')
        cf = boto3.client('cloudformation')

        resource = None
        table = None
        items = None

        try:
            resource = cf.describe_stack_resource(StackName="ImmersionStack", LogicalResourceId="ImmersionOrganizationTable")
        except botocore.exceptions.ClientError as e:
            print("ERROR! SearchCog::get_clubs():", e)
        else:
            try:
                table = ddb.Table(resource.StackResourceDetail.PhysicalResourceId)
            except Exception as e:
                print("ERROR! SearchCog::get_clubs() raised an Exception:", e)
            else:
                items = table.scan()
        print("Stack resources:", items)




        
        for i in range(5):
            clubs.append(Club(name="Cloud Computing Club", image_url="https://se-images.campuslabs.com/clink/images/3f63b266-ed37-4070-8678-6aae47084b5008aa61af-5d5d-499e-8c9e-7ed5ce127541.jpeg?preset=med-sq"))
        return clubs

async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCog(bot))

def create_event_embed(event: Event, idx: int) -> discord.Embed:
    embed = discord.Embed(title=f"Search result {idx}:")
    embed.add_field(name="Name", value=event.name)
    embed.add_field(name="Date", value=event.date)
    embed.add_field(name="Time", value=event.time)
    embed.set_image(url=event.image_url)
    return embed

def create_club_embed(club: Club, idx: int) -> discord.Embed:
    embed = discord.Embed(title=f"Search result {idx}:")
    embed.add_field(name="Name", value=club.name)
    embed.set_image(url=club.image_url)
    return embed