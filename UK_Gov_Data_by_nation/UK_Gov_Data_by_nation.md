```python
import pandas as pd
from pandas.tseries.offsets import *
import requests
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import statsmodels

load_new=False
links = {
        #"total":"https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newDeaths28DaysByDeathDateRate&format=csv",
        "england":["https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=newDeaths28DaysByDeathDate&format=csv",56286961],
        "wales":["https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=W92000004&metric=newDeaths28DaysByDeathDate&format=csv",3152879],
        "scotland":["https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=S92000003&metric=newDeaths28DaysByDeathDate&format=csv",5463300],
        #"ireland":"https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=N92000002&metric=newDeaths28DaysByDeathDateRate&format=csv"
}
df=pd.DataFrame()
for link in links:
    if load_new==True:
        f = requests.get(links[link][0])

        with open("%s_deaths.csv"%link,"w+") as out:
            out.seek(0)
            out.write(f.text)
            out.truncate()
        
    area_data = pd.read_csv("%s_deaths.csv"%link)
    area_data.dropna()#There are nan values in feb before deaths started and yesterday where reporting isn't complete
    area_data=area_data[::-1].reset_index()#Results are indexed backwards in time
    df.insert(0,link,[n/(links[link][1]/100000) for n in area_data["newDeaths28DaysByDeathDate"].rolling(7).mean().to_list()[:-3]])#Drops the last few days because they're always way less since the deaths not yet reported
    df["date"]=area_data["date"]
```


```python
def plot(include):
    plt.rcParams["figure.figsize"] = (15,10)

    plt.plot(df.loc[df['date'] == "2020-03-23"]["england"],marker="o",label="National lockdown announcement",color="grey")
    plt.plot(df.loc[df['date'] == "2020-03-26"]["england"],marker="o",label="National lockdown legally began",color="red")

    for link in include:
        plt.plot(df[link],"--",label=link)
        plt.plot(df.loc[df['date'] == "2020-03-23"][link],marker="o",color="grey")
        plt.plot(df.loc[df['date'] == "2020-03-26"][link],marker="o",color="red")
        plt.errorbar(df.index[df['date'] == "2020-04-11"],df.loc[df['date'] == "2020-04-11"][link].values[0], xerr=3.5,marker="o",color="grey")
        plt.errorbar(df.index[df['date'] == "2020-04-14"],df.loc[df['date'] == "2020-04-14"][link].values[0], xerr=3.5,marker="o",color="red")

    if "england" in include:
        plt.plot(df.loc[df['date'] == "2020-10-13"]["england"],marker="o",label="England tier System began",color="black")
        plt.plot(df.loc[df['date'] == "2020-11-05"]["england"],marker="o",label="England lockdown 2 began",color="red")
        plt.errorbar(df.index[df['date'] == "2020-04-11"],df.loc[df['date'] == "2020-04-11"]["england"].values[0], xerr=3.5,marker="o",label="National announcement plus 19 days",color="grey")
        plt.errorbar(df.index[df['date'] == "2020-04-14"],df.loc[df['date'] == "2020-04-14"]["england"].values[0], xerr=3.5,marker="o",label="National lockdown plus 19 days",color="red")
        plt.errorbar(df.index[df['date'] == "2020-11-01"],df.loc[df['date'] == "2020-11-01"]["england"].values[0], xerr=3.5,marker="o",label="England tier system 1 plus 19 days",color="black")
        plt.errorbar(df.index[df['date'] == "2020-11-24"],df.loc[df['date'] == "2020-11-24"]["england"].values[0], xerr=3.5,marker="o",label="England lockdown 2 plus 19 days",color="red")
    if "wales" in include:  
        plt.plot(df.loc[df['date'] == "2020-10-23"]["wales"],marker="o",label="Wales lockdown 2 began",color="red")
        plt.errorbar(df.index[df['date'] == "2020-11-11"],df.loc[df['date'] == "2020-11-11"]["wales"].values[0], xerr=3.5,marker="o",label="Wales lockdown 2 plus 19 days",color="red")
    if "scotland" in include:
        plt.plot(df.loc[df['date'] == "2020-10-23"]["scotland"],marker="o",label="Scotland tier system announced",color="grey")
        plt.plot(df.loc[df['date'] == "2020-11-02"]["scotland"],marker="o",label="Scotland tier system began",color="black")
        plt.errorbar(df.index[df['date'] == "2020-11-21"],df.loc[df['date'] == "2020-11-21"]["scotland"].values[0], xerr=3.5,marker="o",label="Scotland tier system plus 19 days",color="black")
        plt.errorbar(df.index[df['date'] == "2020-11-11"],df.loc[df['date'] == "2020-11-11"]["scotland"].values[0], xerr=3.5,marker="o",label="Scotland tier system announcement plus 19 days",color="grey")

    plt.xlabel("Days since 3$^{rd}$ January 2020")
    plt.ylabel("COVID 19 Deaths per 100k (that occured on the day)")
    plt.title("COVID 19 Deaths")

    plt.legend()
```


```python
plot(["england","wales"])
```


    
![png](output_2_0.png)
    


18.5±3.5 days is average days to death(https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30566-3/fulltext#tbl2). You can clearly see deaths dropping in both England and Wales almost exactly this amount of time after both lockdowns were implimented.


```python
plot(["england","wales","scotland"])
```


    
![png](output_4_0.png)
    


When Scotland is included it appears that deaths in Scotland respond to the announcement of the measures rather than their legal implimentation. It also appears that Scotland's tier system is effective where England's was not.


```python
plot(["wales","scotland"])
```


    
![png](output_6_0.png)
    


Clearer without England cluttering up the end.


```python

```
