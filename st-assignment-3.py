import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode,
    ColumnsAutoSizeMode,
)

st.set_page_config(
    page_title= "streamlit-aggrid App",
    page_icon="🖐",
    layout="wide"
)

header_style = '''
    <style>
        table th {
            background-color: #FFF933;
            font-size: 20px;
            font-family: "Courier New";
        }
        h1{
            color:Red;
            font-size:28px;
            text-align:center;
        }
        h2{
            color:#6B33FF;
            font-size:28px;
            text-align:center;
        }
        h4{
            color:#33ff33;
            font-size:18px;
            text-align:center;
        }
        
    </style>

'''

st.markdown(header_style, unsafe_allow_html=True)

st.title("Scenarios Comparison using streamlit-aggrid")


@st.cache_data()
def read_scenario_data():
    df = pd.read_excel("scenarios.xlsx", sheet_name="Scenarios Summary")
    df["Created Date"] = df["Created Date"].dt.normalize()
    df["prec_profit"] = df["prec_profit"] * 100
    return df

def gen_aggrid(df):
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_default_column(type=["leftAligned"])
    gd.configure_column(
        field="Created Date",
        header_name="Created Date",
        hide=False,
        type=["customDateTimeFormat"],
        custom_format_string="MM-dd-yyyy",
    )
    gd.configure_column(
        field="revenue",
        header_name="Revenue ($)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.revenue.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="cost",
        header_name="Capital Costs ($)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.cost.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="inv_cost",
        header_name="Inventory Cost ($)",
        hide=True,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.inv_cost.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="profit",
        header_name="Profit ($)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.profit.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="prec_profit",
        header_name="% Profit",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.prec_profit.toLocaleString() +'%';",
    )
    gd.configure_column(
        field="Name", 
        header_name="Name", 
        cellStyle={"white-sapces": "break-spaces"}
    )
    return gd

def format_layout_fig(fig, title="Unit Sales", x_axis_title="Year", prefix=False):
    fig.update_xaxes(
        title_text=x_axis_title,
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
    )
    fig.update_yaxes(
        rangemode="tozero", 
        showline=True, 
        linewidth=1, 
        linecolor="black", 
        mirror=True
    )
    fig.update(layout=dict(title=dict(x=0.5)))
    fig.update_layout(
        title_text=title,
        title_font_family="Rockwell", 
        title_font_color="Black", 
        template="plotly_white",
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell")
    )

    if prefix:
        fig.update_layout(yaxis_tickprefix="$")
    return fig

# Custom CSS
custom_css = {
    ".ag-header-cell-label": {"justify-content": "center"},
    "cellStyle": {"textAlign": "center"},
    ".ag-cell": {"display": "flex", "justify-content": "center",},
    # ".ag-cell": {"white-space": "break-spaces"},
}

sc_data = read_scenario_data()


# Aggrid generation
gd = gen_aggrid(sc_data)

gd.configure_selection(
    selection_mode="multiple", 
    use_checkbox=True,
)
grid_options = gd.build()
grid_table = AgGrid(
    sc_data,
    height=250,
    gridOptions=grid_options,
    fit_columns_on_grid_load=True,
    theme="balham",
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    custom_css=custom_css,
)

selected_row = grid_table["selected_rows"]

if len(selected_row) > 0:
    st.write("## Comparison of Selected Scenarios")
    selected_df = pd.DataFrame(selected_row)
    sel_cols = ["Name", "revenue", "cost", "profit"]
    selected_df = selected_df[sel_cols]

    selected_df = selected_df.rename(
        columns={
            "index": "Metric",
            "Name": "Scenario",
            "revenue": "Revenue",
            "cost": "Cost",
            "profit": "Profit",
        }
    )
    selected_df = selected_df.set_index("Scenario")
    selected_df = selected_df.T.reset_index()
    # st.dataframe(selected_df)
    fig = px.histogram(
        selected_df,
        x="index",
        y=[x for x in selected_df.columns if x != "index"],
        barmode="group",
        text_auto=".2s",
    )
    fig = format_layout_fig(fig, title="Scenario Comparison", x_axis_title="")
    fig = fig.update_layout(
        legend=dict(
            yanchor="bottom", 
            xanchor="center", 
            orientation="h", 
            y=-0.5, 
            x=0.5, 
            title=""
        ),
        yaxis_title="Value ($show)",
    )
    st.plotly_chart(fig, use_container_width=True)