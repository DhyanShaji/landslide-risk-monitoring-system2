import pandas as pd
import folium


# -----------------------------------------
# Load risk data
# -----------------------------------------

input_file = "data/processed/risk_scores.csv"

output_file = "data/processed/ner_risk_map.html"

df = pd.read_csv(input_file)

print("Risk records loaded:", len(df))


# -----------------------------------------
# Create map
# -----------------------------------------

m = folium.Map(
    location=[26.5, 93.5],
    zoom_start=6,
    tiles="OpenStreetMap"
)


# -----------------------------------------
# Risk colors
# -----------------------------------------

def risk_color(level):

    if level == "Critical":
        return "red"

    elif level == "High":
        return "orange"

    elif level == "Moderate":
        return "beige"

    else:
        return "green"


# -----------------------------------------
# Add risk points
# -----------------------------------------

for _, row in df.iterrows():

    folium.CircleMarker(
        location=[
            row["Latitude"],
            row["Longitude"]
        ],
        radius=4,
        color=risk_color(
            row["Risk_Level"]
        ),
        fill=True,
        fill_color=risk_color(
            row["Risk_Level"]
        ),
        fill_opacity=0.7,
        popup=(
            f"<b>Risk Level:</b> "
            f"{row['Risk_Level']}<br>"
            f"<b>Risk Score:</b> "
            f"{row['Risk_Score']}<br>"
            f"<b>Elevation:</b> "
            f"{row['Elevation']} m<br>"
            f"<b>Slope:</b> "
            f"{row['Slope']:.2f}°<br>"
            f"<b>Rainfall:</b> "
            f"{row['Rainfall_2023']:.2f} mm"
        )
    ).add_to(m)


# -----------------------------------------
# Add legend
# -----------------------------------------

legend = """
<div style="
position: fixed;
bottom: 30px;
left: 30px;
width: 180px;
background-color: white;
border: 2px solid grey;
z-index: 9999;
font-size: 14px;
padding: 10px;
">

<b>Landslide Risk</b><br><br>

<span style="color:red;">●</span>
Critical (76–100)<br>

<span style="color:orange;">●</span>
High (51–75)<br>

<span style="color:#d8ca9d;">●</span>
Moderate (26–50)<br>

<span style="color:green;">●</span>
Low (0–25)

</div>
"""

m.get_root().html.add_child(
    folium.Element(legend)
)


# -----------------------------------------
# Save map
# -----------------------------------------

m.save(output_file)

print("\nRisk map created successfully!")

print("Saved to:")
print(output_file)