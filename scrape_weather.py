import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver=webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
url = "https://www.timeanddate.com/weather/"
driver.get(url)

WebDriverWait(driver,10).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "table.zebra.fw.tb-theme")
    )
)

rows=driver.find_elements(
    By.CSS_SELECTOR, 
    "table.zebra.fw.tb-theme tbody tr"
)

print("Rows found:", len(rows))

results = []

try:
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")

        for i in range(0, len(cells) - 3, 4):
            city_cells = cells[i]
            time_cells = cells[i + 1]
            temp_cells = cells[i + 3]

            city_links = city_cells.find_elements(By.TAG_NAME, "a")

            if not city_links:
                continue

            city_link = city_links[0]

            city = city_link.text
            href = city_link.get_attribute("href")
            local_time = time_cells.text
            temperature = temp_cells.text

            country = href.split("/weather/")[1].split("/")[0]

            results.append({
                "City": city,
                "Country": country,
                "Local_Time": local_time,
                "Temperature": temperature
            })

finally:
    df = pd.DataFrame(results)

    print("\nBefore cleaning:")
    print(df.head())

    # Save raw scraped data
    df.to_csv("weather_raw.csv", index=False)

    # Minimal cleaning
    clean_df = df.copy()

    clean_df = clean_df.drop_duplicates()
    clean_df = clean_df.dropna()

    clean_df["Temperature_F"] = (
        clean_df["Temperature"]
        .str.replace("°F", "", regex=False)
        .str.strip()
    )

    clean_df["Temperature_F"] = pd.to_numeric(
        clean_df["Temperature_F"],
        errors="coerce"
    )

    clean_df["Country"] = (
        clean_df["Country"]
        .str.replace("-", " ", regex=False)
        .str.title()
    )

    clean_df = clean_df.dropna(subset=["Temperature_F"])

    # Save cleaned data
    clean_df.to_csv("weather_clean.csv", index=False)
    print("\nAfter cleaning:")
    print(clean_df.head())

    print("Raw rows saved:", len(df))
    print("Clean rows saved:", len(clean_df))

    driver.quit()

    