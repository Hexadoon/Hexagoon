import discord
import sqlite3
import urllib.request
import json 
import sys
from datetime import datetime
import time
from dateutil import parser
from threading import Thread

client = discord.Client()

try:
	cnxn = sqlite3.connect("users.db")
except:
	print('missing db')
	sys.exit(0)

crsr = cnxn.cursor()

org_repos_url = "https://api.github.com/users/hexadoon/repos"

def getGitUser(discordUser):
	crsr.execute("SELECT github_user FROM users WHERE discord_user = '" + discordUser + "'")
	rtrn = []
	for (github_user) in crsr:
		rtrn.append(github_user)

	if len(rtrn) == 0:
		return None
	return rtrn[0][0]

def getJSONfromURL(URL):
	with urllib.request.urlopen(URL) as open_url:
		return json.loads(open_url.read().decode())

# def check_minutely():
# 	while True:
# 		crsr.execute("SELECT * FROM reminders")

# 		all_rem = crsr.fetchall()

# 		for rem in all_rem:
# 			if rem[0] - time.time() < 3600:
# 				notifs = rem[1].split(",")
# 				crsr.execute("DELETE FROM reminders WHERE remtime = " + rem[0] + ";")
# 				crsr.commit()

# 				for u in notifs:
# 					m = bot.get_user(u)
# 					m.dm_channel.send(m.mention + " - Reminder for " + time.strftime('%m/%d/%Y %H:%M', time.localtime(rem[0])))

@client.event
async def on_message(msg):
	msg_author = msg.author.name + "#" + str(msg.author.discriminator)
	if not msg.author.bot:

	 	if "!issues" in msg.content:

	 		github_user = ""

	 		if len(msg.mentions) > 0:
	 			target = msg.mentions[0].name + "#" + str(msg.mentions[0].discriminator)
	 			github_user = getGitUser(target)
	 		else:
	 			github_user = getGitUser(msg_author)

	 		issues_list = []
	 		repos_json = getJSONfromURL(org_repos_url)

	 		if github_user != None:
		 		for repo in repos_json:
		 			issues_json = getJSONfromURL((repo["issues_url"])[:-9]) # index may change depending on github api
		 			for issue in issues_json:
		 				if issue["state"] == "open":
		 					for assignee in issue["assignees"]:
		 						if assignee["login"] == github_user:
		 							issues_list.append(issue["title"] + "\n\n" + issue["body"] + "\n\n" + issue["html_url"])
		 		
		 		target = ""
		 		if len(msg.mentions) > 0:
		 			target = msg.mentions[0]
		 		else:
		 			target = msg.author

		 		await msg.channel.send(target.mention + ", you have `" + str(len(issues_list)) + "` unresolved issues.")
		 		for issue in issues_list:
		 			await msg.channel.send(issue)
		 	else:
		 		await msg.channel.send("User not in database")

	 	elif "!contributions" in msg.content:

	 		github_user = ""
	 		
	 		if len(msg.mentions) > 0:
	 			target = msg.mentions[0].name + "#" + str(msg.mentions[0].discriminator)
	 			github_user = getGitUser(target)
	 		else:
	 			github_user = getGitUser(msg_author)

	 		contributions = {}
	 		additions_total = 0
	 		deletions_total = 0
	 		repos_json = getJSONfromURL(org_repos_url)

	 		if github_user != None:
		 		for repo in repos_json:
		 			repo_name = repo["name"]
		 			contributions_json = getJSONfromURL(repo["url"] + "/stats/contributors")
		 			for user_contributions in contributions_json:
		 				if user_contributions["author"]["login"] == github_user:
		 					contributions[repo_name] = [0, 0]
		 					for week in user_contributions["weeks"]:
		 						contributions[repo_name][0] += week["a"]
		 						additions_total += week["a"]
		 						contributions[repo_name][1] += week["d"]
		 						deletions_total += week["d"]

		 		target = ""
		 		if len(msg.mentions) > 0:
		 			target = msg.mentions[0]
		 		else:
		 			target = msg.author

		 		await msg.channel.send(target.mention + ", you have made `" + str(additions_total) + "` additions and `" + str(deletions_total) + "` deletions.")
		 		for repo in contributions:
		 			await msg.channel.send(repo + ":(`" + str(contributions[repo][0]) + "`+ ; `" + str(contributions[repo][1]) + "`-)")
	 		else:
		 		await msg.channel.send("User not in database")
	 	# elif "!remind" in msg.content:
	 	# 	time_section = msg.content[msg.content.index('[')+1 : msg.content.index(']')]
	 	# 	try:
	 	# 		dt = parser.parse(time_section)
	 	# 	except:
	 	# 		await msg.channel.send("Bad time")

	 	# 	epoch_time = int(dt.timestamp())

	 	# 	all_users = ""
	 	# 	for u in msg.mentions:
	 	# 		all_users += str(u.id) + ","
	 	# 	all_users += str(msg.author.id)

	 	# 	crsr.execute("INSERT INTO reminders VALUES(" + str(epoch_time) + ", '" + all_users + "');")
	 	# 	crsr.commit()

# reminders_thread = Thread(target = check_minutely)
client.run('[INSERT DISCORD BOT TOKEN HERE]')