# streamlit_app_TV.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Terminal Value Sandbox", layout="centered")

DEFAULT_DISCOUNT_RATE = 0.20
DCF_COLOR = "#B52C2F"
TV_COLOR = "#002FA7"

st.markdown("""
### So verwenden Sie dieses Tool
- Wählen Sie aus, wie der Terminal Value berechnet werden soll.
- Wählen Sie bei der Wachstumsmethode eine langfristige Wachstumsrate.
- Wählen Sie bei der Exit-Multiple-Methode ein Exit Multiple.
- Das Tool zeigt, wie sich die Annahmen zum Terminal Value auf den Gesamtwert auswirken.
""")

cash_flows = [2760, 3150, 3530, 3900, 4140]
years = [1, 2, 3, 4, 5]

cf_n = cash_flows[-1]
cf_1 = cash_flows[0]

average_annual_increase = (cf_n - cf_1) / (len(cash_flows) - 1)
cf_n_plus_1 = cf_n + average_annual_increase

st.subheader("Annahmen zum Terminal Value")

method = st.selectbox(
    "Methode zur Berechnung des Terminal Value auswählen",
    ["Wachstumsmethode", "Exit-Multiple-Methode"]
)

if method == "Wachstumsmethode":
    g_pct = st.number_input(
        "Langfristige Wachstumsrate [%]",
        min_value=0.0,
        value=2.0,
        step=1.0,
        format="%.0f",
    )

    discount_rate_pct = st.number_input(
        "Diskontierungszinssatz [%]",
        min_value=1.0,
        value=20.0,
        step=1.0,
        format="%.0f",
    )

    g = g_pct / 100
    discount_rate = discount_rate_pct / 100

    if g >= discount_rate:
        st.warning(
            "Die langfristige Wachstumsrate muss niedriger sein als der "
            "Diskontierungszinssatz. Bitte wählen Sie eine tiefere Wachstumsrate."
        )
        st.stop()

    terminal_value = cf_n * (1 + g) / (discount_rate - g)

else:
    exit_multiple = st.number_input(
        "Exit Multiple",
        min_value=0.0,
        value=10.0,
        step=0.5,
        format="%.1f",
    )

    discount_rate = DEFAULT_DISCOUNT_RATE
    terminal_value = cf_n_plus_1 * exit_multiple

present_values = [
    cf / ((1 + discount_rate) ** (year - 1))
    for cf, year in zip(cash_flows, years)
]

explicit_value = sum(present_values)
discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 4)
valuation = explicit_value + discounted_terminal_value

st.subheader("Unternehmenswert")
st.metric("Gesamtwert", f"USD {valuation:,.0f}k")

st.subheader("Diskontierte Cashflows und Terminal Value")

dcf_df = pd.DataFrame(
    {
        "Periode": [f"Jahr {year}" for year in years] + ["Terminal Value"],
        "Komponente": ["Diskontierte Cashflows"] * len(years) + ["Terminal Value"],
        "Wert": present_values + [discounted_terminal_value],
        "sort_order": list(range(len(years))) + [len(years)],
    }
)

dcf_bar = (
    alt.Chart(dcf_df)
    .mark_bar()
    .encode(
        x=alt.X("Periode:N", title="", sort=alt.SortField("sort_order")),
        y=alt.Y("Wert:Q", title="Barwert (Tausend USD)"),
        color=alt.Color(
            "Komponente:N",
            title="",
            scale=alt.Scale(
                domain=["Diskontierte Cashflows", "Terminal Value"],
                range=[DCF_COLOR, TV_COLOR],
            ),
        ),
        tooltip=[
            alt.Tooltip("Periode:N", title="Periode"),
            alt.Tooltip("Komponente:N", title="Komponente"),
            alt.Tooltip("Wert:Q", title="Wert", format=",.0f"),
        ],
    )
)

st.altair_chart(dcf_bar, use_container_width=True)

st.subheader("Zusammensetzung des Unternehmenswerts")

stack_df = pd.DataFrame(
    {
        "Kategorie": ["Unternehmenswert", "Unternehmenswert"],
        "Komponente": ["Diskontierte Cashflows", "Terminal Value"],
        "Wert": [explicit_value, discounted_terminal_value],
        "stack_order": [0, 1],
    }
)

bar = (
    alt.Chart(stack_df)
    .mark_bar()
    .encode(
        x=alt.X("Kategorie:N", title=""),
        y=alt.Y("sum(Wert):Q", title="Barwert (Tausend USD)"),
        color=alt.Color(
            "Komponente:N",
            title="",
            scale=alt.Scale(
                domain=["Diskontierte Cashflows", "Terminal Value"],
                range=[DCF_COLOR, TV_COLOR],
            ),
        ),
        order=alt.Order("stack_order:Q"),
        tooltip=[
            alt.Tooltip("Komponente:N", title="Komponente"),
            alt.Tooltip("Wert:Q", title="Wert", format=",.0f"),
        ],
    )
)

total_df = pd.DataFrame(
    {
        "Kategorie": ["Unternehmenswert"],
        "Total": [valuation],
    }
)

label = (
    alt.Chart(total_df)
    .mark_text(dy=-10)
    .encode(
        x=alt.X("Kategorie:N"),
        y=alt.Y("Total:Q"),
        text=alt.Text("Total:Q", format=",.0f"),
    )
)

st.altair_chart(bar + label, use_container_width=True)
