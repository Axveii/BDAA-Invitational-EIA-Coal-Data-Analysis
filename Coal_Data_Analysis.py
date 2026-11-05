# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("eia_coal_consumption_quality_2020_2025.csv")

#changes period and sector data to numerical values
df["period"] = pd.to_numeric(df["period"])
df["sector"] = pd.to_numeric(df["sector"])

#filters for national data 
us = df[df["location"] == "US"]

#filters for state observations; excludes Puerto Rico and US totals
states = df[
    df["location"].str.fullmatch(r"[A-Z]{2}") &
    (df["location"] != "US") &
    (df["location"] != "PR")
]
#selects the six non-overlapping sectors
#94 combines 1 and 2, 98 combines 1, 2, and 3
valid_sectors = [1, 2, 3, 8, 9, 10]

#calculates national totals across individual sectors
national_totals = (
    us[us["sector"].isin(valid_sectors)]
    .groupby("period")["consumption"]
    .sum()
)

# %%
plt.figure(figsize = (10, 6))

plt.plot(
    national_totals.index,
    national_totals.values / 1000000,
    marker = "o"
)

plt.title("Total U.S. Coal Consumption (2020–2025)")
plt.xlabel("Year")
plt.ylabel("Consumption (Million Short Tons)")
plt.xticks(national_totals.index)
plt.show()

# %%
sector_consumption = us[us["sector"].isin(valid_sectors)].pivot(
    index = "period", 
    columns = "sectorDescription", 
    values = "consumption"
)

sector_consumption = sector_consumption / 1000000

sector_consumption.plot(
    kind = "area",
    stacked = True,
    figsize = (12, 7)
)

plt.title("U.S. Coal Consumption by Sector (2020–2025)")
plt.xlabel("Year")
plt.ylabel("Consumption (Million Short Tons)")
plt.legend(title = "Sector", bbox_to_anchor = (1.05, 1))
plt.tight_layout()
plt.show()

# %%
sector_change = us[us["sector"].isin(valid_sectors)].pivot(
    index = "sectorDescription",
    columns = "period",
    values = "consumption"
)

sector_change["Percent Change"] = (
    (sector_change[2025] - sector_change[2020])
    / sector_change[2020]
) * 100

sector_change = sector_change.sort_values("Percent Change")

plt.figure(figsize=(10, 6))

sns.barplot(
    x=sector_change["Percent Change"],
    y=sector_change.index
)

plt.axvline(0, color="black")

plt.title("Percentage Change in Coal Consumption by Sector (2020–2025)")
plt.xlabel("Percentage Change")
plt.ylabel("Sector")
plt.tight_layout()
plt.show()

# %%
for year in [2020, 2025]:

    state_year = states[
        (states["period"] == year) &
        (states["sector"].isin(valid_sectors))
    ]

    state_year = (
        state_year.groupby("stateDescription")["consumption"]
        .sum()
        .sort_values(ascending=False)
    ) / 1000000

    plt.figure(figsize=(10, 7))

    state_year.head(15).sort_values().plot(kind="barh")

    plt.title(f"Top 15 Coal-Consuming States ({year})")
    plt.xlabel("Consumption (Million Short Tons)")
    plt.ylabel("State")

    plt.tight_layout()
    plt.show()

# %%
state_comparison = states[states["sector"].isin(valid_sectors)].pivot_table(
    index = "stateDescription",
    columns = "period",
    values = "consumption",
    aggfunc = "sum"
)

state_comparison["Change"] = (
    state_comparison[2025] - state_comparison[2020]
) / 1000000

state_comparison = state_comparison.sort_values("Change")

plt.figure(figsize = (11, 9))

state_comparison["Change"].plot(kind = "barh")

plt.axvline(0, color = "black")

plt.title("Change in Coal Consumption by State (2020–2025)")
plt.xlabel("Change (Million Short Tons)")
plt.ylabel("State")
plt.show()

# %% [markdown]
# #Prices, deliveries, and stockpiles

# %%
plt.figure(figsize = (11, 7))

sns.lineplot(
    data  =us[us["sector"].isin(valid_sectors)],
    x = "period",
    y = "price",
    hue = "sectorDescription",
    marker = "o"
)

plt.title("Coal Prices by Sector (2020–2025)")
plt.xlabel("Year")
plt.ylabel("Price (Dollars per Short Ton)")
plt.xticks(range(2020, 2026))
plt.legend(title = "Sector", bbox_to_anchor = (1.05, 1))
plt.tight_layout()
plt.show()

