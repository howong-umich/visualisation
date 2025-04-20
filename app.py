import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, State
import textwrap
from flask_caching import Cache  # Import caching

# Initialize the Dash app with custom styles
app = Dash(__name__)
server = app.server

# Add caching to improve performance
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

# Cache timeout (in seconds)
TIMEOUT = 60 * 60  # 1 hour

# Define flag data for countries
country_codes = {
    'Argentina': 'ar',
    'Australia': 'au',
    'Austria': 'at',
    'Belgium': 'be',
    'Brazil': 'br',
    'Bulgaria': 'bg',
    'Canada': 'ca',
    'Chile': 'cl',
    'Colombia': 'co',
    'Costa Rica': 'cr',
    'Croatia': 'hr',
    'Czechia': 'cz',
    'Denmark': 'dk',
    'Estonia': 'ee',
    'Finland': 'fi',
    'France': 'fr',
    'Germany': 'de',
    'Greece': 'gr',
    'Hong Kong': 'hk',
    'Hungary': 'hu',
    'Iceland': 'is',
    'Indonesia': 'id',
    'Ireland': 'ie',
    'Israel': 'il',
    'Italy': 'it',
    'Japan': 'jp',
    'Korea': 'kr',
    'Latvia': 'lv',
    'Lithuania': 'lt',
    'Luxembourg': 'lu',
    'Mexico': 'mx',
    'Netherlands': 'nl',
    'New Zealand': 'nz',
    'Norway': 'no',
    'Peru': 'pe',
    'Poland': 'pl',
    'Portugal': 'pt',
    'Romania': 'ro',
    'Singapore': 'sg',
    'Slovak Republic': 'sk',
    'Slovenia': 'si',
    'South Africa': 'za',
    'Spain': 'es',
    'Sweden': 'se',
    'Switzerland': 'ch',
    'Thailand': 'th',
    'Turkiye': 'tr',
    'United Kingdom': 'gb',
    'United States': 'us'
}

