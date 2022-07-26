# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

rawData_df = pd.read_json("transaction-data-adhoc-analysis.json")

"""# Data Cleaning"""

cleanedData_df = rawData_df.copy()
cleanedData_df['transaction_date'] = pd.to_datetime(rawData_df['transaction_date'])
cleanedData_df['birthdate'] = pd.to_datetime(rawData_df['birthdate'])

cleanedData_df['age'] = round((pd.Timestamp.now() - cleanedData_df['birthdate'])  / np.timedelta64(1, 'Y'))

cleanedData_df['transaction_items'] = cleanedData_df['transaction_items'].apply(lambda x: x.split(';'))
cleanedData_df = cleanedData_df.explode('transaction_items').reset_index(drop=True)

cleanedData_df['transaction_amount'] = cleanedData_df['transaction_items'].apply(lambda x: int(x.split(',')[-1].strip('(x)')))
cleanedData_df['transaction_items'] = cleanedData_df['transaction_items'].apply(lambda x: x.split(',')[0] + '/' + x.split(',')[1])

priceList_df = cleanedData_df[cleanedData_df['transaction_amount']==1].groupby(cleanedData_df['transaction_items'])['transaction_value'].agg(min)

cleanedData_df['transaction_value'] = cleanedData_df['transaction_items'].apply(lambda x: priceList_df[x]) * cleanedData_df['transaction_amount']

priceList_df

cleanedData_df

"""# Item Count Sold Per Month"""

itemCountPerMonth_df = cleanedData_df[['transaction_items','transaction_value','transaction_date','transaction_amount']].copy()
itemCountPerMonth_df['transaction_month'] = itemCountPerMonth_df['transaction_date'].apply(lambda x: x.month)
itemCountPerMonth_table = pd.pivot_table(itemCountPerMonth_df, index=['transaction_month'], columns=['transaction_items'], values=['transaction_amount'], aggfunc=sum, fill_value=0)

itemCountPerMonth_table

itemCountPerMonth_table.plot(subplots=True, layout=(3,3), figsize=(25,10))

itemCountPerMonth_table.plot.line(figsize=(20,10))

"""# Sales Value per Item per Month"""

salesPerItemPerMonth_df = itemCountPerMonth_df.copy()
salesPerItemPerMonth_table = pd.pivot_table(salesPerItemPerMonth_df, index=['transaction_month'], columns=['transaction_items'], values=['transaction_value'], aggfunc=sum, fill_value=0)

salesPerItemPerMonth_table

salesPerItemPerMonth_table.plot(subplots=True, layout=(3,3), figsize=(20,10))

salesPerItemPerMonth_table.plot.line(figsize=(20,10))

"""# Total Sales per Month"""

totalSalesPerMonth_df = itemCountPerMonth_df.copy()
totalSalesPerMonth_table = pd.pivot_table(salesPerItemPerMonth_df, index=['transaction_month'], values=['transaction_value'], aggfunc=sum, fill_value=0)

totalSalesPerMonth_table

totalSalesPerMonth_table.plot(figsize=(20,10))

"""# Monthly Repeaters, Inactives, and Engaged"""

monthlyUsers_df = cleanedData_df[['name','transaction_date']].copy()
monthlyUsers_df['transaction_month'] = monthlyUsers_df['transaction_date'].apply(lambda x: x.month)

monthlyUsers_table = pd.pivot_table(monthlyUsers_df, index=['transaction_month'], columns=['name'], aggfunc=any, fill_value=False)

monthlyUsers_table = pd.DataFrame({
    'repeaters':monthlyUsers_table.apply(lambda x: [False if i==1 else (True if x[i-1] and x[i] else False) for i in x.index]).transpose().sum(),
    'inactive':monthlyUsers_table.apply(lambda x: [False if i==1 else ((True if x[i]==False else False) if any(x[:i]) else False) for i in x.index]).transpose().sum(),
    'engaged':monthlyUsers_table.apply(lambda x: [True if all(x[:i]) else False for i in x.index]).transpose().sum()
  }).transpose()

monthlyUsers_table

monthlyUsers_table.transpose().plot.line(figsize=(20,10))

monthlyUsers_table.transpose().plot(subplots=True, layout=(3,1), figsize=(25,10))

"""# Item Count per Age Group per Month"""

agePerItemPerMonth_df = cleanedData_df[['transaction_items','transaction_amount','age','transaction_date']].copy()
agePerItemPerMonth_df['transaction_month'] = agePerItemPerMonth_df['transaction_date'].apply(lambda x: x.month)

agePerItemPerMonth_df['age_group'] = agePerItemPerMonth_df['age'].apply(
    lambda x: 'Child' if x<=14 else ('Youth' if 15<=x<=24 else ('Adult' if 25<=x<=64 else 'Senior'))
  )

agePerItemPerMonth_table = pd.pivot_table(agePerItemPerMonth_df, index=['transaction_month'], columns=['age_group','transaction_items'], values=['transaction_amount'], aggfunc=sum, fill_value=0)
agePerItemPerMonth_table.columns = agePerItemPerMonth_table.columns.droplevel()

agePerItemPerMonth_table

agePerItemPerMonth_table['Child']

agePerItemPerMonth_table['Child'].plot(figsize=(20,10))

agePerItemPerMonth_table['Youth']

agePerItemPerMonth_table['Youth'].plot(figsize=(20,10))

agePerItemPerMonth_table['Adult']

agePerItemPerMonth_table['Adult'].plot(figsize=(20,10))

agePerItemPerMonth_table['Senior']

agePerItemPerMonth_table['Senior'].plot(figsize=(20,10))