# %%
national_data = us[us["sector"].isin(valid_sectors)]

national_flows = national_data.groupby("period")[["receipts", "consumption"]].sum()

national_stocks = national_data.groupby("period")["stocks"].sum()

national_flows = national_flows / 1000000
national_stocks = national_stocks / 1000000

fig, ax1 = plt.subplots(figsize = (12, 7))

ax1.plot(
    national_flows.index,
    national_flows["receipts"],
    marker = "o",
    label = "Receipts"
)

ax1.plot(
    national_flows.index,
    national_flows["consumption"],
    marker = "o",
    label = "Consumption"
)

ax1.set_xlabel("Year")
ax1.set_ylabel("Annual Flow (Million Short Tons)")
ax1.set_xticks(range(2020, 2026))

ax2 = ax1.twinx()

ax2.plot(
    national_stocks.index,
    national_stocks,
    marker = "s",
    linestyle = "--",
    label = "Stocks"
)

ax2.set_ylabel("Inventory (Million Short Tons)")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(lines1 + lines2, labels1 + labels2)

plt.title("U.S. Coal Receipts, Consumption, and Stockpiles")
plt.show()

# %%
quality_data = us[
    us["sector"].isin(valid_sectors)
]

plt.figure(figsize = (12, 7))

sns.lineplot(
    data = quality_data,
    x = "period",
    y = "ash-content",
    hue = "sectorDescription",
    marker = "o"
)

plt.title("Ash Content by Sector")
plt.xlabel("Year")
plt.ylabel("Ash Content (% by Weight)")
plt.tight_layout()
plt.show()

plt.figure(figsize = (12, 7))

sns.lineplot(
    data = quality_data,
    x = "period",
    y = "sulfur-content",
    hue = "sectorDescription",
    marker = "o"
)

plt.title("Sulfur Content by Sector")
plt.xlabel("Year")
plt.ylabel("Sulfur Content (% by Weight)")
plt.tight_layout()
plt.show()

# %%
quality_data = us[
    us["sector"].isin(valid_sectors) &
    us["period"].isin([2020, 2025])
].copy()

quality_change = quality_data.pivot(
    index = "sector",
    columns = "period",
    values = ["ash-content", "sulfur-content", "price"]
)

quality_change["ash-change"] = (
    quality_change["ash-content"][2025] -
    quality_change["ash-content"][2020]
)

quality_change["sulfur-change"] = (
    quality_change["sulfur-content"][2025] -
    quality_change["sulfur-content"][2020]
)

quality_change["price-change"] = (
    quality_change["price"][2025] -
    quality_change["price"][2020]
)

quality_change["sectorDescription"] = (
    quality_data.drop_duplicates("sector")
    .set_index("sector")["sectorDescription"]
)

quality_change = quality_change.reset_index()

plt.figure(figsize = (12, 7))

sns.scatterplot(
    data = quality_change,
    x = "ash-change",
    y = "price-change",
    hue = "sectorDescription",
    s = 100
)

plt.title("Coal Price Change vs. Ash Content Change (2020–2025)")
plt.xlabel("Change in Ash Content (%)")
plt.ylabel("Change in Coal Price (Dollars per Short Ton)")
plt.axhline(0, color = "gray", linestyle = "--")
plt.axvline(0, color = "gray", linestyle = "--")
plt.tight_layout()
plt.show()

plt.figure(figsize = (12, 7))

sns.scatterplot(
    data = quality_change,
    x = "sulfur-change",
    y = "price-change",
    hue = "sectorDescription",
    s = 100
)

plt.title("Coal Price Change vs. Sulfur Content Change (2020–2025)")
plt.xlabel("Change in Sulfur Content (%)")
plt.ylabel("Change in Coal Price (Dollars per Short Ton)")
plt.axhline(0, color = "gray", linestyle = "--")
plt.axvline(0, color = "gray", linestyle = "--")
plt.tight_layout()
plt.show()

# %%
sector_prices = us[
    us["sector"].isin(valid_sectors)
].pivot(
    index = "sectorDescription",
    columns = "period",
    values = "price"
)

sector_consumption = us[
    us["sector"].isin(valid_sectors)
].pivot(
    index = "sectorDescription",
    columns = "period",
    values = "consumption"
)

sector_comparison = pd.DataFrame(index = sector_prices.index)

sector_comparison["Price Change"] = (
    (sector_prices[2025] - sector_prices[2020])
    / sector_prices[2020]
) * 100