# Define custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Well-being Dashboard</title>
        {%metas%}
        {%favicon%}
        {%css%}
        <style>
            * {
                font-family: Arial, Helvetica, sans-serif;
            }
            .dropdown-label {
                font-weight: bold;
                margin-bottom: 8px;
            }
            .chart-container {
                margin-bottom: 40px;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }
            .Select {
                font-family: Arial, Helvetica, sans-serif;
            }
            .checkbox-container {
                margin-top: 15px;
                margin-bottom: 15px;
                font-weight: bold;
            }
            .notes-section {
                margin-top: 20px;
                margin-bottom: 30px;
                padding: 15px;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 0.9em;
                color: #555;
            }
            .flag-option {
                display: flex;
                align-items: center;
            }
            .flag-image {
                width: 20px;
                height: 15px;
                margin-right: 10px;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the app layout
app.layout = html.Div([
    html.H1("Well-being Dashboard"),
    
    html.Div([
        html.Div([
            html.Label("Select Economy:", className="dropdown-label"),
            dcc.Dropdown(
                id='country-select',
                options=[],  # Will be populated after loading data
                placeholder="Please select an economy"
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label("Select Welfare Domain:", className="dropdown-label"),
            dcc.Dropdown(
                id='domain-select',
                options=[],  # Will be populated after loading data
                placeholder="Please select a welfare domain"
            )
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ], style={'marginBottom': '15px'}),
    
    # Add international comparison checkbox
    html.Div([
        dcc.Checklist(
            id='intl-comparison-checkbox',
            options=[{'label': 'Show International Comparison', 'value': 'show'}],
            value=[]  # Empty list means not checked
        )
    ], className='checkbox-container'),
    
    # Add notes section
    html.Div([
        html.P([
            "Data source for economies other than Hong Kong and Singapore: ",
            html.A("OECD Data Explorer", 
                  href="https://data-explorer.oecd.org/vis?fs[0]=Topic%2C1%7CSociety%23SOC%23%7CWell-being%20and%20beyond%20GDP%23SOC_WEL%23&pg=0&fc=Topic&bp=true&snb=26&df[ds]=dsDisseminateFinalDMZ&df[id]=DSD_HSL%40DF_HSL_CWB&df[ag]=OECD.WISE.WDP&df[vs]=1.1&dq=......&pd=%2C&to[TIME_PERIOD]=false",
                  target="_blank")
        ]),
        html.P("For Hong Kong and Singapore, data is obtained or derived from websites of various government departments and tertiary institutes."),
        html.P("Data sources have different geographical coverage and data collection periods, so please make comparisons with caution.")
    ], className="notes-section"),
    
    html.Div(id="charts-container")
], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})

# Cache the data loading function
@cache.memoize(timeout=TIMEOUT)
def load_data():
    return pd.read_excel('well_being_data.xlsx')  #Update the filename or filepath if needed

# Load data and populate dropdowns
@app.callback(
    [Output('country-select', 'options'),
     Output('domain-select', 'options')],
    [Input('country-select', 'id')]  # Dummy input to trigger on load
)
def populate_dropdowns(_):
    # Load the data using the cached function
    df = load_data()
    
    # Get unique countries (sorted alphabetically)
    countries = sorted(df['Reference area'].unique())

    # Create country options with flags
    country_options = []

    for country in countries:
        country_code = country_codes.get(country, '').lower()
        
        if country_code:
            # Use flag from assets folder
            flag_path = f'/assets/flags/{country_code}.png'
            country_options.append({
                'label': html.Div([
                    html.Img(src=flag_path, className='flag-image'),
                    html.Span(country)
                ], className='flag-option'),
                'value': country
            })
        else:
            country_options.append({'label': country, 'value': country})
    
    # Create a custom dropdown component
    country_dropdown = dcc.Dropdown(
        id='country-select',
        options=country_options,
        placeholder="Please select an economy",
        optionHeight=40  # Taller options to accommodate flags
    )

    #country_options = [{'label': country, 'value': country} for country in countries]
    
    # Get unique domains (sorted by DOMAIN value)
    domains = df[['DOMAIN', 'Domain']].drop_duplicates()
    domains = domains.sort_values('DOMAIN')
    domain_options = [{'label': domain, 'value': domain} for domain in domains['Domain'].tolist()]
    
    return country_options, domain_options

@app.callback(
    Output('charts-container', 'children'),
    [Input('country-select', 'value'),
     Input('domain-select', 'value'),
     Input('intl-comparison-checkbox', 'value')]
)
def update_charts(selected_country, selected_domain, intl_comparison_values):
    # If either dropdown is not selected, return empty
    if not selected_country or not selected_domain:
        return html.Div("Please select both an economy and a welfare domain to view data.",
                        style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})
    
    # Load data from cache
    df = load_data()
    
    # If international comparison is enabled (checklist has 'show' value)
    if 'show' in intl_comparison_values:
        return create_international_comparison(df, selected_country, selected_domain)
    
    # Otherwise, proceed with regular charts
    # Filter data based on selections
    filtered_data = df[(df['Reference area'] == selected_country) & (df['Domain'] == selected_domain)]
    
    if filtered_data.empty:
        return html.Div("No data available for the selected country and domain.", 
                        style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})
    
    # Group data by measure
    measure_groups = filtered_data.groupby('MEASURE')
    
    # Create charts for each measure
    chart_rows = []
    
    for measure, measure_data in measure_groups:
        # Get the measure name and name (for bold part)
        measure_name = measure_data['Measure'].iloc[0]
        measure_label = measure_data['Name'].iloc[0] if 'Name' in measure_data.columns else measure_name
        
        # Determine available breakdowns
        has_age_breakdown = any(measure_data['AGE'] != '_T')
        has_sex_breakdown = any(measure_data['SEX'] != '_T')
        has_education_breakdown = any(measure_data['EDUCATION_LEV'] != '_T')
        
        # Count the number of available breakdowns
        breakdown_count = sum([has_age_breakdown, has_sex_breakdown, has_education_breakdown])
        
        # Get total data
        total_data = measure_data[(measure_data['AGE'] == '_T') & 
                                 (measure_data['SEX'] == '_T') & 
                                 (measure_data['EDUCATION_LEV'] == '_T')]
        
        chart_components = []
        
        # If sex breakdown is available
        if has_sex_breakdown:
            sex_data = measure_data[(measure_data['SEX'] != '_T') & 
                                   (measure_data['AGE'] == '_T') & 
                                   (measure_data['EDUCATION_LEV'] == '_T')]
            
            sex_chart = create_chart_component(measure_label, measure_name, "by Sex", total_data, 
                                             sex_data, 'SEX', 'Sex', charts_in_row=breakdown_count)
            chart_components.append(sex_chart)
        
        # If age breakdown is available
        if has_age_breakdown:
            age_data = measure_data[(measure_data['AGE'] != '_T') & 
                                   (measure_data['SEX'] == '_T') & 
                                   (measure_data['EDUCATION_LEV'] == '_T')]
            
            age_chart = create_chart_component(measure_label, measure_name, "by Age", total_data, 
                                             age_data, 'AGE', 'Age', charts_in_row=breakdown_count)
            chart_components.append(age_chart)
        
        # If education breakdown is available
        if has_education_breakdown:
            education_data = measure_data[(measure_data['EDUCATION_LEV'] != '_T') & 
                                         (measure_data['SEX'] == '_T') & 
                                         (measure_data['AGE'] == '_T')]
            
            education_chart = create_chart_component(measure_label, measure_name, "by Education", 
                                                   total_data, education_data, 'EDUCATION_LEV', 
                                                   'Education level', charts_in_row=breakdown_count)
            chart_components.append(education_chart)
        
        # If no breakdowns or only total data is available
        if breakdown_count == 0 or (not total_data.empty and breakdown_count == 0):
            basic_chart = create_chart_component(measure_label, measure_name, None, total_data, 
                                               pd.DataFrame(), None, None, charts_in_row=1)
            chart_components.append(basic_chart)
        
        # If there are measure data with no total
        if total_data.empty and not has_sex_breakdown and not has_age_breakdown and not has_education_breakdown:
            basic_chart = create_chart_component(measure_label, measure_name, None, pd.DataFrame(), 
                                               measure_data, None, None, charts_in_row=1)
            chart_components.append(basic_chart)
        
        # Create a row for this measure's charts
        num_charts = len(chart_components)
        chart_width = f"{100 / num_charts}%" if num_charts > 0 else "100%"
        
        row = html.Div([
            html.Div(component, 
                   style={'width': chart_width, 'display': 'inline-block', 'verticalAlign': 'top'},
                   className="chart-container")
            for component in chart_components
        ], style={'marginBottom': '40px'})
        
        chart_rows.append(row)
    
    return html.Div(chart_rows)

def create_international_comparison(df, selected_country, selected_domain):
    """Create horizontal bar charts for international comparison"""
    # Filter data for the selected domain (all countries)
    domain_data = df[df['Domain'] == selected_domain]
    
    # Group by measure
    measure_groups = domain_data.groupby('MEASURE')
    
    comparison_charts = []
    
    for measure, measure_data in measure_groups:
        # Get measure details
        measure_name = measure_data['Measure'].iloc[0]
        measure_label = measure_data['Name'].iloc[0] if 'Name' in measure_data.columns else measure_name
        
        # Get unit of measure
        full_unit = measure_data['Unit of measure'].iloc[0]
        unit_of_measure = 'Percentage' if 'percentage' in full_unit.lower() else full_unit
        
        # Special handling for Life Expectancy - compare by sex instead of total
        # Check the 'Name' column for "Life Expectancy"
        if "Life expectancy" in measure_label:
            # Create male comparison with simplified title
            male_charts = create_sex_specific_comparison(measure_data, selected_country, measure_label, 
                                                      "Male", 'M', unit_of_measure)
            if male_charts:
                comparison_charts.append(male_charts)
                
            # Create female comparison with simplified title
            female_charts = create_sex_specific_comparison(measure_data, selected_country, measure_label, 
                                                        "Female", 'F', unit_of_measure)
            if female_charts:
                comparison_charts.append(female_charts)
        else:
            # For all other measures, use the standard total data approach
            # We only want the total data (no breakdowns)
            total_data = measure_data[(measure_data['AGE'] == '_T') & 
                                   (measure_data['SEX'] == '_T') & 
                                   (measure_data['EDUCATION_LEV'] == '_T')]
            
            if total_data.empty:
                continue
                
            # Get the selected country's data
            selected_country_data = total_data[total_data['Reference area'] == selected_country]
            
            # If there's no data for the selected country, skip this measure
            if selected_country_data.empty:
                continue
            
            # Get comparable years data
            earliest_year_info = find_comparable_year(total_data, selected_country, 'earliest')
            latest_year_info = find_comparable_year(total_data, selected_country, 'latest')
            
            # If only the selected country has data (no comparison possible), skip this measure
            if earliest_year_info['comparison_count'] < 2 and latest_year_info['comparison_count'] < 2:
                continue
            
            # Create a container for this measure's charts
            measure_container = html.Div(
                style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'justifyContent': 'space-between',
                    'marginBottom': '40px'
                }
            )
            
            charts_added = 0
            
            # If earliest and latest years are the same, only show the latest chart
            if earliest_year_info['year'] == latest_year_info['year']:
                # Create only latest year chart (which is the same as earliest)
                if latest_year_info['comparison_count'] >= 2:
                    latest_chart = create_comparison_chart(total_data, selected_country, 
                                                          measure_label, measure_name, 
                                                          latest_year_info, unit_of_measure)
                    
                    chart_div = html.Div(latest_chart, 
                                        style={
                                            'width': '70%', 
                                            'margin': '0 auto'
                                        },
                                        className="chart-container")
                    
                    measure_container.children = [chart_div]
                    charts_added = 1
            else:
                # Both charts might be needed
                chart_divs = []
                
                # Only add earliest chart if there's something to compare with
                if earliest_year_info['comparison_count'] >= 2:
                    earliest_chart = create_comparison_chart(total_data, selected_country, 
                                                            measure_label, measure_name, 
                                                            earliest_year_info, unit_of_measure)
                    
                    chart_divs.append(
                        html.Div(earliest_chart, 
                                style={'width': '48.5%'},
                                className="chart-container")
                    )
                    charts_added += 1
                
                # Only add latest chart if there's something to compare with
                if latest_year_info['comparison_count'] >= 2:
                    latest_chart = create_comparison_chart(total_data, selected_country, 
                                                          measure_label, measure_name, 
                                                          latest_year_info, unit_of_measure)
                    
                    chart_divs.append(
                        html.Div(latest_chart, 
                                style={'width': '48.5%'},
                                className="chart-container")
                    )
                    charts_added += 1
                
                # Add the charts to the measure container
                measure_container.children = chart_divs
            
            # Only add the container if we added at least one chart
            if charts_added > 0:
                comparison_charts.append(measure_container)
    
    if not comparison_charts:
        return html.Div("No comparable data available for international comparison.", 
                      style={'textAlign': 'center', 'color': '#666', 'padding': '50px'})
    
    return html.Div(comparison_charts)

