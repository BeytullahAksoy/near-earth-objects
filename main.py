import requests
import pandas as pd
import streamlit as st
import datetime
import arrow


def _extract_data(near_earth_objects):
    asteroid_dict = {}

    for date in near_earth_objects:
        for entry in near_earth_objects[date]:
            key_dict = date
            temp_dict = {
                "neo_reference_id": entry["neo_reference_id"],
                "name": entry["name"],
                "absolute_magnitude_h": entry["absolute_magnitude_h"],
                "diameter_min": entry["estimated_diameter"]["meters"][
                    "estimated_diameter_min"
                ],
                "diameter_max": entry["estimated_diameter"]["meters"][
                    "estimated_diameter_max"
                ],
                "approach_date": entry["close_approach_data"][0]["close_approach_date"],
                "distance": entry["close_approach_data"][0]["miss_distance"][
                    "kilometers"
                ],
            }
            asteroid_dict.setdefault(key_dict, []).append(temp_dict)
    dict1 = dict(sorted(asteroid_dict.items(), key=lambda item: len(item)))

    for d in dict1:
        dict1[d].sort(key=lambda x: x["absolute_magnitude_h"], reverse=True)
    return dict1


def get_data_dictionary(start_date, end_date):
    API_KEY = "4Tfx4FsPzaEuyiHGdPK2aKnPJXQQJcBgqhtJbGVD"
    path = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
    url = path.format(start_date, end_date)
    rsp = requests.get(url)
    neo = rsp.json()["near_earth_objects"]
    asteroid_dict = _extract_data(neo)
    return asteroid_dict


def create_df(start_date, end_date):
    data = get_data_dictionary(start_date, end_date)
    res = {}
    for d in data:
        for l in data[d]:
            res[d + " " + l["neo_reference_id"]] = {
                "name": l["name"],
                "absolute_magnitude_h": l["absolute_magnitude_h"],
                "diameter_min": l["diameter_min"],
                "is_potentially_hazardous_asteroid": l["diameter_max"],
                "approach_date": l["approach_date"],
                "distance": l["distance"],
            }
    df = []
    count = 0
    for r in res:
        value = [
            res[r]["name"],
            res[r]["absolute_magnitude_h"],
            res[r]["approach_date"],
            res[r]["distance"],
        ]
        df.append(value)
        count += 1
    df = pd.DataFrame(
        df,
        columns=["Name", "Size Estimate", "Encounter Time", "Encounter Distance(km)"],
    )
    df = df.sort_values(by="Encounter Distance(km)", ascending=False)
    df = df.reset_index(drop=True)
    return df


def main():
    st.title("Near Earth Objects")
    today = arrow.now().format("YYYY-MM-DD")
    current_year = today.split()[0][:4]
    current_month = today.split()[0][5:7]
    current_day = today.split()[0][8:10]
    start_date = st.sidebar.date_input(
        "Start date",
        datetime.date(int(current_year), int(current_month), int(current_day)),
    )
    end_date = st.sidebar.date_input(
        "End date",
        datetime.date(int(current_year), int(current_month), int(current_day) - 7),
    )
    date_range = (start_date - end_date).days
    if date_range <= 7:
        try:
            df = create_df(start_date, end_date)
            print(df)
            st.dataframe(df)
        except:
            st.write("No response from API, please enter a valid date")
    else:
        st.write(
            "Due to API limitation, please enter the date range so that the difference between the two dates is 7 days."
        )


if __name__ == "__main__":
    main()
