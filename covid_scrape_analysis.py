import re
import requests
import pandas as pd
import numpy as np
from time import sleep
from bs4 import BeautifulSoup

state_dir = "data/"

base_url = 'https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/'

home_page = requests.get(base_url)

home_page.status_code
home_page.content

soup = BeautifulSoup(home_page.text, 'html.parser')



state_urls = {}

all_states = soup.find_all('a', class_='MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorInherit')

all_states_text = []

for state in all_states: 
    all_states_text.append(state.text)

all_states_links = []

for state in all_states:       
    all_states_links.append('https://usafacts.org' + state['href'])

for i in range(len(all_states_text)): 
    state_urls[all_states_text[i]] = all_states_links[i]

state_urls


if len(state_urls.keys()) != 51 or state_urls["District of Columbia"] != "https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/state/district-of-columbia":
    print("urls need review")
else:
    print("urls look good")



for state, url in state_urls.items():
    

    r = requests.get(url)
    

    with open(state_dir + state, 'w') as f:
        f.write(r.text)
    
    sleep(2) 

state_info = [(state, state_dir + state) for state in state_urls.keys()]


def load_covid_data(state_info):

    covid_data = {}
    
    for state in state_info: 
        
        with open(state[1]) as f: 
            read_data = f.read()
            
        soup = BeautifulSoup(read_data, 'html.parser')
        
        counties = soup.find_all('th', scope="row")
        
        counties_list = []
        
        for i, county in enumerate(counties): 
            if 1 < i:
                counties_list.append(county.text)
        
        with open(state[1]) as f2: 
            read_data2 = f2.read()

        soup2 = BeautifulSoup(read_data2, 'html.parser')
      
        counties_info = soup2.find_all('td', scope="col")

        counties_info_list = []
        
        for info in counties_info: 
            counties_info_list.append(info.text)
        county_dict = dict()
        
        county_dict = {}
        

        for i in range(len(counties_list)): 
        
            new_dict = dict()
            new_dict = {}
            
            new_dict['cases'] = counties_info_list[i * 3]
            new_dict['deaths'] = counties_info_list[i*3 + 1]
            new_dict['per100k'] = counties_info_list[i*3 + 2]
            
            county_dict[counties_list[i]] = new_dict
        
        covid_data[state[0]] = county_dict
        
    # END OF YOUR CODE HERE
    
    return covid_data



covid_data = load_covid_data(state_info)



def convert_to_pandas(covid_data):
    
    # YOUR CODE HERE
    counties = []
    for state_node in covid_data.items():
        for county_node in state_node[1].items(): 
        
            #initialize the dictionary
            county = {} #{key: value}
            county['county'] = county_node[0]
            county['state'] = state_node[0]
            county['# total covid cases'] = int(county_node[1]['cases'].replace(',',''))
            county['# covid cases per 100k'] = int(float(county_node[1]['per100k'].replace(',','')))
            county['# covid deaths'] = int(county_node[1]['deaths'].replace(',',''))
            counties.append(county)


    covid_df = pd.DataFrame(counties)

    
    return covid_df




covid_df = convert_to_pandas(covid_data)
covid_df


def calculate_county_stats2(covid_df):
    max_id = covid_df['# covid cases per 100k'].idxmax()
    min_id = covid_df['# covid cases per 100k'].idxmin()
    
    ldr = str(covid_df['# covid cases per 100k'][max_id])
    hdr = str(covid_df['# covid cases per 100k'][min_id])
    
    ct_ldr = covid_df['county'][max_id]
    ct_hdr = covid_df['county'][min_id]
    
    st_ldr = covid_df['state'][max_id]
    st_hdr = covid_df['state'][min_id]
    
    tied_counties = covid_df.loc[covid_df['# covid cases per 100k'] == int(hdr)]['county']
    tied_states = covid_df.loc[covid_df['# covid cases per 100k'] == int(hdr)]['state']
    
    tied_counties_list = tied_counties.values.tolist()
    tied_states_list = tied_states.values.tolist()
    
    outstring = ''
    
    for i in range(len(tied_counties_list) - 1): 
        outstring += tied_counties_list[i] + ' (' + tied_states_list[i] + '), '
    
    print(outstring + 'and ' + ct_hdr + " (" + st_hdr + ") has the lowest rate of confirmed COVID cases: " + hdr + " per 100k")
    print(ct_ldr + " (" + st_ldr + ") has the highest rate of confirmed COVID cases: " + ldr + " per 100k")