def create_sex_specific_comparison(measure_data, selected_country, label, sex_display, sex_code, unit_of_measure):
    """Create sex-specific comparison charts for measures like Life Expectancy"""
    # Filter data for the specified sex
    sex_data = measure_data[(measure_data['AGE'] == '_T') & 
                         (measure_data['SEX'] == sex_code) & 
                         (measure_data['EDUCATION_LEV'] == '_T')]
    
    if sex_data.empty:
        return None
    
    # Get the selected country's data
    selected_country_data = sex_data[sex_data['Reference area'] == selected_country]
    
    # If there's no data for the selected country, skip
    if selected_country_data.empty:
        return None
    
    # Get comparable years data
    earliest_year_info = find_comparable_year(sex_data, selected_country, 'earliest')
    latest_year_info = find_comparable_year(sex_data, selected_country, 'latest')
    
    # If only the selected country has data (no comparison possible), skip
    if earliest_year_info['comparison_count'] < 2 and latest_year_info['comparison_count'] < 2:
        return None
    
    # Create a container for this measure's charts
    measure_container = html.Div(
        style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'space-between',
            'marginBottom': '40px'
        }
    )
    
    charts_added = 0
    
    # If earliest and latest years are the same, only show the latest chart
    if earliest_year_info['year'] == latest_year_info['year']:
        # Create only latest year chart (which is the same as earliest)
        if latest_year_info['comparison_count'] >= 2:
            latest_chart = create_comparison_chart(sex_data, selected_country, 
                                                  label, sex_display, 
                                                  latest_year_info, unit_of_measure)
            
            chart_div = html.Div(latest_chart, 
                                style={
                                    'width': '70%', 
                                    'margin': '0 auto'
                                },
                                className="chart-container")
            
            measure_container.children = [chart_div]
            charts_added = 1
    else:
        # Both charts might be needed
        chart_divs = []
        
        # Only add earliest chart if there's something to compare with
        if earliest_year_info['comparison_count'] >= 2:
            earliest_chart = create_comparison_chart(sex_data, selected_country, 
                                                    label, sex_display, 
                                                    earliest_year_info, unit_of_measure)
            
            chart_divs.append(
                html.Div(earliest_chart, 
                        style={'width': '48.5%'},
                        className="chart-container")
            )
            charts_added += 1
        
        # Only add latest chart if there's something to compare with
        if latest_year_info['comparison_count'] >= 2:
            latest_chart = create_comparison_chart(sex_data, selected_country, 
                                                  label, sex_display, 
                                                  latest_year_info, unit_of_measure)
            
            chart_divs.append(
                html.Div(latest_chart, 
                        style={'width': '48.5%'},
                        className="chart-container")
            )
            charts_added += 1
        
        # Add the charts to the measure container
        measure_container.children = chart_divs
    
    # Only return the container if we added at least one chart
    if charts_added > 0:
        return measure_container
    
    return None


