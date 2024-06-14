import pandas as pd
import numpy as np
import altair as alt

# Read in the excel file (male) downloaded from website
df_raw_male = pd.read_excel("Table 110-01001_male.xlsx") 
df_raw_male.drop(index=df_raw_male.index[:4], inplace=True)
df_raw_male.drop(index=df_raw_male.index[1134:], inplace=True)
df_raw_male = df_raw_male.reset_index()
df_raw_male.drop(['index', 'Table 110-01001 : Population by Sex and Age Group','Unnamed: 1','Unnamed: 2'], axis=1, inplace=True)
df_raw_male.rename(columns={'Unnamed: 3': 'Age', 'Unnamed: 4': 'Male'}, inplace=True)
df_raw_male['Male']=df_raw_male['Male'].astype(float)*1000
years = [year for year in range(1961, 2024) for _ in range(18)]
df_raw_male['Year']=years
new_order = ['Year', 'Age', 'Male']
df_raw_male = df_raw_male[new_order]

# Read in the excel file (male) downloaded from website
df_raw_female = pd.read_excel("Table 110-01001_female.xlsx") 
df_raw_female.drop(index=df_raw_female.index[:4], inplace=True)
df_raw_female.drop(index=df_raw_female.index[1134:], inplace=True)
df_raw_female = df_raw_female.reset_index()
df_raw_female.drop(['index', 'Table 110-01001 : Population by Sex and Age Group','Unnamed: 1','Unnamed: 2'], axis=1, inplace=True)
df_raw_female.rename(columns={'Unnamed: 3': 'Age', 'Unnamed: 4': 'Female'}, inplace=True)
df_raw_female['Female']=df_raw_female['Female'].astype(float)*1000
df_raw_female['Year']=years
new_order = ['Year', 'Age', 'Female']
df_raw_female = df_raw_female[new_order]

# Merge male and female datasets
df = pd.merge(df_raw_male, df_raw_female, on=['Year', 'Age'], how='left')

# Calculate total population by year
df['Both']=df['Male']+df['Female']
df_total=df.groupby(['Year']).agg({'Both':'sum'}).reset_index()
df_total['Year2']=df_total['Year']

# Plot an interactive population pyramid
# Set the interactive slider, from 1961 to 2023
slider = alt.binding_range(min=1961, max=2023, step=1)
select_year = alt.selection_point(name=" ",fields=['Year'],
                                   bind=slider, value=2000)

# Fix the ordering of the age group to be displayed in the population pyramid
age_order = ['≥85','80 - 84','75 - 79','70 - 74','65 - 69','60 - 64','55 - 59','50 - 54',
              '45 - 49','40 - 44','35 - 39','30 - 34','25 - 29','20 - 24','15 - 19','10 - 14','5 - 9','0 - 4']

# Set up the base file
base = alt.Chart(df).add_params(
    select_year
).transform_filter(
    select_year
)    

# Create the right side of population pyramid (female population)
right=base.mark_bar(size=18).encode(
    x=alt.X(
        'Female:Q',
        axis=alt.Axis(tickCount=5, title='Female Population'),
        scale=alt.Scale(domain=(0,400000))
    ),
    y=alt.Y(
        'Age:O',
        axis=None,
        sort=age_order
    ),
    color=alt.value(
    'lightcoral'
    )
)

# Create the left side of population pyramid (male population)
left=base.mark_bar(size=18).encode(
    x=alt.X(
        'Male:Q',
        axis=alt.Axis(tickCount=5, title='Male Population'),
        sort='descending',
        scale=alt.Scale(domain=(0,400000))
    ),
    y=alt.Y(
        'Age:O',
        axis=None,
        sort=age_order
    ),
    color=alt.value(
    'cornflowerblue'
    )
)

# Create the middle part of the population pyramid (displaying the 18 age groups)
middle = base.encode(
    y=alt.Y('Age:O', axis=None, sort=age_order),
    text=alt.Text('Age:O'),
).mark_text().properties(width=20)

# Prepare bar chart of total population from 1961 to 2020 (shown at the bottom of the pyramid)
bottom=alt.Chart(df_total).mark_bar(size=8).encode(
    x=alt.X(
        'Year2:N',
        axis=alt.Axis(tickCount=5, title='Year')
    ),
    y=alt.Y(
        'Both:Q',
        axis=alt.Axis(tickCount=5, title='Total Population')
    ),
    color=alt.condition(
        select_year,  
        alt.value('darkred'),     
        alt.value('lightgray')   
    )
).add_params(select_year
).properties(width=680)

text2 = alt.Chart(df_total).mark_text(
    align='left'
).encode(alt.Text('Both:Q'), alt.X('Year2:N'))

text2Above = text2.transform_filter(select_year).mark_text(
    align='center',
    color='darkred',
    baseline='middle',
    fontSize=12,
    fontWeight='bold',
    dy=-142
)

# Combine everything to form the interactive population pyramid
bottom2 = bottom + text2Above

top=left|middle|right

final_chart=alt.vconcat(top,bottom2).configure_view(strokeWidth=0
     ).properties(title=alt.TitleParams(text=["Population Pyramid of Hong Kong"," "], anchor='middle', 
                                        fontSize=20, fontWeight='bold', subtitle="Age Group", subtitleFontWeight='bold',
                                        subtitleFontSize=11, dx=32)
     )

final_chart.save('pop_pyramid.html')

