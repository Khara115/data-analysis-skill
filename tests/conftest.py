# -*- coding: utf-8 -*-
"""
Pytest configuration and test data fixtures for ev-data-analysis skill.
Generates fully self-contained in-memory synthetic datasets matching the exact schema in core/engine.py.
"""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def synthetic_ev_df():
    """Generates a consistent, reproducible synthetic EV dataset matching the schema."""
    np.random.seed(42)
    n = 2000

    annual_income = np.random.uniform(20000, 150000, n)
    daily_commute = np.random.uniform(5, 120, n)
    city_type = np.random.choice(["Urban", "Suburban", "Rural"], size=n, p=[0.5, 0.3, 0.2])
    eco_level = np.random.choice([1, 2, 3, 4, 5], size=n)

    # In urban, home charging is lower; in suburban/rural, it's higher
    home_chg_prob = np.where(city_type == "Urban", 0.35, 0.8)
    home_charger = np.where(np.random.uniform(0, 1, n) < home_chg_prob, "Yes", "No")

    # If home charger is Yes, anxiety is almost always Low; if No, higher anxiety
    anxiety_p_yes = [0.99, 0.01, 0.0]
    anxiety_p_no = [0.1, 0.4, 0.5]
    range_anxiety = []
    for hc in home_charger:
        if hc == "Yes":
            range_anxiety.append(np.random.choice(["Low", "Medium", "High"], p=anxiety_p_yes))
        else:
            range_anxiety.append(np.random.choice(["Low", "Medium", "High"], p=anxiety_p_no))
    range_anxiety = np.array(range_anxiety)

    subsidy = np.random.choice(["Yes", "No"], size=n, p=[0.5, 0.5])

    # Realistic conversion probability logic
    anxiety_penalty = np.where(range_anxiety == "High", -4.0, np.where(range_anxiety == "Medium", -0.5, 0.6))
    charger_boost = np.where(home_charger == "Yes", 1.2, -0.8)
    subsidy_boost = np.where(subsidy == "Yes", 0.8, 0.0)

    logits = (annual_income - 60000) / 35000 + anxiety_penalty + charger_boost + subsidy_boost
    probs = 1 / (1 + np.exp(-logits))
    target = (np.random.uniform(0, 1, n) < probs).astype(int)

    df = pd.DataFrame({
        "Annual_Income_USD": annual_income,
        "Daily_Commute_km": daily_commute,
        "City_Type": city_type,
        "Range_Anxiety_Level": range_anxiety,
        "Home_Charging_Possible": home_charger,
        "Subsidy_Available": subsidy,
        "Environmental_Concern_Level": eco_level,
        "Will_Buy_EV": np.where(target == 1, "Yes", "No"),
        "target": target
    })
    return df