def find_comparable_year(measure_data, selected_country, year_type):
    """Find a year with comparable data and return information about it"""
    # Get selected country's data
    selected_country_data = measure_data[measure_data['Reference area'] == selected_country]
    
    # Sort by time period
    selected_country_data = selected_country_data.sort_values('TIME_PERIOD')
    
    # Get all available years for the selected country
    available_years = selected_country_data['TIME_PERIOD'].tolist()
    
    # Find a year with comparable data
    target_year = None
    comparison_count = 0
    
    if year_type == 'earliest':
        # Try each year from earliest to latest
        for year in available_years:
            # Get all countries with data for this year
            year_data = measure_data[measure_data['TIME_PERIOD'] == year]
            # Count unique countries
            current_count = year_data['Reference area'].nunique()
            # If we have at least two countries (including the selected one)
            if current_count >= 2:
                target_year = year
                comparison_count = current_count
                break
        
        # If we couldn't find a year with multiple countries, just use the earliest
        if target_year is None and available_years:
            target_year = available_years[0]
            year_data = measure_data[measure_data['TIME_PERIOD'] == target_year]
            comparison_count = year_data['Reference area'].nunique()
            
        year_info = {
            'year': target_year,
            'comparison_count': comparison_count,
            'type': 'earliest'
        }
            
    else:  # latest
        # Try each year from latest to earliest
        for year in reversed(available_years):
            # Get all countries with data for this year
            year_data = measure_data[measure_data['TIME_PERIOD'] == year]
            # Count unique countries
            current_count = year_data['Reference area'].nunique()
            # If we have at least two countries (including the selected one)
            if current_count >= 2:
                target_year = year
                comparison_count = current_count
                break
        
        # If we couldn't find a year with multiple countries, just use the latest
        if target_year is None and available_years:
            target_year = available_years[-1]
            year_data = measure_data[measure_data['TIME_PERIOD'] == target_year]
            comparison_count = year_data['Reference area'].nunique()
            
        year_info = {
            'year': target_year,
            'comparison_count': comparison_count,
            'type': 'latest'
        }
    
    return year_info

