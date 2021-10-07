import discord, requests, sqlite3, datetime, eva_vars, tabulate, ezgmail
import pandas as pd
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

#Bot Key Prefix
client = commands.Bot(command_prefix="$")
#Removes the original help command in lieu of the one I made
client.remove_command('help')

def create_connection(sql_logic=None, dframe_logic=None):
    #sql_logic is needed for regular sql queries but dframe_logic id needed to return dataframe
    conn = None
    try:
        conn = sqlite3.connect("eva.db")
    except sqlite3.Error as e:
        print(e)
    finally: 
        if sql_logic != None and dframe_logic == None:
            cursor = conn.cursor()
            sql_var = cursor.execute(sql_logic) 
            conn.commit() # writes to db
            return sql_var
        if sql_logic == None and dframe_logic != None:
            df = pd.read_sql_query(dframe_logic, conn)
            conn.commit()
            return df
        conn.close()

@client.event
async def on_ready(): # When the bot boots    
    test.start() #Needed to start tasks upon start 
    await client.change_presence(activity=discord.Game(name='Cryostasis: Type $help' ,emoji=':snowflake:')) #Setting Status Variable 

@client.event
async def on_message(message): #Waits on Messages 
    person = message.author.nick
    muster_channel = client.get_channel(775027173022498828) #Specify discord channel
    message.content = message.content.lower()
    if message.author == client.user:
        return
    #i had issues with it accidentally taking commands as regular messages
    if message.channel == muster_channel and not message.content.startswith("$"):
        name = message.author.nick #will pull discord nickname
        muster_date = str(datetime.date.today().strftime('%m/%d/%Y')) #puts it in the M/D/Y format
        status =  message.content
        #input muster status into the database
        sql_logic = f"INSERT INTO muster(name, muster_date, status) VALUES(\'{name}\', \'{muster_date}\', \'{status}\')"
        create_connection(sql_logic)
    else: 
        pass
    await client.process_commands(message) #This is needed to enable commands an events

@client.command()
#Help Embed
async def help(ctx):
    embed=discord.Embed(title="Evangelion Unit-01", url="https://evangelion.fandom.com/wiki/Evangelion_Unit-01", description="Evangelion Unit-01 (初号機[?], Shogōki) is the first non-prototype Evangelion unit, and is referred to as the Test Type. It houses the soul of Shinji's mother, Yui Ikari.", color=0x765898)
    embed.set_author(name="Thadvillian", url="https://github.com/adminprivileges", icon_url="https://factmag-images.s3.amazonaws.com/wp-content/uploads/2015/07/Madvillain240715.jpg")
    embed.set_thumbnail(url="https://assets3.thrillist.com/v1/image/2828794/792x536/scale;jpeg_quality=60;progressive.jpg")
    embed.add_field(name='Type $muster', value='This command is used to take muster please type \"$muster help\" for more', inline=False)
    embed.add_field(name='Tasks', value='The bot also scrapes the Navy Page for Navadmins every morning and emails muster to Dept. Leadership', inline=False)
    await ctx.send(embed=embed)

@client.command()
async def muster(ctx, arg1="help"):
    arg1 = arg1.lower()
    #variable for server nickname
    person = ctx.message.author.nick
    if arg1 == "help":
        embed=discord.Embed(title="Evangelion Unit-01", url="https://evangelion.fandom.com/wiki/Evangelion_Unit-01", description=f"Hello {person} if you'd like to report your muster status please use the muster chat and your status will be automatically recorded and emailed at 0700.", color=0x765898)
        embed.set_author(name="Thadvillian", url="https://github.com/adminprivileges", icon_url="https://factmag-images.s3.amazonaws.com/wp-content/uploads/2015/07/Madvillain240715.jpg")
        embed.set_thumbnail(url="https://assets3.thrillist.com/v1/image/2828794/792x536/scale;jpeg_quality=60;progressive.jpg")
        embed.add_field(name='Type $muster check', value='If you are the Muster PO you can use this command to check muster', inline=False)
        await ctx.send(embed=embed)
    #Will query the database for todays muster status and send a table in discord
    elif arg1 == "check":
        dframe_logic = f"SELECT * FROM muster WHERE muster_date = \'{str(datetime.date.today().strftime('%m/%d/%Y'))}\'"
        print(dframe_logic)
        df = create_connection(None, dframe_logic)
        await ctx.send(tabulate.tabulate(df, headers = 'keys', tablefmt = 'psql')) #makes it look good

@tasks.loop(minutes=1)
async def test():
    #Loop goes once a min to look for any specified task times
    print(datetime.datetime.now().strftime("%H:%M"))
    if datetime.datetime.now().strftime("%H:%M") == "15:53":
        #Make sure its not a weekend
        if str(datetime.datetime.today().strftime("%A")) not in ['Saturday', 'Sunday']:
            date_var = str(datetime.date.today())
            #pulls dataframe from db and then converts it to CSV
            dframe_logic = f"SELECT * FROM muster WHERE muster_date = \'{str(datetime.date.today().strftime('%m/%d/%Y'))}\'"
            df = create_connection(None, dframe_logic)
            df.to_csv(f"{date_var}.csv", index=False)
            channel = client.get_channel(775027106823405588)
            #Fields are ("Recipient", "Subject", "Body", ["Attachment"], cc="recipient", bcc="person1, person2")
            ezgmail.send(f'{eva_vars.muster_emails}', f'Muster for {date_var}', f'Good Moorning,\nAttached I have included the muster for {date_var}, if there are any questions please inform the muster PO', [f"{date_var}.csv"])
            await channel.send('Muster Sent') #ACK
        
    elif datetime.datetime.now().strftime("%H:%M") == "05:00":
        #Scrape Navadmin page
        #today = datetime.date.today()
        channel = client.get_channel(775027173022498828) #Specify discord channel
        #The navy is big dumb and changed the URL structure in 2021 so thats the only year it'll work for
        URL = f'https://www.mynavyhr.navy.mil/References/Messages/NAVADMIN-{datetime.date.today().year}'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        nav_container = soup.find("div", {"id":"dnn_ctr40652_ContentPane"})
        rows = nav_container.find_all('tr')
        rows = rows[1:5]
        for row in rows:
            item = row.find_all("td")
            #print(item)
            message_id = item[0].text
            #i needed this check to specify the end of the NAVADMIN table, otherwise script returns IndexError
            if str(message_id) != f"000/{str(datetime.date.today().year)[2:]}":
                try:
                    admin_date = item[2].text
                    #if the navadmin date matches today
                    if str(admin_date) == str(datetime.date.today().strftime('%m/%d/%Y')):
                        title = item[1].text.strip()
                        #print(item)
                        link1 = row.find("a")["href"]
                        #print(link1)
                        link = f'https://www.mynavyhr.navy.mil/{link1}'
                        sql_logic = (f"INSERT INTO navadmin(message_id, title, admin_date, link) VALUES(\'{message_id}\', \'{title}\', \'{admin_date}\', \'{link}\')")
                        #print(sql_logic)
                        create_connection(sql_logic)
                        await channel.send(f"""Good morning @everyone theres a new Navadmin \nDate: {admin_date} \nTitle: {title}\nLink: {link} """)
                    else:
                        break
                except IndexError:
                    pass
            else:
                print("Done")
client.run(eva_vars.discord_key)
