from wowspy import Wows
from pprint import pp
from config import apikey,AOD_A,AOD_B,AOD_C,AOD_D,AOD_EU,AOD_CZ_EU,OAUTH_KEY
from datetime import datetime, timedelta
import requests
from discord_webhooks import DiscordWebhooks
import pygsheets
import pandas as pd

gc = pygsheets.authorize(client_secret='E:\\Projects\\Repos\\PyWoWSStats\\oauth.json')
api_key = apikey
my_api=Wows(api_key)
webhook_url = DiscordWebhookURL
# change your region by changing the end to EU or Asia or RU.
NA = my_api.region.NA
EU = my_api.region.EU
ASIA = my_api.region.AS
RU = my_api.region.RU 


# Create empty dataframe
df = pd.DataFrame()
# Open the sheet named Inactivity
sh=gc.open('Inactivity')
# go to sheet 1
wks=sh[0]
# index to A1
wks.set_dataframe(df,(0,0))

# exclude the following users, i.e. officers alt accounts and such.
excludeUsers = ["AODGLAD1980E","AOD_StyrgisE_1","ZiggyInTheSea","AOD_StyrgisC_1","NotYouZiggy","Gladiator1980c","AOD_Styrgis","Gladiator1980d","aodstud","SabreSixFour","gladiator1980a"]

# silly math stuff to get date 30 and 60 days ago
thirtyDaysAgo = datetime.now() - timedelta(days = 30)
sixtyDaysAgo = datetime.now() - timedelta(days = 60)

# create lists for 30 day and 60 day Nicknames, Profile Links, Days since Last Battle, and Date of Last Battle
nicks1 = ["Nickname"]
links1 = ["Profile Link"]
days_lbt1 = ["Days Since Last Battle"]
lbt_time1 = ["Date of Last Battle"]
nicks2 = ["Nickname"]
links2 = ["Profile Link"]
days_lbt2 = ["Days Since Last Battle"]
lbt_time2 = ["Date of Last Battle"]

#change unix time to UTC
def unixToUTC(unixTime):
    utc_time = datetime.utcfromtimestamp(unixTime)
    final_utc_time = utc_time #.strftime("%Y-%m-%d %H:%M:%S.%f+00:00 (UTC)")
    return final_utc_time

# actually do the work with the Wargaming API
def getInactives(region, Clan_ID):
    clan_members = my_api.clan_details(region,Clan_ID)['data'][str(Clan_ID)]['members_ids']
    #print(clan_members)
    overThirty = []
    overSixty = []
    for member_id in clan_members:
        stats = my_api.player_personal_data(region,member_id,fields='last_battle_time,nickname')
        #print(stats)
        lbt = stats['data'][f'{member_id}']['last_battle_time']
        #print(lbt)
        lbt_unix = int(lbt)
        nickname = stats['data'][f'{member_id}']['nickname']
        if nickname in excludeUsers:
            continue
        # nicks.append(nickname)
        # if region == NA:
        #     links.append(("https://profile.worldofwarships.com/statistics/"+str(member_id)))
        # if region == EU:
        #     links.append(("https://profile.worldofwarships.eu/statistics/"+str(member_id)))
        lbt_utc = unixToUTC(lbt_unix)
        lbt_utc_str = lbt_utc.strftime("%Y-%m-%d %H:%M:%S (UTC)")
        days_since_lbt = datetime.now() - lbt_utc
        
        if lbt_utc < thirtyDaysAgo and lbt_utc > sixtyDaysAgo:
            # NA links
            if region == NA:
                links1.append(("https://profile.worldofwarships.com/statistics/"+str(member_id)))
            # make sure if they're EU the link actually freaking works    
            if region == EU:
                links1.append(("https://profile.worldofwarships.eu/statistics/"+str(member_id)))
            lbt_time1.append(str(lbt_utc_str))
            days_lbt1.append(str(days_since_lbt.days))
            overThirty.append(f"{nickname} was last on {lbt_utc_str}, {days_since_lbt.days} days ago")
        if lbt_utc < sixtyDaysAgo:
            # link if NA
            if region == NA:
                links2.append(("https://profile.worldofwarships.com/statistics/"+str(member_id)))
            # link if EU
            if region == EU:
                links2.append(("https://profile.worldofwarships.eu/statistics/"+str(member_id)))
            lbt_time2.append(str(lbt_utc_str))
            days_lbt2.append(str(days_since_lbt.days))
            overSixty.append(f"{nickname} was last on {lbt_utc_str}, {days_since_lbt.days} days ago")
            #print(f'{nickname} last battle was on {lbt_utc}')
        #return overThirty,overSixty
    o30 = ""
    o60 = ""
    # priinting members to console if over 30 and over 60.
    if (len(overThirty) > 0):
        print(f'\nMembers over 30 days since LBT:\n\n')
        o30 += f'Members over 30 days since LBT:\n\n'
    for member in overThirty:
        print(f'{member}\n')
        o30 += f'{member}\n'
    if(len(overSixty) > 0):
        print(f'\nMembers over 60 days since LBT:\n\n')
        o60 += f'\nMembers over 60 days since LBT:\n\n'
    for member in overSixty:
        print(f'{member}\n')
        o60 += f'{member}\n'
    tot = o30 + o60
    return tot
    #print(f'\n Rest of the clan, not inactive:\n')
    #print(clan_members)

