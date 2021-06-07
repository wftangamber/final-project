# final-project
# Wufan Tang
In this project, I am going to explain and analyze the reported cases and deaths of the COVID-19 coronavirus worldwide. The website I am choosing to crawl is [woroldometer](https://www.worldometers.info/coronavirus/?utm_campaign=homeAdvegas1?#countries).

COVID-19 is a highly contagious disease which affect people's life worldwild. Comparing to other contagious disease, COVID-19 has a high fatality rate. Although most people infected with the COVID-19 only have mild to moderate illness, a lot of people will have severe illness which might lead to death. I am interested in the mapping of the fatality situation across the world. And hopefully we can find the reasons behind the differences of death rate to avoid more deaths. So in this project, I am going to define the fatality rate as total death/total cases, and have some basic analyze toward the death situation.

(The detailed definition of the code is written within in the code after #)

I. crawl the website and get the data

> I am using the BeautifulSoup in the project because I need to scrape and parse HTML
```
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
```
```
def getHtml(url):
    # create a persistent session which maintains certain parameters across requests
    session = requests.Session()
    req=session.get(url)

    # return the response data
    html=req.text
    return html
```
```
# define the url I am going to crawl
url='https://www.worldometers.info/coronavirus/?utm_campaign=homeAdvegas1?#countries'
html=getHtml(url)
```
```
def getData(html):
    '''
    (str)->list
    
    html: URL request return value, str
    
    return data, list
    '''
    # use BeautifulSoup to scrape the website
    soup = BeautifulSoup(html,'lxml')
    # find the data with 'tr' in soup, cause the target data is in 'tr'
    divs = soup.find_all('tr', style='')
    
    # define the empty string, which for the panda dataframe later
    data=[]
    for div in divs:
        if '/a' in str(div):
            data_series=[]
            data_series.append(div.a.string)
            for idx,td in enumerate(div.find_all('td')):
                if idx >=2 and idx <=15:
                    if idx==7:
                        pass
                    elif idx ==14:
                        data_series.append(td.a.string) if td.a != None else data_series.append(np.nan)
                    else:
                        data_series.append(td.string)

            data.append(data_series)
    return data
```
```
# set column names of panda dataframe
columns=['Country,Other','Total Cases','New Cases','Total Deaths','New Deaths','Total Recovered',
         'Active Cases','Serious Critical','Tot Cases/1M pop','Deaths/1M pop','Total Tests',
         'Tests/1M pop','Population','Region']

data=getData(html)

pdata=pd.DataFrame(data,columns=columns)
pdata.head()
```

II. Manipulate the data

> The raw data is rough, so I am doing some manipulation for a better visualizatioin and analyz later.
> A new column of Total Death Ratio is created here, which define as the total deaths/total cases, and allow us to see the death rates more directly.
```
# remove the , and + signs in numbers
def cleanComma(pdata,columns):
    for column in columns:
        pdata[column]=pdata[column].str.replace(',','')
        pdata[column]=pdata[column].str.replace('+','')
    
    
cleanComma(pdata,columns)
pdata.head()
```
```
def change_to_numeric(pdata,columns):
    for column in columns:
        pdata[column]=pd.to_numeric(pdata[column], downcast='float', errors='coerce').fillna(np.nan)
    
    
columns_change2numeric=['Total Cases','New Cases','Total Deaths','New Deaths','Total Recovered',
         'Active Cases','Serious Critical','Tot Cases/1M pop','Deaths/1M pop','Total Tests',
         'Tests/1M pop','Population']

change_to_numeric(pdata,columns_change2numeric)

# create a new column - Total Deaths Ratio
pdata['Total Deaths Ratio']=pdata['Total Deaths']/pdata['Total Cases']
pdata.head()
```
```
# replace the missing values with 0
pdata.fillna(0,inplace=True)
pdata.info()
pdata.drop_duplicates(['Country,Other'],keep='first',inplace=True)
pdata.info()
# check
pdata[pdata['Country,Other']=='India']
```
```
#group with regions
pdata_group=pdata.groupby("Region")[['Total Cases','New Cases','Total Deaths','New Deaths','Total Recovered',
         'Active Cases','Serious Critical','Tot Cases/1M pop','Deaths/1M pop','Total Tests',
         'Tests/1M pop','Population']].sum()
pdata_group.index
```

III. Simple visualization

```
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
#new death vs. region plot to find the rough situation
plt.figure(figsize=(10, 8))
plt.plot(pdata_group.index,pdata_group['New Deaths'],'o-',color='red',linewidth='1')
plt.bar(pdata_group.index,pdata_group['New Deaths'],width=0.6, align='center',color='skyblue')
plt.xlabel('Region')
plt.ylabel('New Deaths')
plt.title('New Deaths vs Region')
plt.show()
```
> The new death vs. region plot

![Screen Shot 2021-06-06 at 10 18 19 PM](https://user-images.githubusercontent.com/79046826/120962788-41f8d800-c715-11eb-9f00-237b508793a5.png)

Comparing to other regions in the world, we can see that the new death cases in Asia is very high. Why? So I am going to look deeper into Asia.
```
pdata_asia=pdata[(pdata['Region']=='Asia') & (pdata['New Deaths']>0)]
pdata_asia.sort_values(by='New Deaths', ascending=False, inplace=True )
pdata_asia
```
> The table for asia

![Screen Shot 2021-06-06 at 10 37 00 PM](https://user-images.githubusercontent.com/79046826/120964169-b7fe3e80-c717-11eb-8339-4486b1f5fd03.png)

The India has 2437 new death, which is the only country above 200. 

```
plt.figure(figsize=(10, 10))
plt.barh(pdata_asia['Country,Other'],pdata_asia['New Deaths'],align='center',color='skyblue')
plt.xlabel('Country,Other')
plt.ylabel('New Deaths')
plt.title('Location vs hourly sales (AUD) in raining day')
plt.show()

# filter out the 0 new death country in Asia
pdata[(pdata['Region']=='Asia') & (pdata['New Deaths']==0)]['Country,Other']
```
> plot for countries which have new death in Asia

![Screen Shot 2021-06-06 at 10 42 57 PM](https://user-images.githubusercontent.com/79046826/120964694-8d60b580-c718-11eb-919d-6a87fd522516.png)

India have a very high new death. It seems that the India is why Asia have so much new death compares to other regions. I think this happens because there is virus mutation in India. And many people dies due to the new type of COVID-19. Also the vaccination isn't enough in India.

IV. General situation of regions and the world

> Overall situation by SQL
```
# by regions
from sqlalchemy import create_engine
engine = create_engine('sqlite:///worldometers.sqlite')
pdata.to_sql(name='coronavirus', con=engine ,if_exists='replace',index=False)

pdata[pdata['Region']=='Africa'].to_sql(name='coronavirus_Africa', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='Asia'].to_sql(name='coronavirus_Asia', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='Australia/Oceania'].to_sql(name='coronavirus_Australia/Oceania', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='Europe'].to_sql(name='coronavirus_Europe', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='North America'].to_sql(name='coronavirus_North_America', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='South America'].to_sql(name='coronavirus_South_America', con=engine ,if_exists='replace',index=False)
```
```
#North America situation cuz I am interested
North_America = "SELECT * from coronavirus_North_America where [New Deaths] >0" # when empty space appears
North_America = pd.read_sql_query(North_America, engine)
North_America
coronavirus = "SELECT * from coronavirus where [New Deaths] >0" 
coronavirus = pd.read_sql_query(coronavirus, engine)
coronavirus
```
```
# Summary the data by regions
coronavirus_group=coronavirus.groupby('Region')['Total Cases','Total Deaths'].sum()
coronavirus_group['Total Deaths Ratio']=coronavirus_group['Total Deaths']/coronavirus_group['Total Cases']*100
coronavirus_group
```
> summary table by regions

![Screen Shot 2021-06-06 at 10 55 44 PM](https://user-images.githubusercontent.com/79046826/120965921-568b9f00-c71a-11eb-8d2f-de5bda01c3ef.png)

We can see that Asia has the smallest death ratio. 

> D3
```
import mpld3
from mpld3 import plugins

# plt.figure(figsize=(10, 8))
# plt.plot(coronavirus_group.index,coronavirus_group['Total Deaths Ratio'],'*-',color='red',linewidth='1')
# plt.xlabel('Region')
# plt.ylabel('Total Deaths Ratio/%')
# plt.title('Total Deaths Ratio vs Region')
# plt.show()

fig, ax = plt.subplots()
ax.grid(True, alpha=0.3)
ax.plot(coronavirus_group.index,coronavirus_group['Total Deaths Ratio'])
ax.grid(color='white', linestyle='solid')

ax.set_title("Total Deaths Ratio vs Region", size=20)
# mpld3.display()
mpld3.show()
```
> plot of death ratio vs. regions

![Screen Shot 2021-06-06 at 11 08 46 PM](https://user-images.githubusercontent.com/79046826/120967343-30ff9500-c71c-11eb-981b-729898fd36f1.png)

It's clearly that Asia has the lowest death rate. Why? I am guessing the staying at home policy was more efficient? Believe me, most Asians are very afraid of death. I am an Asian, and I was literally stayed in the house for at least 3 months. I didn't even go to the grocery. 

V. Summary

For the new death, India has the largest number. The COVID-19 mutation might be the reason behind it. In general, Asia has the lowest death rate - despite that there is a large increase of death cases in India recently. The reason behind it might be complex. A lot of countries in Asia are developing countries. The economics is bad comparing to other regions. And the medical conditions suppose to be worse than Europe and North America. Without the advantages of medical conditions, it's hard to believe that the death rate in Asia is so low. I think more researches can be done base on the result. But just for a wild guess, I think Asia took the COVID-19 more seriously. Developing countries can't risk it -- once the COVID-19 starts, it is hard to stop. Hopefully the situation will get better and better, and no more death will occur.