sector_comparison["Consumption Change"] = (
    (sector_consumption[2025] - sector_consumption[2020])
    / sector_consumption[2020]
) * 100

plt.figure(figsize = (10, 7))

sns.scatterplot(
    data = sector_comparison,
    x = "Price Change",
    y = "Consumption Change",
    hue = sector_comparison.index,
    s = 150
)

plt.axhline(0, color = "black")
plt.axvline(0, color = "black")

plt.title("Sector Price Changes vs. Consumption Changes")
plt.xlabel("Price Change (%)")
plt.ylabel("Consumption Change (%)")

plt.show()

# %%
electricity_consumption = (
    us[us["sector"].isin([1, 2, 3])]
    .groupby("period")["consumption"]
    .sum()
)

other_consumption = (
    us[us["sector"].isin([8, 9, 10])]
    .groupby("period")["consumption"]
    .sum()
)

electricity_share = (
    electricity_consumption / national_totals
) * 100

plt.figure(figsize = (10, 6))

plt.plot(
    electricity_share.index,
    electricity_share.values,
    marker = "o"
)

plt.title("Electricity Generation's Share of U.S. Coal Consumption")
plt.xlabel("Year")
plt.ylabel("Share of Consumption (%)")
plt.show()

# %%
# selects sector 98 for 2020
state_prices_2020 = states[
    (states["period"] == 2020) &
    (states["sector"] == 98)
].copy()

state_prices_2020["price_per_mmbtu"] = (
    state_prices_2020["price"] / state_prices_2020["heat-content"]
)

# removes missing and zero values
state_prices_2020 = state_prices_2020[
    state_prices_2020["price_per_mmbtu"] > 0
].dropna(
    subset = ["price_per_mmbtu"]
)


# selects sector 98 for 2025
state_prices_2025 = states[
    (states["period"] == 2025) &
    (states["sector"] == 98)
].copy()

state_prices_2025["price_per_mmbtu"] = (
    state_prices_2025["price"] / state_prices_2025["heat-content"]
)

# removes missing and zero values
state_prices_2025 = state_prices_2025[
    state_prices_2025["price_per_mmbtu"] > 0
].dropna(
    subset = ["price_per_mmbtu"]
)


# identifies states appearing in both years
common_states = set(state_prices_2020["stateDescription"]) & \
                set(state_prices_2025["stateDescription"])

# keeps only common states
state_prices_2020 = state_prices_2020[
    state_prices_2020["stateDescription"].isin(common_states)
].copy()

state_prices_2025 = state_prices_2025[
    state_prices_2025["stateDescription"].isin(common_states)
].copy()


state_prices_2020 = state_prices_2020.sort_values(
    by = "price_per_mmbtu"
)

state_prices_2025 = state_prices_2025.sort_values(
    by = "price_per_mmbtu"
)

plt.figure(figsize = (10, 11))

sns.barplot(
    data = state_prices_2020,
    x = "price_per_mmbtu",
    y = "stateDescription",
    width = 0.5
)

plt.xlim(0, state_prices_2020["price_per_mmbtu"].max() + 0.5)
plt.xticks(np.arange(0, state_prices_2020["price_per_mmbtu"].max() + 0.5, 0.5))

for i, value in enumerate(state_prices_2020["price_per_mmbtu"]):
    plt.text(
        value + 0.03,
        i,
        f"${value:.2f}",
        va = "center"
    )

plt.gca().invert_yaxis()

plt.title("Cost of Coal Energy by State, 2020 (Electric Power)")
plt.xlabel("$ per MMBtu")
plt.ylabel("State")
plt.tight_layout()
plt.show()

plt.figure(figsize = (10, 11))

sns.barplot(
    data = state_prices_2025,
    x = "price_per_mmbtu",
    y = "stateDescription",
    width = 0.5
)

plt.xlim(0, state_prices_2025["price_per_mmbtu"].max() + 0.5)
plt.xticks(np.arange(0, state_prices_2025["price_per_mmbtu"].max() + 0.5, 0.5))

for i, value in enumerate(state_prices_2025["price_per_mmbtu"]):
    plt.text(
        value + 0.03,
        i,
        f"${value:.2f}",
        va = "center"
    )

plt.gca().invert_yaxis()

plt.title("Cost of Coal Energy by State, 2025 (Electric Power)")
plt.xlabel("$ per MMBtu")
plt.ylabel("State")
plt.tight_layout()
plt.show()