def getStringInactives(r, c):
    na30,na60 = getInactives(r,c)
    na30 = f"Over 30 days since LBT:\n"
    na60 = f"Over 60 days since LBT:\n"
    for m in na30:
        na30 += f'{m}\n'
    for m in na60:
        na60 += f'{m}\n'
    total = na30 + na60
    return total

def main():
    #call the API for each port
    getInactives(NA,AOD_A)
    getInactives(NA,AOD_B)
    getInactives(NA,AOD_C)
    getInactives(NA,AOD_D)
    # EU is included too!
    getInactives(EU,AOD_EU)
    getInactives(EU,AOD_CZ_EU)
    #sheet 1
    wks=sh[0]
    # index to A1
    wks.set_dataframe(df,(0,0))
    # clear all entries
    sh.clear("*")
    wks.update_col(1,nicks1)
    print("nicks 30+ done")
    wks.update_col(2,days_lbt1)
    print("lbt_days 30+ done")
    wks.update_col(3,lbt_time1)
    print("lbt_time 30+ done")
    wks.update_col(4,links1)
    print("30+ done")
    # switch to sheet two
    wks=sh[1]
    # index to A1
    wks.set_dataframe(df,(0,0))
    # clear all entries
    sh.clear("*")
    wks.update_col(1,nicks2)
    print("nicks 60+ done")
    wks.update_col(2,days_lbt2)
    print("lbt_days 60+ done")
    wks.update_col(3,lbt_time2)
    print("lbt_time 60+ done")
    wks.update_col(4,links2)
    print("Completely done")

#     url = 'https://discord.com/api/webhooks/1100054997959463063/8bnlNAyJ0M6JX4zb-6HM-6NHuTuHG8QtlZc9MjSaMtu3B-pfHAJT1vTcpVAopSHTeAYq'
# #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    
#     # change the name here, as well as for each of the embeds below. The pp() statements simply show up on the terminal output, so if using discord webhook,
#     # it's unnecessary.
#     data = {
#         "content" : "Inactivity Report for Each AOD Port",
#         "username" : "Inactivity Checker"
#     }
#     NA_AOD_A = getInactives(NA,AOD_A)
#     NA_AOD_B = getInactives(NA,AOD_B)
#     NA_AOD_C = getInactives(NA,AOD_C)
#     NA_AOD_D = getInactives(NA,AOD_D)
#     EU_AOD = getInactives(EU,AOD_EU)
#     EU_AODCZ = getInactives(EU,AOD_CZ_EU)
    
#     # using pretty print to format this neatly when it outputs to console. Be sure to change the clan names as appropriate.
#     pp(f'AOD_A: \n {NA_AOD_A} \n')
#     pp(f'AOD_B: \n {NA_AOD_B} \n')
#     pp(f'AOD_C: \n {NA_AOD_C} \n')
#     pp(f'AOD_D: \n {NA_AOD_D} \n')
#     pp(f'AOD (EU): \n {EU_AOD} \n')
#     pp(f'AOD_CZ (EU): \n {EU_AODCZ} \n')
# #leave this out if you dont want an embed
# #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
#     data["embeds"] = [
#         # each dict (the {key:pair, key:pair} portions) consitutes its own embed.
        
#         {
#             "description" : f'```{NA_AOD_A}```',
#             "title" : "AOD_A"
#         },
#         {
#             "description" : f'```{NA_AOD_B}```',
#             "title" : "AOD_B"
#         },
#         {
#             "description" : f'```{NA_AOD_C}```',
#             "title" : "AOD_C"
#         },
#         {
#             "description" : f'```{NA_AOD_D}```',
#             "title" : "AOD_D"
#         },
#         {
#             "description" : f'```{EU_AOD}```',
#             "title" : "AOD (EU)"
#         },
#         {
#             "description" : f'```{EU_AODCZ}```',
#             "title" : "AODCZ (EU)"
#         }
#     ]

#     result = requests.post(url, json = data)

#     try:
#         result.raise_for_status()
#     except requests.exceptions.HTTPError as err:
#         print(err)
#     else:
#         print("Payload delivered successfully, code {}.".format(result.status_code))

if __name__ == '__main__':
    main()  

