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

dau = ph.read_clickhouse(query='''
select uniq(user_id) as dau
from simulator_20220320.feed_actions
where toStartOfDay(time) = today() - 1
''', connection=connection)
dau = dau.iloc[0,0]

views = ph.read_clickhouse(query='''
select count(*) as views
from simulator_20220320.feed_actions
where toStartOfDay(time) = today() - 1 and action = 'view'
''', connection=connection)
views = views.iloc[0,0]

likes = ph.read_clickhouse(query='''
select count(*) as likes
from simulator_20220320.feed_actions
where toStartOfDay(time) = today() - 1 and action = 'like'
''', connection=connection)
likes = likes.iloc[0,0]

ctr = round(likes/views, 3)

msg = f"REPORT #1\nYesterday the key metrics were following:\nDAU: {dau}\nNumber of views: {views}\nNumber of likes: {likes}\nCTR: {ctr}\n\nThe graphs of the key metrics for the last week are below:"
      
bot.sendMessage(chat_id=chat_id, text=msg)

week = ph.read_clickhouse(connection=connection, query='''
select toStartOfDay(toDateTime(time)) as date,
    uniq(user_id) as dau,
    countIf(action, action='view') as views,
    countIf(action, action='like') as likes,
    round(countIf(action, action='like') / countIf(action, action='view'),3) as ctr
from simulator_20220320.feed_actions
where (toStartOfDay(toDateTime(time)) >= yesterday() - 6 and toStartOfDay(toDateTime(time)) <= yesterday())
group by toStartOfDay(toDateTime(time))
order by toStartOfDay(toDateTime(time))
''')

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=week, x='date', y='dau',marker= 'o')
plt.xticks(rotation=18)
plt.title('DAU in dynamic for last week')
dau_plot = io.BytesIO()
plt.savefig(dau_plot)
dau_plot.name = 'dau_plot.png'
dau_plot.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=dau_plot)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=week, x='date', y='likes',marker= 'o')
plt.xticks(rotation=18)
plt.title('Number of likes in dynamic for last week')
likes_plot = io.BytesIO()
plt.savefig(likes_plot)
likes_plot.name = 'likes_plot.png'
likes_plot.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=likes_plot)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=week, x='date', y='views',marker= 'o')
plt.xticks(rotation=18)
plt.title('Number of views in dynamic for last week')
views_plot = io.BytesIO()
plt.savefig(views_plot)
views_plot.name = 'views_plot.png'
views_plot.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=views_plot)

fig, ax = plt.subplots(1,1,figsize=(8,8))
ax = sns.lineplot(data=week, x='date', y='ctr',marker= 'o')
plt.xticks(rotation=18)
plt.title('CTR in dynamic for last week')
ctr_plot = io.BytesIO()
plt.savefig(ctr_plot)
ctr_plot.name = 'ctr_plot.png'
ctr_plot.seek(0)
plt.close()
bot.sendPhoto(chat_id=chat_id, photo=ctr_plot)
