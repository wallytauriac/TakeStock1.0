import plotly.express as px

# Sample data
data = {
    'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'Sales': [100, 150, 80, 200, 300]
}

# Create a DataFrame
import pandas as pd
df = pd.DataFrame(data)

# Create a line chart
fig = px.line(df, x='Day', y='Sales', title='Sales Over the Week')

# Export the chart to an HTML file
fig.write_html('sales_over_week.html')
