import discord, time, requests, schedule, ezgmail, csv
from datetime import datetime, timedelta, date
from discord.ext import commands, tasks
import pandas as pd
from bs4 import BeautifulSoup
#Bot Key Prefix
client = commands.Bot(command_prefix="$")
#Removes the original help command in lieu of the one I made
client.remove_command('help')
#Extra variables i need
global todays_must
global master_must
todays_must = {}
master_must = {}
@client.event
#Defines EVA's Reddit Status
async def on_ready():
    test.start()
    await client.change_presence(activity=discord.Game(name='Cryostasis: Type $help' ,emoji=':snowflake:'))
@client.event
async def on_message(message):
    message.content = message.content.lower()
    #Start of dirty code ===========================================
    bullshit = ["shipmate",
    "tradition",
    "discuss",
    "hooyah",
    "understand",
    "curious",
    "semantics"
    ]
    if message.author == client.user:
        return
    elif message.content in bullshit and "7554" in str(message.author):
        await message.delete()
    #end dirty code ===================================================

    await client.process_commands(message) #This is needed to enable commands an events

@client.command()
async def help(ctx):
    embed=discord.Embed(title="Evangelion Unit-01", description='Evangelion Unit-01 (初号機[?], Shogōki) is the first non-prototype Evangelion unit, and is referred to as the Test Type. It houses the soul of Shinji\'s mother, Yui Ikari.', color=0x765898)
    embed.add_field(name='Type $muster', value='This command is used to take muster please type \"$muster help\" for more', inline=False)
    embed.add_field(name='Tasks', value='The bot also scrapes the Navy Page for Navadmins every morning and emails muster to Dept. Leadership', inline=False)

    await ctx.send(embed=embed)

@client.command()
async def muster(ctx, arg1):
    arg1 = arg1.lower()
    excuses = {
        "wl":"WhiteLaw",
        "pt/wl":"WhiteLaw/PT",
        "op":"OP",
        "speclib":"Speclib",
        "rom":"ROM",
        "appointment1":"Appointment(No Show)",
        "appointment2":"Appointment (Will be back)",
        "leave": "On Leave",
        "muster": "Mustered with Muster PO"
    }
    muster_aux_commands = ["help", "check"]
    person = ctx.message.author.nick
    if arg1 == "help":
        await ctx.send(f"""
        Hello {person} if youd like to report your muster status please use \"$muster <REASON> \" with one of the following options as your arguments:
        **WL**: Going straight to Whitelaw at the beginning of the work day.
        **PT/WL**: Going to Whitelaw after PT
        **OP**: You have an op today, will be in an hour before the op
        **Speclib**: Speclib
        **ROM**: ROM
        **Appointment1**: Appointment (Will not be at work)
        **Appointment2**: Appointment (Will be at work afterwards)
        **On Leave**: On Leave

        If you are the Muster PO you can check muster by typing \"$muster check\"
        """)
    elif arg1 == "check":
        df1 = pd.DataFrame(master_must[str(date.today())].items(), columns=["name", "status"])
        await ctx.channel.send(df1.to_string(index=False))


    if arg1 not in excuses and arg1 not in muster_aux_commands:
        await ctx.send("Please use one of the valid excuses, or hit up the muster person directly")
    elif arg1 in excuses:
        todays_must[person]= excuses[arg1]
        master_must[str(date.today())] = todays_must
        await ctx.channel.send(f"thanks, gotcha {person}")
#@client.command()
#async def test(ctx):
#    await ctx.send(ctx.author)
@tasks.loop(minutes=1)
async def test():
    if datetime.now().strftime("%H:%M") == "00:00":
        todays_must = {}
    if datetime.now().strftime("%H:%M") == "07:00":
        #Scrape Navadmin page
        today = date.today()
        channel = client.get_channel(776197972865056778)
        URL = f'https://www.public.navy.mil/bupers-npc/reference/messages/NAVADMINS/Pages/NAVADMIN{today.year}.aspx'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        #Finds the elements of the list that match the date
        row = soup.find_all(class_="ms-rteFontSize-1")
        for item in row:
            row_upp = item.find_all('strong')
            if len(row_upp) == 3 and row_upp[2].text == str(datetime.today().strftime("%m/%d/%Y")):
                navadmin_message = row_upp[0].text
                navadmin_title = row_upp[1].text
                navadmin_link = f'https://www.public.navy.mil/{row_upp[1].find("a")["href"]}'
                navadmin_date = row_upp[2].text
                cfile = open('navadmin.csv', mode='a+')
                csv_writer = csv.writer(cfile)
                csv_reader = csv.reader(cfile)
                cfile.seek(0)
                header = next(csv_reader)
                ddate = next(cfile)
                ddate = ddate.split(",")[3][:10]
                if ddate == navadmin_date:
                    pass
                else:
                    csv_writer.writerow([navadmin_message,navadmin_title,navadmin_link,navadmin_date])
                    await channel.send(
                        f"""
                        Hey guys, New NAVADMIN:
                        Heres the message ID: {navadmin_message}
                        Heres the Navadmin Title: {navadmin_title}
                        Heres the Navadmin Link: {navadmin_link}
                        Heres the Date: {navadmin_date} 
                    """)
    if datetime.now().strftime("%H:%M") == "08:42":
        if str(datetime.today().strftime("%A")) not in ['Saturday', 'Sunday']:
            date_var = str(date.today())
            df = pd.DataFrame(master_must[date_var].items(), columns=["name", "status"])
            df.to_csv(f"{date_var}.csv", index=False)
            channel = client.get_channel(776197972865056778)
            ezgmail.send('thaddeuskoenig@gmail.com', f'Muster for {date_var}', f'Good Moorning,\nAttached I have included the muster for {date_var}, if there are any questions please inform the muster PO', [f"{date.today()}.csv"])
            await channel.send('Muster Sent')
            #https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-send-a-message-to-a-specific-channel


    #await self.client.send("yes")
#https://www.programcreek.com/python/example/127968/discord.ext.tasks.loop
#https://www.reddit.com/r/Discord_Bots/comments/g76ax6/discordpy_schedule_daily_tasks/foftglt/

client.run('Nzc2MTMwNTEzOTExNDE0ODI0.X6wZ3g.nkMmrnIE8ohGJP0V5cnG0my7HFQ')

