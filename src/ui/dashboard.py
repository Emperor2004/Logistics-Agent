import streamlit as st
from typing import Any

st.set_page_config(page_title="Logistics Agent Dashboard")


def run_dashboard(simulator_snapshot_getter: Any):
    # Minimal dashboard that expects a callable to return a snapshot dict.
    st.title("Logistics Agent Dashboard")
    if st.button("Refresh"):
        pass
    snap = simulator_snapshot_getter()
    st.write("Time", snap.get("time"))
    st.write("Drivers")
    for d in snap.get("drivers", []):
        st.write(f"- {d.id}: {d.status} @ ({d.location.lat:.4f}, {d.location.lon:.4f})")
    st.write("Packages")
    for p in snap.get("packages", []):
        st.write(f"- {p.id}: {p.status} -> assigned {p.assigned_to}")