def create_comparison_chart(measure_data, selected_country, label, measure, year_info, unit_of_measure):
    """Create a horizontal bar chart for international comparison for the selected country's earliest/latest year"""
    target_year = year_info['year']
    year_type = year_info['type']
    
    # If no target year was found, return empty chart
    if target_year is None:
        return dcc.Graph(
            figure=go.Figure().update_layout(
                title=f"No comparable data available for {selected_country}",
                height=450
            ),
            config={'displayModeBar': False}
        )
    
    # Filter to only include the target year
    year_data = measure_data[measure_data['TIME_PERIOD'] == target_year]
    
    # Create list of countries with data for this year
    countries_data = []
    
    for country, country_data in year_data.groupby('Reference area'):
        # Just take the first row as we're already filtered to a specific year
        data_row = country_data.iloc[0]
        
        countries_data.append({
            'Country': country,
            'Year': target_year,
            'Value': data_row['OBS_VALUE'],
            'IsSelected': country == selected_country
        })
    
    # Convert to DataFrame and sort by value (descending)
    comparison_df = pd.DataFrame(countries_data)
    comparison_df = comparison_df.sort_values('Value', ascending=False)
    
    # Get count of countries for subtitle
    country_count = len(comparison_df)
    
    # Create the horizontal bar chart
    fig = go.Figure()
    
    # Add bars for each country
    for _, row in comparison_df.iterrows():
        # Set color based on whether this is the selected country
        color = 'rgb(31, 119, 180)' if row['IsSelected'] else 'rgb(158, 202, 225)'
        
        fig.add_trace(go.Bar(
            x=[row['Value']],
            y=[row['Country']],
            orientation='h',
            marker=dict(color=color),
            name=row['Country'],
            showlegend=False,
            hovertemplate=
            '<b>%{y}</b><br>' +
            'Value: %{x}<br>' +
            'Year: ' + str(row['Year']) +
            '<extra></extra>'
        ))
    
    # Construct chart title with more intelligent line breaks
    year_label = "Earliest" if year_type == 'earliest' else "Latest"
    
    # Combine label and measure for title
    combined_title = f"{label}: {measure}"
    
    # Apply intelligent line breaks for long titles
    # If the title is very long, split it intelligently
    if len(combined_title) > 60:
        # First, find the colon that typically separates the label from description
        if ': ' in combined_title:
            parts = combined_title.split(': ', 1)
            title_line1 = f"<b>{parts[0]}</b>:"
            
            # Now see if we need to split the description further
            description = parts[1]
            if len(description) > 50:
                # Try to find a natural breaking point (around midpoint)
                mid_point = len(description) // 2
                # Look for spaces near the midpoint
                for i in range(mid_point - 10, mid_point + 10):
                    if i < len(description) and description[i] == ' ':
                        # Found a good breaking point
                        title_line2 = description[:i]
                        title_line3 = description[i+1:]
                        break
                else:
                    # If no good breaking point found, just split at midpoint
                    title_line2 = description[:mid_point]
                    title_line3 = description[mid_point:]
            else:
                # Description fits on one line
                title_line2 = description
                title_line3 = None
        else:
            # No colon, just split based on length
            mid_point = len(combined_title) // 2
            title_line1 = f"<b>{combined_title[:mid_point]}</b>"
            title_line2 = combined_title[mid_point:]
            title_line3 = None
    else:
        # Title fits on one line
        title_line1 = f"<b>{combined_title}</b>"
        title_line2 = None
        title_line3 = None
    
    # Construct the final title with line breaks
    if title_line3:
        title_part = f"{title_line1}<br>{title_line2}<br>{title_line3}"
    elif title_line2:
        title_part = f"{title_line1}<br>{title_line2}"
    else:
        title_part = title_line1
    
    # Add the year and comparison info as the last line
    comparison_info = f"{year_label} comparable data ({target_year}) - Comparison with {country_count-1} other economies"
    full_title = f"{title_part}<br><span style='font-size:0.7em;'>{comparison_info}</span>"
    
    # Calculate dynamic height based on number of countries
    chart_height = max(450, 100 + 20 * len(comparison_df))
    
    # Calculate top margin based on number of title lines (more lines need more space)
    # Reduced spacing by lowering the base margin and per-line addition
    title_lines = 2  # Minimum (includes comparison info line)
    if title_line2: title_lines += 1
    if title_line3: title_lines += 1
    top_margin = 60 + (13 * title_lines)  # Reduced from 80+(20*lines) to 60+(15*lines)
    
    # Add layout with slightly larger font size for title and reduced spacing
    fig.update_layout(
        title={
            'text': full_title,
            'y': 0.97,  # Moved up slightly from 0.97 to 0.98
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Arial', 'size': 18} 
        },
        xaxis=dict(
            title=unit_of_measure,
            titlefont={'family': 'Arial'},
            domain=[0, 1],  # Ensure x-axis takes full width
            automargin=True  # Auto-adjust margins if needed
        ),
        yaxis=dict(
            title='',  # No title for y-axis (countries)
            autorange="reversed",  # Reverse to have highest value at top
            titlefont={'family': 'Arial'},
            automargin=True  # Auto-adjust margins if needed
        ),
        margin=dict(l=120, r=30, t=top_margin, b=50),
        height=chart_height,
        font={'family': 'Arial'},
        # Reduce padding between elements
        bargap=0.15,  # Reduced from default
        plot_bgcolor='white',
        
        # Add more space for the chart content by adjusting the layout
        autosize=True
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False, 'responsive': True})


