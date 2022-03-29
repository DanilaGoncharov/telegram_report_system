import pandas as pd
import pandahouse as ph
import io
import telegram
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})

bot = telegram.Bot(token='5109223515:AAGULsMs-W-pCPYrfNj8RlNUni7gU-UE7Do')
chat_id = -1001539201117
# -1001539201117 group chat_id
#  322178021 Danila chat_id

connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220320.feed_actions'}

#number of message per user for yesterday
msg_per_user = ph.read_clickhouse(connection=connection, query=
'''
select count(*) / uniq(user_id) as avg_msg from simulator_20220320.message_actions 
where toDate(time) = today() - 1
''').iloc[0,0]
msg_per_user = round(msg_per_user,3)

#number of message per user for last week
msg_per_user_week = ph.read_clickhouse(connection=connection, query=
'''
select toStartOfDay(toDateTime(time)) as date, count(*) / uniq(user_id) as avg_msg from simulator_20220320.message_actions 
where (toStartOfDay(toDateTime(time)) >= yesterday() - 6 and toStartOfDay(toDateTime(time)) <= yesterday())
group by toStartOfDay(toDateTime(time))
order by toStartOfDay(toDateTime(time))
''')

# DAU of both messenger and feed users for yesterday
dau_msg_feed = ph.read_clickhouse(connection=connection, query=
'''
SELECT uniq(user_id) as dau_msg_feed
FROM simulator_20220320.feed_actions 
JOIN simulator_20220320.message_actions mes using(user_id)
WHERE toStartOfDay(toDateTime(time)) = today() - 1
GROUP BY toDate(time)
ORDER BY toDate(time)
''').iloc[0,0]

# DAU of both messenger and feed users for last week
dau_msg_feed_week = ph.read_clickhouse(connection=connection, query=
'''
SELECT toDate(time) as date, uniq(user_id) as dau_msg_feed
FROM simulator_20220320.feed_actions 
JOIN simulator_20220320.message_actions mes using(user_id)
WHERE (toStartOfDay(toDateTime(time)) >= yesterday() - 6 and toStartOfDay(toDateTime(time)) <= yesterday())
GROUP BY toDate(time)
ORDER BY toDate(time)
''')

# DAU of only feed users for yesterday
dau_feed = ph.read_clickhouse(connection=connection, query=
'''
select uniq(user_id) from simulator_20220320.feed_actions
where user_id not in (
    select user_id from simulator_20220320.message_actions)
    and
    toDate(time) = today() - 1
''').iloc[0,0]

# DAU of only feed users for last week
dau_feed_week = ph.read_clickhouse(connection=connection, query=
'''
select toDate(time) as date, uniq(user_id) as dau_feed from simulator_20220320.feed_actions 
where user_id not in (
    select user_id from simulator_20220320.message_actions)
    and
    (toStartOfDay(toDateTime(time)) >= yesterday() - 6 and toStartOfDay(toDateTime(time)) <= yesterday())
GROUP BY toDate(time)
ORDER BY toDate(time)
''')

dau_feed_week['dau_msg_feed'] = dau_msg_feed_week['dau_msg_feed']
dau = dau_feed_week.copy()
dau['only_msg_pct'] = (round(dau['dau_msg_feed'] / (dau['dau_msg_feed'] + dau['dau_feed']),3)) * 100

message = f"REPORT #2\nYesterday metrics:\nDAU of only feed users: {dau_feed}\nDAU of both messenger and feed users: {dau_msg_feed}\nAverage number of messages per user: {msg_per_user}\n\nThe graphs of the metrics for the last week are below:"

bot.sendMessage(chat_id=chat_id, text=message)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=dau, x='date', y='dau_feed',marker= 'o')
plt.xticks(rotation=18)
plt.title('DAU of only feed users in dynamic for last week')
dau_feed_plot = io.BytesIO()
plt.savefig(dau_feed_plot)
dau_feed_plot.name = 'dau_feed_plot.png'
dau_feed_plot.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=dau_feed_plot)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=dau, x='date', y='dau_msg_feed',marker= 'o')
plt.xticks(rotation=18)
plt.title('DAU of both messenger and feed users in dynamic for last week')
dau_msg_feed_plot = io.BytesIO()
plt.savefig(dau_msg_feed_plot)
dau_msg_feed_plot.name = 'dau_msg_feed_plot.png'
dau_msg_feed_plot.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=dau_msg_feed_plot)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=dau, x='date', y='only_msg_pct',marker= 'o')
plt.xticks(rotation=18)
plt.title('Percent of only feed users in dynamic for last week')
only_msg_pct = io.BytesIO()
plt.savefig(only_msg_pct)
only_msg_pct.name = 'pct_plot.png'
only_msg_pct.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=only_msg_pct)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=msg_per_user_week, x='date', y='avg_msg',marker= 'o')
plt.xticks(rotation=18)
plt.title('Average number of messages per user in dynamic for last week')
avg_msg = io.BytesIO()
plt.savefig(avg_msg)
avg_msg.name = 'pct_plot.png'
avg_msg.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=avg_msg)