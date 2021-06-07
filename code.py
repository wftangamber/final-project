import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
def getHtml(url):
    session = requests.Session()
    req=session.get(url)

    html=req.text
    return html
url='https://www.worldometers.info/coronavirus/?utm_campaign=homeAdvegas1?#countries'
html=getHtml(url)
def getData(html):
    '''
    (str)->list
    
    html: URL request return value, str
    
    return data, list
    '''
    
    soup = BeautifulSoup(html,'lxml')
    
    divs = soup.find_all('tr', style='')
    
    
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
columns=['Country,Other','Total Cases','New Cases','Total Deaths','New Deaths','Total Recovered',
         'Active Cases','Serious Critical','Tot Cases/1M pop','Deaths/1M pop','Total Tests',
         'Tests/1M pop','Population','Region']

data=getData(html)

pdata=pd.DataFrame(data,columns=columns)
pdata.head()
def cleanComma(pdata,columns):
    for column in columns:
        pdata[column]=pdata[column].str.replace(',','')
        pdata[column]=pdata[column].str.replace('+','')
    
    
cleanComma(pdata,columns)
pdata.head()
def change_to_numeric(pdata,columns):
    for column in columns:
        pdata[column]=pd.to_numeric(pdata[column], downcast='float', errors='coerce').fillna(np.nan)
    
    
columns_change2numeric=['Total Cases','New Cases','Total Deaths','New Deaths','Total Recovered',
         'Active Cases','Serious Critical','Tot Cases/1M pop','Deaths/1M pop','Total Tests',
         'Tests/1M pop','Population']

change_to_numeric(pdata,columns_change2numeric)


pdata['Total Deaths Ratio']=pdata['Total Deaths']/pdata['Total Cases']
pdata.head()
pdata.fillna(0,inplace=True)
pdata.info()
pdata.drop_duplicates(['Country,Other'],keep='first',inplace=True)
pdata.info()
pdata[pdata['Country,Other']=='India']
pdata_group=pdata.groupby("Region")[['Total Cases','New Cases','Total Deaths','New Deaths','Total Recovered',
         'Active Cases','Serious Critical','Tot Cases/1M pop','Deaths/1M pop','Total Tests',
         'Tests/1M pop','Population']].sum()
pdata_group.index
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
plt.figure(figsize=(10, 8))
plt.plot(pdata_group.index,pdata_group['New Deaths'],'o-',color='red',linewidth='1')
plt.bar(pdata_group.index,pdata_group['New Deaths'],width=0.6, align='center',color='skyblue')
plt.xlabel('Region')
plt.ylabel('New Deaths')
plt.title('New Deaths vs Region')
plt.show()
pdata_asia=pdata[(pdata['Region']=='Asia') & (pdata['New Deaths']>0)]
pdata_asia.sort_values(by='New Deaths', ascending=False, inplace=True )
pdata_asia
plt.figure(figsize=(10, 10))
plt.barh(pdata_asia['Country,Other'],pdata_asia['New Deaths'],align='center',color='skyblue')
plt.xlabel('Country,Other')
plt.ylabel('New Deaths')
plt.title('Location vs hourly sales (AUD) in raining day')
plt.show()
pdata[(pdata['Region']=='Asia') & (pdata['New Deaths']==0)]['Country,Other']
from sqlalchemy import create_engine
engine = create_engine('sqlite:///worldometers.sqlite')
pdata.to_sql(name='coronavirus', con=engine ,if_exists='replace',index=False)

pdata[pdata['Region']=='Africa'].to_sql(name='coronavirus_Africa', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='Asia'].to_sql(name='coronavirus_Asia', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='Australia/Oceania'].to_sql(name='coronavirus_Australia/Oceania', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='Europe'].to_sql(name='coronavirus_Europe', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='North America'].to_sql(name='coronavirus_North_America', con=engine ,if_exists='replace',index=False)
pdata[pdata['Region']=='South America'].to_sql(name='coronavirus_South_America', con=engine ,if_exists='replace',index=False)
North_America = "SELECT * from coronavirus_North_America where [New Deaths] >0" 
North_America = pd.read_sql_query(North_America, engine)
North_America
coronavirus = "SELECT * from coronavirus where [New Deaths] >0" 
coronavirus = pd.read_sql_query(coronavirus, engine)
coronavirus
coronavirus_group=coronavirus.groupby('Region')['Total Cases','Total Deaths'].sum()
coronavirus_group['Total Deaths Ratio']=coronavirus_group['Total Deaths']/coronavirus_group['Total Cases']*100
coronavirus_group
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
