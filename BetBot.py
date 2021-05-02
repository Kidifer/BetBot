# Importing stuff
import os, json, giphy_client
from dotenv import load_dotenv
from discord.ext import commands
from giphy_client.rest import ApiException

load_dotenv()

# Global variables
# When going to .exe, change BIDFILE, USERFILE, and COMMAND_PREFIX!!
TOKEN = os.getenv('DISCORD_TOKEN')
GIPHY = os.getenv('GIPHY_TOKEN')
BIDSFILE = 'BetBot\\BIDS.json'
USERFILE = 'BetBot\\USERS.json'
COMMAND_PREFIX = '?'

api_instance = giphy_client.DefaultApi()

# Creating Bot object
bot = commands.Bot(command_prefix=COMMAND_PREFIX)

# Function to pull stored values
def openClose(fName):
    # Inputs:
    #   fname:  File path containing dict
    # Outputs:  Dictionary contained in (fName)
    outs = {}
    try:
        with open(fName) as f:
            outs = json.load(f)
        f.close
    except:
        pass
    return outs

def search_gifs(query: str, num = 1, rate = 'g'):
    # Inputs:
    #   query:  String to be searched for gif
    #   num:    Number of strings returned
    #   rate:   Rating of gifs returned
    # Outputs:
    #   response.data[0].url:   Url of gif, just needs to be .send()'d as a string to output gif.
    try: 
        response = api_instance.gifs_search_get(GIPHY, query, limit = num, rating = rate)
        return response.data[0].url
    except ApiException as e:
        return "Exception when calling DefaultAPI -> gifs_search_get: %s\n" % e

def rewrite(file, var = {}):
    # Inputs:
    #   file:   File path containing dict to be rewritten
    #   var:    Dict that is being rewritten
    # Outputs:
    #   N/A
    f = open(file, 'r+')
    f.truncate(0)
    json.dump(var,f)
    f.close

def stringOut(headers: tuple, dic, *case):
    stringHeaders = '\t\t'.join(headers)
    body =''
    for key, value in dic.items():
        body += str((value[1] + '\t\t' + str(value[0]) + '\t\t' + key + '\n'))
    outString = '```' + str(stringHeaders + '\n' + body) + '```'
    return outString
# Notify when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected.')

# Register user
@bot.command(name='reg', help='Register your name. YOU ONLY GET ONE. Format: ``reg name')
async def reg(ctx, *name: str):
    # Allow names with spaces
    if len(name) > 1 :
        name = ' '.join(name)
    else:
        name = name[0]    

    global USERFILE
    
    users = openClose(USERFILE)

    # Check if user is in USERS, if not then add them
    if str(ctx.author.id) not in users:
        users[ctx.author.id]= name
        await ctx.send('User {0} registered as \'{1}\'.'.format(ctx.author.id, name))
    else:
        await ctx.send('No takesies backsies!! (You can''t register under a new name to prevent scamming the system.)')

    # Save USERS to USERS.json locally
    rewrite(USERFILE, users)

# User bidding
@bot.command(name='bid', help='Allows you fucks to place bids. Format: ``bid price game')
async def bid(ctx, bid: float, *game:str):
    global USERFILE, BIDSFILE

    bid = round(bid,2)  # Round to cents
    users = openClose(USERFILE)
    bids = openClose(BIDSFILE)

    # Allow names with spaces
    if len(game) > 1 :
        game = ' '.join(game)
    else:
        game = game[0]
    game = game.upper()  # Cast to upper case

    # Check if user is registered, rightfully insult them if not.
    if str(ctx.author.id) in users:
        if game not in bids:
            bids[game]=[bid, users[str(ctx.author.id)]]
            await ctx.message.add_reaction('👍')
            await ctx.message.add_reaction('🥇')
        # Make sure bid is larger than current bid
        elif bid > bids[game][0]:
            bids[game]=[bid, users[str(ctx.author.id)]]
            await ctx.message.add_reaction('👍')
        elif bid <= bids[game][0]:
            await ctx.message.add_reaction('❌')
            await ctx.message.add_reaction('🇧')
            await ctx.message.add_reaction('🇮')
            await ctx.message.add_reaction('🇩')
            await ctx.message.add_reaction('💸')
            await ctx.message.add_reaction('🇲')
            await ctx.message.add_reaction('🇴')
            await ctx.message.add_reaction('🇷')
            await ctx.message.add_reaction('🇪')

    else:
        await ctx.send('Register yourself, pigfucker.')
    
    rewrite(BIDSFILE, bids)

# Display current table values
@bot.command(name='current', help='Gives the current bids.')
async def current(ctx):
    # Get current bid data
    global BIDSFILE
    bids = openClose(BIDSFILE)
    
    # Display all current games, bids, and users
    if not bids:
        await ctx.send('There are no bids!')
    for game, price in bids.items():
        await ctx.send('{0}: ${1} by {2}'.format(game, price[0], price[1]))
        
# Display current table and ping server for final bids at end of week
@bot.command(name='final', help='Gives current bids AND pings @everyone.')
async def final(ctx):
    await ctx.send('@everyone Final bids for the week:')
    await current(ctx)
    await ctx.send('Place final bids if you haven''t yet!')

# List the names of all games that have been bid on so far
@bot.command(name='listGames', help='Gives names of all games that have been bid on so far.')
async def listGames(ctx):
    global BIDSFILE
    bids = openClose(BIDSFILE)
    for game in bids:
        await ctx.send(game)

    headers = ('game','bid','name')
    await ctx.send(stringOut(headers, bids, 'simple'))
    
# Clear all bids
@bot.command(name='clearBids', help='Clears the bids. !!ALL VALUES WILL BE LOST!!')
async def clearBids(ctx):
    global BIDSFILE
    rewrite(BIDSFILE)
    await ctx.send('Bids cleared!')

# Clear all bids after posting it in chat
@bot.command(name='clearBidsSafe', help='Clears the bids after posting their values. !!VALUES LOST!!')
async def clearBidsSafe(ctx):
    await current(ctx)
    await clearBids(ctx)

# List all registered users by nickname (not ID)
@bot.command(name='users', help='Lists all registered users by nickname.')
async def users(ctx):
    global USERFILE
    users = openClose(USERFILE)
    for _, user in users.items():
        await ctx.send(user)

# Display current bids with corresponding gif
@bot.command(name='currentGif', help='Gives current bids with corresponding GIF!')
async def currentGif(ctx):
    global BIDSFILE
    bids = openClose(BIDSFILE)
    for game, price in bids.items():
        await ctx.send(str(game))
        await ctx.send(search_gifs(str(int(price[0])), 1, 'g'))

# C O L L U S I O N !
@bot.command(name='collusion', help='C O L L U S I O N !')
async def collusion(ctx):
    await ctx.send('https://tenor.com/view/collusion-ruxin-league-gif-5684150')

# Used to remove spaces between command prefix and command
@bot.event
async def on_message(message):
    if message.content[0] == COMMAND_PREFIX and message.content [1] == ' ':
        message.content = COMMAND_PREFIX + message.content[2:]
    else:
        pass
    await bot.process_commands(message)

bot.run(TOKEN)