import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
import requests
from IPython.display import HTML
from matplotlib.animation import PillowWriter

def init():
    for line in plt_list:
        line.set_data([],[])
    return plt_list

def animate(i):
	for lnum,line in enumerate(plt_list[:int((len(plt_list)-len(quarantines)-len(selection))/2)]):
		line.set_data(totals[selection[lnum]][:i+1], data_week[selection[lnum]][:i+1])

	for lnum,line in enumerate(plt_list[int((len(plt_list)-len(quarantines)-len(selection))/2):-len(quarantines)-len(selection)]):
		if (totals[selection[lnum]][i]>min_x) and (data_week[selection[lnum]][i]>min_y) :
			line.set_x(totals[selection[lnum]][i])
			line.set_y(data_week[selection[lnum]][i])

	qx=[]
	qy=[]
	for time in list(quarantines.keys()):
		if i>=time:
			qx.append(totals[quarantines[time]][time])
			qy.append(data_week[quarantines[time]][time])
		else:
			qx.append(1)
			qy.append(1)


	for lnum,line in enumerate(plt_list[-len(quarantines)-len(selection):-len(selection)]):
		line.set_data(qx[lnum], qy[lnum])

	for lnum,line in enumerate(plt_list[-len(selection):]):
		line.set_data(totals[selection[lnum]][i], data_week[selection[lnum]][i])

	return plt_list

###**** Settings ***
num_days = 3 #The number of days the new cases are counted over
all_places = False #Show all the places in the world
show_quarantine = True #Show the days that lockdowns started in the contries set below
show_legend = True #Show the legend (unhelpful for lots of contries)
selection = ["United Kingdom", "South Korea","United States","Spain","Italy","Austria","India","Sweden"] #The contries you want to see if not all
quarantines= {"2020-03-26":"United Kingdom", "2020-01-27":"China","2020-02-22":"South Korea","2020-03-10":"Italy","2020-03-19":"Austria"} #The days lockdown started in different contries
use_deaths = True #Use deaths or cases data (deaths is less smooth)
save_gif = False #Save as a gif (don't show animation)

# Settings end

if use_deaths == False:
    choice = "cases"
else:
    choice = "deaths"
link = "https://covid.ourworldindata.org/data/ecdc/new_%s.csv"%choice
f = requests.get(link)

with open("%s_new.csv"%choice,"w+") as out:
    out.seek(0)
    out.write(f.text)
    out.truncate()

pd.read_csv("%s_new.csv"%choice, header=None).T.to_csv("%s_new_t.csv"%choice, header=False, index=False)

with open("%s_new_t.csv"%choice) as f:
	data = f.read()
    
data = data.split("\n")
data2 = dict()

dates = data[0].split(",")
data = data[1:]

for line in data:
	line = line.split(",")
	d = line[1:]
	c=list()
	for i in d:
		if i =="":
			i=0
		c.append(float(i))
	data2[line[0]]=c

data = data2
if "World" in list(data.keys()):
    data.pop("World")
if "International" in list(data.keys()):
    data.pop("International")
data.pop("")

totals = dict()
for place in list(data.keys()):
	total=list()
	line = data[place]
	c=1
	total.append(line[0])
	while c<len(line):
		total.append(line[c]+total[c-1])
		c+=1
	totals[place] = total

data_week = dict()
totals_week = dict()
y_week = dict()
ys_week = dict()
for place in list(data.keys()):
	line = data[place]
	week = list()
	week = [line[0],line[0]+line[1],line[0]+line[1]+line[2],line[0]+line[1]+line[2]+line[3]]
	c=num_days
	while c<len(line):
		n = 0
		add = 0
		while n<num_days:
			add+=line[c-n]
			n+=1
		c+=1
		week.append(add)
	data_week[place]=week

	total = totals[place]
	week = list()
	c=0
	while c<len(line):
		week.append(line[c])
		c+=num_days
	totals_week[place]=week

for place in list(data.keys()):
	line = data[place]
	week = list()
	week = [line[0],line[0]+line[1],line[0]+line[1]+line[2],line[0]+line[1]+line[2]+line[3]]
	c=num_days*2
	while c<len(line):
		n = 0
		add = 0
		while n<num_days:
			add+=line[c-n]
			n+=1
		c+=1
		week.append(add)
	y_week[place]=week

	total = totals[place]
	week = list()
	c=0
	while c<len(line):
		week.append(line[c])
		c+=num_days
	ys_week[place]=week

quarantines_tmp=dict()
for d in list(quarantines.keys()):
    quarantines_tmp[dates.index(d)]=quarantines[d]
    
quarantines = quarantines_tmp

fig = plt.figure(figsize=(18,10))
plt.xlabel("Total %s"%choice,fontsize=20)
plt.ylabel("New %s (in the last %s days)"%(choice,num_days),fontsize=20)
plt.title("Trajectory of COVID-19 %s %s"%(choice,dates[-1]),fontsize=20)

ax = fig.add_subplot(111)
ax.set_yscale('log')
ax.set_xscale('log')
ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

if all_places==True:
	selection=list(data.keys())

if show_quarantine==False:
	quarantines={}
max_x = 0
max_y = 0

for contry in selection:
	for i in range(len(data_week[contry])):
		contry_max_y = max(data_week[contry])
		contry_max_x = max(totals[contry])
		if contry_max_y > max_y:
			max_y = contry_max_y
		if contry_max_x > max_x:
			max_x = contry_max_x

min_x = 10
min_y = 1
plt.xlim(left=min_x)
plt.ylim(bottom=min_y)
plt.xlim(right=max_x+100000)
plt.ylim(top=max_y+10000)

ann_list = []
plt_list = []
if num_days == 1:
	data_week = data
for i in selection:
	#color="grey",
	lobj = ax.plot([],[],lw=1, label=i)[0]
	plt_list.append(lobj)

for i in selection:
	lobj = ax.text(1,1, i)
	plt_list.append(lobj)

for i in list(quarantines.keys()):
	lobj = ax.plot([],[],"ro")[0]
	plt_list.append(lobj)

for i in selection:
	lobj = ax.plot([],[],"kx")[0]
	plt_list.append(lobj)

for line in plt_list[0:int((len(plt_list)-len(quarantines)-len(selection))/2)]:
	line.set_data([],[])

a = animation.FuncAnimation(fig, animate, frames = len(data_week[selection[0]])-1, interval=100, blit=True, repeat=False)

if show_legend==True:
	plt.legend(loc="upper left")
    
if show_quarantine == True:
    plt.text(0.95, 0.03,'Red dot shows the \nstart of lockdowns', horizontalalignment='center', verticalalignment='center', transform = ax.transAxes)

plt.show()
print("Max Italy:",max(data_week["Italy"]))
print("Max UK:",max(data_week["United Kingdom"]))
