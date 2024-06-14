import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Allow sufficient space for rendering animation
plt.rcParams['animation.embed_limit'] = 50

# Read in the dafa file
df_raw=pd.read_excel("Table 310-34101.xlsx")
df_raw['Wholesale, import & export trade']=df_raw['Wholesale']+df_raw['Import and export trade']
df_raw['Warehousing, courier and other transportation services']=df_raw['Warehousing and other transportation services']+df_raw['Postal and courier services']
df_raw.drop(columns=['Wholesale', 'Import and export trade', 'Warehousing and other transportation services', 'Postal and courier services'],inplace=True)
df_raw.set_index('Year',inplace=True)

# Color map used
colors = plt.cm.tab20(np.linspace(0, 1, 21))

# Plot 'bar chart race'
def nice_axes(ax):
    ax.set_facecolor('.9')
    ax.tick_params(labelsize=5, length=0)
    ax.grid(True, axis='x', color='white')
    ax.set_axisbelow(True)
    [spine.set_visible(False) for spine in ax.spines.values()]

def prepare_data(df, steps=5):
    df = df.reset_index()
    df.index = df.index * steps
    last_idx = df.index[-1] + 1
    df_expanded = df.reindex(range(last_idx))
    df_expanded['Year'] = df_expanded['Year'].fillna(method='ffill')
    df_expanded = df_expanded.set_index('Year')
    df_rank_expanded = df_expanded.rank(axis=1, method='first')
    df_expanded = df_expanded.interpolate()
    df_rank_expanded = df_rank_expanded.interpolate()
    return df_expanded, df_rank_expanded

df_expanded, df_rank_expanded = prepare_data(df_raw)

labels=['Agriculture, fishing, mining & quarrying',
        'Manufacturing',
        'Electricity, gas & water supply',
        'Construction',        
        'Retail trade',
        'Accommodation services',
        'Food & beverage services',
        'Land transport',
        'Water transport',
        'Air transport',
        'Financing',
        'Insurance',
        'Real estate',
        'Telecommunications',
        'Other information & communications services',
        'Professional & business services',
        'Public administration',
        'Social & personal services',
        'Ownership of premises',
        'Wholesale, import & export trade',
        'Warehousing, courier & other transport services']

def init():
    ax.clear()
    nice_axes(ax)
    ax.set_xlabel('(HK$ million)', fontsize=5)
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=5, which='major', pad=10)
    ax.set_title(
        'Evolving Economic Landscape of Hong Kong:\nNominal Value Added at Basic Price by Sector (1980 – 2022)',
        fontsize=10)

def update(i):
    ax.clear()
    nice_axes(ax)
    ax.set_xlabel('(HK$ million)', fontsize=5)
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=5, which='major', pad=10)
    ax.set_title(
        'Evolving Economic Landscape of Hong Kong:\nNominal Value Added at Basic Price by Sector (1980 – 2022)',
        fontsize=10)
    y = df_rank_expanded.iloc[i]
    width = df_expanded.iloc[i]
    total = width.sum()
    bars = ax.barh(y=y, width=width, color=colors, tick_label=labels)
    text_objects = []

    for bar, label in zip(bars, labels):
        width_size = bar.get_width()  # Get the width of the bar
        share = (width_size / total) * 100  # Calculate the percentage share
        label_x_pos = width_size + 0.5  # Offset the label a little bit to the right for visibility
        formatted_width = format(int(width_size), ',')
        text = ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2, f"{formatted_width} ({share:.1f}%)", va='center', fontsize=5)
        text_objects.append(text)
    
        # Load the corresponding emoji image for each label
        emoji_path = f'emoji_{labels.index(label)+1}.png'  # Update path and naming convention as needed
        emoji_img = plt.imread(emoji_path)
        imagebox = OffsetImage(emoji_img, zoom=0.1)  # Adjust zoom to fit the size of your plot

        ab = AnnotationBbox(imagebox, (-20, bar.get_y() + bar.get_height() / 2), frameon=False, box_alignment=(1.25, 0.5))
        ax.add_artist(ab)

    total_text = ax.text(0.95, 0.05, f'Total Nominal GDP: HK${format(int(total), ",")} million', transform=ax.transAxes,
                         horizontalalignment='right', verticalalignment='bottom', color='black', fontsize=10)    
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    year = df_expanded.index[i]
    ax.text(0.95, 0.125, f'{int(year)}', transform=ax.transAxes,
            horizontalalignment='right', verticalalignment='bottom', color='black', fontsize=12)
    
fig = plt.Figure(figsize=(8, 4), dpi=144)
fig.subplots_adjust(left=0.25)
ax = fig.add_subplot()
anim = FuncAnimation(fig=fig, func=update, init_func=init, frames=len(df_expanded), 
                     interval=150, repeat=False)

# Write the content to an html file
html_content = anim.to_jshtml()
with open('sector_va.html', 'w') as f:
    f.write(html_content)