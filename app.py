from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

# --------------------------------------------
# SET UP THE REACTIVE CONTENT MINDY CRUZ
# --------------------------------------------
DEQUE_SIZE = 15
UPDATE_INTERVAL_SECS = 3
data_deque = reactive.value(deque(maxlen=DEQUE_SIZE))


@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    data_deque.get().append(new_dictionary_entry)
    deque_snapshot = data_deque.get()
    df = pd.DataFrame(deque_snapshot)
    latest_dictionary_entry = new_dictionary_entry

    return deque_snapshot, df, latest_dictionary_entry

# --------------------------------------------
# UI Layout
# --------------------------------------------

ui.page_opts(title="Mindy's Live Climate Tracker", fillable=True)

with ui.sidebar(open="open"):
    ui.h2("⛅️ Mindy's ⛅️ Antarctic Explorer  ", class_="text-center")
    ui.p("A demonstration of real-time temperature readings in Antarctica.", class_="text-center")
    ui.hr()
    ui.h6("Link:")
    ui.a(
        "Mindy's GitHub", href="https://github.com/mindy0cruz/cintel-05-cintel-",
        target="_blank",)

with ui.layout_columns():

    # Temperature Value Box
    with ui.value_box(showcase=icon_svg("cloud"),  theme="bg-gradient-blue-purple"):
        "Current Temperature"
        @render.text
        def display_temp():
             deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
             return f"{latest_dictionary_entry['temp']} °C"
    
        "🔥 Warmer than usual 🔥"

    # Date & Time Card
    with ui.card(full_screen=True):
        ui.card_header("🕒 Current Time and Date")
        @render.text
        def display_time():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"


# --------------------------------------------
# Data Table
# --------------------------------------------
with ui.card(full_screen=True):
    ui.card_header("📋 Most Recent Readings")
    @render.data_frame
    def display_df():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        return render.DataGrid(df, width="65%")

# --------------------------------------------
# Live Chart with Trend
# --------------------------------------------
with ui.card():
    ui.card_header("📈 Temp Trend")
    @render_plotly
    def display_plot():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            x_vals = list(range(len(df)))
            y_vals = df["temp"]
            slope, intercept, *_ = stats.linregress(x_vals, y_vals)
            df["regression"] = [slope * x + intercept for x in x_vals]

            fig = px.scatter(
                df,
                x="timestamp",
                y="temp",
                title="Live Temperature Readings",
                labels={"temp": "°C", "timestamp": "Time"},
            )
            fig.add_scatter(
                x=df["timestamp"],
                y=df["regression"],
                mode="lines",
                name="Trend Line",
            )
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                margin=dict(l=20, r=20, t=40, b=20),
            )
            return fig
        return px.scatter()
