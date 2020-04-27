'''
The script organizes the super messy census data by name, state and type.
Place types include: 'city', 'town', 'village', 'borough', and 'city and borough'
'''
from tqdm import tqdm
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv('sub-est2018_all.csv', encoding = "ISO-8859-1")
    df_result = pd.DataFrame(columns=['name', 'state', 'type', 'population'])
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        state = row['STNAME']
        name = row['NAME']
        pop = row['POPESTIMATE2018']
        if name.endswith('city'):
            name = name[:-len(' city')]
            df_result = df_result.append({'name':name, 'state':state, 'type':'city', 'population':pop}, ignore_index=True)
        elif name.endswith('town'):
            name = name[:-len(' town')]
            df_result = df_result.append({'name':name, 'state':state, 'type':'town', 'population':pop}, ignore_index=True)
        elif name.endswith('village'):
            name = name[:-len(' village')]
            df_result = df_result.append({'name':name, 'state':state, 'type':'village', 'population':pop}, ignore_index=True)
        elif name.endswith('borough'):
            name = name[:-len(' borough')]
            df_result = df_result.append({'name':name, 'state':state, 'type':'borough', 'population':pop}, ignore_index=True)
        elif name.endswith('city and borough'):
            name = name[:-len(' city and borough')]
            df_result = df_result.append({'name':name, 'state':state, 'type':'city and borough', 'population':pop}, ignore_index=True)
    # order places in a state by population
    df_result_grouped = df_result.groupby(by='state', sort=False)
    df_result2 = pd.DataFrame(columns=['name', 'state', 'type', 'population'])
    for name, df_temp in df_result_grouped:
        df_result2 = df_result2.append(df_temp.sort_values(by=['population'], ascending=False), ignore_index=True)
    df_result2.to_csv('US_places2.csv', index=False)
