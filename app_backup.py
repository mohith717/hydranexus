import pandas as pd
import streamlit as st

from detector import detect_possible_leak

st.set_page_config(
    page_title="HydraNexus | Intelligent Water Monitoring",
    page_icon="💧",
    layout="wide",
)

st.title("💧 HydraNexus")
st.subheader("Intelligent Water Monitoring & Leak Detection")
st.caption("Detect. Analyze. Conserve.")

st.info(
    "HydraNexus is a prototype using simulated or manually entered "
    "water-flow readings. It is not connected to a physical sensor."
)

SCENARIOS = {
    "Normal usage": [0.2, 0.3, 0.1, 0.4, 0.2, 0.3, 0.1],
    "Possible leak": [0.2, 0.3, 1.4, 1.5, 1.6, 1.7, 1.8],
    "Brief spike": [0.2, 0.3, 1.8, 0.2, 0.3, 0.2, 0.1],
}

with st.sidebar:
    st.header("Monitoring settings")

    scenario = st.selectbox(
        "Scenario",
        ["Normal usage", "Possible leak", "Brief spike", "Custom readings"],
    )

    threshold = st.slider(
        "High-flow threshold (L/min)",
        min_value=0.1,
        max_value=3.0,
        value=1.0,
        step=0.1,
    )

    consecutive = st.slider(
        "Consecutive high readings required",
        min_value=1,
        max_value=6,
        value=3,
    )

    st.caption(
        "An alert is triggered when the selected number of "
        "consecutive readings exceeds the threshold."
    )

if scenario == "Custom readings":
    custom_input = st.text_input(
        "Flow readings (L/min), separated by commas",
        value="0.2, 0.3, 1.4, 1.5, 1.6",
    )

    try:
        readings = [
            float(value.strip())
            for value in custom_input.split(",")
            if value.strip()
        ]

        if not readings:
            raise ValueError("Enter at least one reading.")

        if any(value < 0 for value in readings):
            raise ValueError("Flow readings cannot be negative.")

    except ValueError as error:
        st.error(f"Invalid input: {error}")
        st.stop()

else:
    readings = SCENARIOS[scenario]

try:
    possible_leak = detect_possible_leak(
        readings,
        threshold=threshold,
        consecutive=consecutive,
    )
except ValueError as error:
    st.error(str(error))
    st.stop()

data = pd.DataFrame({
    "Reading number": range(1, len(readings) + 1),
    "Flow (L/min)": readings,
})

data["Above threshold"] = data["Flow (L/min)"] > threshold

st.divider()
st.header("Monitoring overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total readings", len(readings))
col2.metric("Average flow", f"{data['Flow (L/min)'].mean():.2f} L/min")
col3.metric("Peak flow", f"{data['Flow (L/min)'].max():.2f} L/min")
col4.metric("High readings", int(data["Above threshold"].sum()))

if possible_leak:
    st.error(
        "⚠️ POSSIBLE SUSTAINED HIGH FLOW DETECTED\n\n"
        "Inspect the water system to determine the cause. "
        "This alert does not prove that a leak exists."
    )
else:
    st.success(
        "✅ No sustained high-flow pattern detected "
        "with the current settings."
    )

left, right = st.columns([2, 1])

with left:
    st.subheader("Water-flow trend")
    st.line_chart(
        data.set_index("Reading number")["Flow (L/min)"]
    )

with right:
    st.subheader("Detection summary")
    st.write(f"**Scenario:** {scenario}")
    st.write(f"**Threshold:** {threshold:.1f} L/min")
    st.write(f"**Required consecutive readings:** {consecutive}")
    st.write(f"**Alert result:** {'Possible high flow' if possible_leak else 'No sustained high flow'}")

st.subheader("Reading details")
st.dataframe(data, width="stretch", hide_index=True)

st.download_button(
    label="Download readings as CSV",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="hydranexus_readings.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "HydraNexus prototype | Simulated data | "
    "Real-world performance requires sensor integration and validation."
)