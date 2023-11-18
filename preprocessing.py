import pandas as pd


def extra_mapping(country):
    extras = {
        "Cabo Verde": "Cape Verde",
        "Iran (Islamic Republic of)": "Iran",
        "Korea, North": "North Korea",
        "Korea, South": "South Korea",
        "Taiwan*": "Taiwan",
        "Timor-Leste": "Timor",
        "Lao People's Democratic Republic": "Laos",
        "Republic of Moldova": "Moldova",
        "Russian Federation": "Russia",
        "United Republic of Tanzania": "Tanzania",
        "United States of America": "United States",
        "Venezuela (Bolivarian Republic of)": "Venezuela",
    }
    if country in extras.keys():
        return extras[country]
    else:
        return country


def get_time_series():
    df = pd.read_csv("data/owid-covid-data.csv")
    df["date"] = pd.to_datetime(df["date"]).apply(lambda dt: dt.replace(day=1))
    df = (
        df.groupby(["date", "iso_code"])
        .agg(
            {
                "location": "first",
                "new_cases_per_million": "sum",
                "new_deaths_per_million": "sum",
            }
        )
        .reset_index()
    )
    df.columns = [
        "Date",
        "iso_code",
        "Country",
        "New Cases Per Million",
        "New Deaths Per Million",
    ]
    return df


def get_data(diet_csv):
    df_covid = pd.read_csv("data/owid-covid-data.csv")
    grouped = (
        df_covid.groupby("location")
        .agg(
            {
                "continent": "first",
                "iso_code": "first",
                "total_cases_per_million": "max",
                "total_deaths_per_million": "max",
                "life_expectancy": "first",
                "human_development_index": "first",
                "female_smokers": "first",
                "male_smokers": "first",
            }
        )
        .reset_index()
    )
    grouped.columns = [
        "Country",
        "Continent",
        "iso_code",
        "Total Cases Per Million",
        "Total Deaths Per Million",
        "Life Expectancy",
        "Human Development Index",
        "Female Smokers",
        "Male Smokers",
    ]
    fs = pd.read_csv(diet_csv)

    fs["Animals Products"] = (
        fs["Offals"]
        + fs["Animal fats"]
        + fs["Animal Products"]
        + fs["Aquatic Products, Other"]
        + fs["Fish, Seafood"]
        + fs["Meat"]
        + fs["Milk - Excluding Butter"]
    )
    fs["Sugas Crops & Sweeteners"] = fs["Sugar & Sweeteners"] + fs["Sugar Crops"]
    fs["Plant Based Products"] = (
        fs["Starchy Roots"]
        + fs["Pulses"]
        + fs["Vegetal Products"]
        + fs["Vegetables"]
        + fs["Vegetable Oils"]
        + fs["Oilcrops"]
        + fs["Cereals - Excluding Beer"]
        + fs["Treenuts"]
    )
    fs = fs.drop(
        [
            "Offals",
            "Animal fats",
            "Animal Products",
            "Aquatic Products, Other",
            "Fish, Seafood",
            "Sugar & Sweeteners",
            "Sugar Crops",
            "Starchy Roots",
            "Pulses",
            "Vegetal Products",
            "Vegetables",
            "Vegetable Oils",
            "Oilcrops",
            "Cereals - Excluding Beer",
            "Treenuts",
        ],
        axis=1,
    )

    fs.Country = fs.Country.map(extra_mapping)
    df = pd.merge(grouped, fs, on="Country", how="inner")

    for col in ["Total Cases Per Million", "Total Deaths Per Million"]:
        df[col] = df[col].round()
    return df
