#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 25 11:57:50 2018

@author: mlbook
Trade Scrips Analysis for trades using the Bokeh graphs which has good features for use..
Tools are available for each graph for panning/zooming/refeshing the graphs.

Note: The same can be done in Excel using Scale functionality of Pivot tables.

"""

from bokeh.core.properties import value
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.transform import dodge
from bokeh.layouts import row, column

output_file("dodged_bars2.html")

#Import datafile
import pandas as pd
import numpy as np

#Import the dataset from the csv file
df = pd.read_csv('Trades-Buy-Sell.csv')

#Create a feature for Buy/Sell-Quantity for the day
df['Q-B'] = np.where(df['Transaction_Type']=='Buy',df['Bal_Qty'],0)
df['Q-S'] = np.where(df['Transaction_Type']=='Sell',df['Bal_Qty'],0)

#Create a feature for Prices at Buy/Sell..
df['Price_Buy'] = np.where(df['Transaction_Type']=='Buy',df['Purchase_Rate'],0)
df['Price_Sell'] = np.where(df['Transaction_Type']=='Sell',df['Purchase_Rate'],0)

#This will fetch the scrips and order based on recent transaction.
df['td_datewise'] = pd.to_datetime(df['Transaction_Date'])
scrips = df.loc[df.groupby('Scrip_ID').td_datewise.idxmax()].sort_values('td_datewise',ascending=False).Scrip_ID

#Convert the data in values for further processing..
scrips = scrips.values

#Calculate the no. of filter scrips which will be used for iteration..
len_scrips = len(scrips)

prows=[]

count=0
while count < len_scrips:    #len_scrips
    
    dfselect=df.loc[df['Scrip_ID']== scrips[count]]

    df1 = pd.pivot_table(dfselect,index=['Transaction_Date','Scrip_ID','Transaction_Type'],values = ['Purchase_Rate','Q-B','Q-S','Price_Buy','Price_Sell'],aggfunc={'Q-B':np.sum, 'Q-S':np.sum, 'Price_Buy':np.mean, 'Price_Sell':np.mean})
    
    df1=df1.round({'Price_Buy':1, 'Price_Sell':1})

    pivinx=df1.index.values
    pivinxz = list(zip(*pivinx))
    df1['newtd']=pivinxz[0]
    df1['newscripid']=pivinxz[1]
    df1['newtrantype']=pivinxz[2]
    
    df1['newtd-date']=pd.to_datetime(df1['newtd'])
     
    df1.set_index('newtd', inplace=True)
   
    q_fig_plot_max_range = (max(df1['Q-B'].max(), df1['Q-S'].max())*1.2).astype(int)
    q_fig_plot_min_range = (min(df1['Q-B'].min(), df1['Q-S'].min())*0.8).astype(int)
    
    p_fig_plot_max_range = (max(df1['Price_Buy'].max(), df1['Price_Sell'].max())*1.3).astype(int)
    p_fig_plot_min_range = (min(df1['Price_Buy'].min(), df1['Price_Sell'].min())*0.7).astype(int)
    
    df1.replace(0,np.nan,inplace = True)
    
    df1=df1.groupby('newtd').first() 
    df1.sort_values(by='newtd-date', ascending=True,inplace=True)
    
    myx = df1.index.values
    myy = ['Buy', 'Sell']
    
    data = {'myx' : myx,
            'Buy'   : df1['Q-B'],
            'Sell'   : df1['Q-S'],
            'PriceBuy' : df1['Price_Buy'],
            'PriceSell' : df1['Price_Sell']
            }
    
    source = ColumnDataSource(data=data)
    
    
    #Graph - Bar - Volumes    
    p1 = figure(x_range=myx, y_range=(q_fig_plot_min_range, q_fig_plot_max_range), 
                plot_height=500, title="Trades Data by Volume - {}" . format(scrips[count]),
                tools='pan,box_zoom,reset')    
    p1.vbar(x=dodge('myx', -0.2, range=p1.x_range), top='Buy', width=0.2, source=source,
           color="#2ecc71", legend=value("Buy"))
    p1labels1 = LabelSet(x='myx', y='Buy', text='Buy', y_offset=10,x_offset=-7,
                      text_font_size="8pt", text_color="green", text_font_style="bold",
                      source=source, text_align='center')
    p1.add_layout(p1labels1)
    
    
    p1.vbar(x=dodge('myx',  0.2,  range=p1.x_range), top='Sell', width=0.2, source=source,
           color="#e84d60", legend=value("Sell"))
    
    p1labels2 = LabelSet(x='myx', y='Sell', text='Sell', y_offset=0,x_offset=8,
                      text_font_size="8pt", text_color="orange", text_font_style="italic",
                      source=source, text_align='center')
    p1.add_layout(p1labels2)
    
    
    #Graph - Line graph to depict our scrips data..  
    p2 = figure(x_range=myx, y_range=(p_fig_plot_min_range, p_fig_plot_max_range), plot_height=500, title="Trades Data by price - {}" . format(scrips[count]),
                tools='pan,box_zoom,reset')
    p2.line(x='myx', y='PriceBuy',source=source,legend=value('Buy'),line_width=2,color='green')
    p2.triangle(x='myx', y='PriceBuy',source=source,line_width=2,color='green')
    
    p2.line(x='myx', y='PriceSell',source=source,legend=value('Sell'),line_width=2, color='red')
    p2.circle(x='myx', y='PriceSell',source=source,line_width=2,color='orange')
    
    #Incorporate lables to know the Buy / Sell prices
    p2labels1 = LabelSet(x='myx', y='PriceBuy', text='PriceBuy', y_offset=10,x_offset=-7,
                      text_font_size="8pt", text_color="green",text_font_style="bold",
                      source=source, text_align='center')
    p2.add_layout(p2labels1)
    
    p2labels2 = LabelSet(x='myx', y='PriceSell', text='PriceSell', y_offset=20,x_offset=-7,
                      text_font_size="8pt", text_color="orange",text_font_style="italic",
                      source=source, text_align='center')
    
    p2.add_layout(p2labels2)
    
    # Adding legend..
    p1.xgrid.grid_line_color = None
    p1.legend.location = "top_left"
    p1.legend.orientation = "horizontal"
    p1.xaxis.major_label_orientation = 1
    p1.xaxis.major_label_standoff=10 #This keeps x-axis label away from the line
    
    p2.legend.location = "top_left"
    p2.legend.orientation = "horizontal"
    p2.xaxis.major_label_orientation = 1

    #Append to the object
    prow=row([p1,p2])
    prows.append(prow)
    
    #Increment the counter
    count += 1

#Display all the scrips in the form of charts, in a single shot. Thus, reducing time to filter and analyse.
show(column(*prows))