def create_chart_component(label, measure, breakdown_type, total_data, breakdown_data, 
                          breakdown_code, breakdown_label, charts_in_row=1):
    # Prepare data for the chart
    time_points = set()
    traces = []
    
    # Format unit of measure
    unit_of_measure = ''
    if not total_data.empty:
        full_unit = total_data['Unit of measure'].iloc[0]
        unit_of_measure = 'Percentage' if 'percentage' in full_unit.lower() else full_unit
    elif not breakdown_data.empty:
        full_unit = breakdown_data['Unit of measure'].iloc[0]
        unit_of_measure = 'Percentage' if 'percentage' in full_unit.lower() else full_unit
    
    # Count number of breakdowns to determine legend size
    breakdown_count = 1  # Start with 1 for Total
    
    # Add total data trace
    if not total_data.empty:
        years = total_data['TIME_PERIOD'].tolist()
        values = total_data['OBS_VALUE'].tolist()
        
        time_points.update(years)
        
        if len(years) >= 4:
            # Line chart
            traces.append(go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name='Total',
                line=dict(width=4),
                marker=dict(size=8),
                visible=True  # Always show total
            ))
        else:
            # Bar chart
            traces.append(go.Bar(
                x=years,
                y=values,
                name='Total',
                visible=True  # Always show total
            ))
    
    # Add breakdown data traces
    if not breakdown_data.empty:
        # Group by breakdown value
        if breakdown_code:
            breakdown_groups = breakdown_data.groupby(breakdown_label)
        else:
            breakdown_groups = breakdown_data.groupby('MEASURE')
        
        # Count breakdowns to estimate legend width
        breakdown_count += len(breakdown_groups)
        
        for breakdown_value, group_data in breakdown_groups:
            years = group_data['TIME_PERIOD'].tolist()
            values = group_data['OBS_VALUE'].tolist()
            time_points.update(years)
            
            if len(years) >= 4:
                # Line chart
                traces.append(go.Scatter(
                    x=years,
                    y=values,
                    mode='lines+markers',
                    name=breakdown_value,
                    marker=dict(size=6),
                    visible='legendonly'  # Hide breakdowns initially
                ))
            else:
                # Bar chart
                traces.append(go.Bar(
                    x=years,
                    y=values,
                    name=breakdown_value,
                    visible='legendonly'  # Hide breakdowns initially
                ))
    
    # Sort time points
    time_points_list = sorted(list(time_points))
    
    # Create the figure
    fig = go.Figure(data=traces)
    
    # Create title with formatting
    # Format: "{Bold Name}: {Measure}" + optional "(by {breakdown})"
    breakdown_suffix = f" ({breakdown_type})" if breakdown_type else ""
    full_title = f"<b>{label}</b>: {measure}{breakdown_suffix}"
    
    # Adjust max line length based on number of charts in row
    # For a single chart, allow longer lines
    if charts_in_row == 1:
        max_line_length = 80  # More characters per line for single chart
    else:
        # For multiple charts, reduce line length proportionally
        max_line_length = int(80 / charts_in_row)
        # Ensure minimum readability
        max_line_length = max(max_line_length, 30)
    
    # Use textwrap for intelligent word wrapping
    wrapped_lines = textwrap.wrap(full_title, width=max_line_length, break_long_words=False)
    
    # Join lines with HTML line breaks, preserving HTML tags
    wrapped_title = '<br>'.join(wrapped_lines)
    
    # Calculate legend dimensions based on number of items
    # More items need more space for horizontal display
    legend_x = 0.5
    legend_xanchor = 'center'
    legend_y = -0.35  # Default position
    
    # For many breakdown categories, adjust legend position
    if breakdown_count > 5:
        legend_y = -0.20  # Lower the legend to avoid overlapping with x-axis labels
    
    # Calculate reduced top margin based on title length
    # Base margin is smaller now (70 instead of 100)
    # We add less extra space per line (10px instead of 20px)
    top_margin = 70 + (len(wrapped_lines) - 1) * 10
    
    fig.update_layout(
        title={
            'text': wrapped_title,
            'y': 0.97,  # Move title closer to the top
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Arial'}
        },
        xaxis=dict(
            title='Year',
            type='category',
            categoryorder='array',
            categoryarray=time_points_list,
            titlefont={'family': 'Arial'}
        ),
        yaxis=dict(
            title=unit_of_measure,
            titlefont={'family': 'Arial'}
        ),
        # Place legend in a single horizontal row below the chart
        legend=dict(
            orientation='h',  # Horizontal orientation
            yanchor='top',
            y=legend_y,
            xanchor=legend_xanchor,
            x=legend_x,
            font={'family': 'Arial'},
            traceorder='normal',  # Keep "Total" as the first item
            itemwidth=40,  # Make items more compact
            itemsizing='constant'  # Keep item size consistent
        ),
        margin=dict(l=60, r=30, t=top_margin, b=100),  # Reduced top margin 
        hovermode='closest',
        # Use fixed height with minimal increase for additional lines
        height=430 + (len(wrapped_lines) - 1) * 10,
        font={'family': 'Arial'}  # Set Arial as the default font throughout
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

if __name__ == '__main__':
    app.run_server(debug=False)