calculate_county_stats2(covid_df)


def calculate_state_deaths2(covid_df):
    
    new_covid_df = covid_df.groupby('state').sum()
    low_state = new_covid_df['# covid deaths'].idxmin()
    high_state = new_covid_df['# covid deaths'].idxmax()
    
    low = str(new_covid_df['# covid deaths'][low_state])
    high = str(new_covid_df['# covid deaths'][high_state])
    
    print(low_state +  " has the fewest COVID deaths: " + low)
    print(high_state + " has the most COVID deaths: " + high)



calculate_state_deaths2(covid_df)



def calculate_state_deathrate2(covid_df):
    
    new_covid_df = covid_df
    new_covid_df["pop"] = new_covid_df["# total covid cases"] / new_covid_df['# covid cases per 100k'] * 100000
    new_covid_df = new_covid_df.groupby('state').sum()
    new_covid_df['death_rate'] = new_covid_df['pop'] / new_covid_df['# covid deaths']
    
    
    high_state = new_covid_df['death_rate'].idxmin()
    low_state = new_covid_df['death_rate'].idxmax()
    
    low = str(int(new_covid_df['death_rate'][low_state]))
    high = str(int(new_covid_df['death_rate'][high_state]))
    
    print(low_state + " has the lowest COVID death rate; 1 out of every " + low + " people has died")
    print(high_state + " has the highest COVID death rate; 1 out of every " + high + " people has died")




calculate_state_deathrate2(covid_df)



def add_death_stats(covid_df):
    
    covid_df['# covid deaths per 100k'] = covid_df['# covid deaths'] / (covid_df["# total covid cases"] / covid_df['# covid cases per 100k'])
    covid_df['case_fatality_rate'] = covid_df['# covid deaths per 100k'] / covid_df['# covid cases per 100k']
    
    covid_df = covid_df.sort_values(by=['case_fatality_rate'])
    
    return covid_df




covid_updated = add_death_stats(covid_df)
covid_updated


def merge_data(covid_updated, filepath):
    
    election_df = pd.read_csv(filepath)
    updated_df = covid_updated.merge(election_df,on=['state', 'county']).drop(columns=['fipscode', 'population'])
    
    return updated_df



merged = merge_data(covid_updated, 'election2016_by_county.csv')


len(covid_updated.index) - len(merged.index)

df_dropped = covid_updated[~covid_updated.county.isin(merged.county)]
df_dropped.iloc[:, 0:2]

merged = merged[merged['# covid deaths'] != 0]

merged.describe()


def partition_df(df, column_name, min, max):
    df = df[df[column_name] >= min]
    df = df[df[column_name] <= max]
    return df

#partition_df(merged, 'density', 0.0, 5000.0).describe()

print(partition_df(merged, 'minority', 0.0, 5.0).describe())
#partition_df(merged, 'minority', 0.5, 10.0).describe()
#partition_df(merged, 'minority', 10.0, 15.0).describe()
#partition_df(merged, 'minority', 15.0, 20.0).describe()
#partition_df(merged, 'minority', 20.0, 25.0).describe()
#partition_df(merged, 'minority', 25.0, 30.0).describe()

#partition_df(merged, 'trump', 0.0, 30.0).describe()
#partition_df(merged, 'trump', 30.0, 50.0).describe()
#partition_df(merged, 'trump', 50.0, 70.0).describe()

#partition_df(merged, 'income', 0.0, 70000.0).describe()
#partition_df(merged, 'income', 70000.0, 1000000.0).describe()

#partition_df(merged, 'nodegree', 0.0, 5.0).describe()
#partition_df(merged, 'nodegree', 5.0, 10.0).describe()
#partition_df(merged, 'nodegree', 10.0, 15.0).describe()


bins = [0, 38000, 45000, 52000, 200000]
names = ['income-group-1', 'income-group-2', 'income-group-3', 'income-group-4']
d = dict(enumerate(names, 1))
merged['income group'] = np.vectorize(d.get)(np.digitize(merged['income'], bins))
print(merged)

merged = merged.groupby(['income group']).mean()
print(merged)