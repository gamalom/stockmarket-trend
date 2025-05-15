import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import time

def web_scraping():
    st.title("Web Scraping: Stock Price History")

    # User inputs
    symbol = st.text_input("Enter stock symbol (e.g., NTC):", "NTC")
    num_rows = st.number_input("Enter number of rows to scrape:", min_value=1, value=100, step=1)

    def scrape_page(driver):
        # Wait for the table to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-bordered")))
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='table-bordered')
        
        data = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cols = row.find_all('td')
            if len(cols) == 9:
                data.append([col.text.strip() for col in cols])
        
        return data

    if st.button("Start Scraping"):
        url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_settings.geolocation": 2
            })
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for the page to load completely
            time.sleep(3)

            try:
                # First try the original ID
                price_history_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_CompanyDetail1_lnkHistoryTab"))
                )
                # Scroll the button into view
                driver.execute_script("arguments[0].scrollIntoView(true);", price_history_button)
                time.sleep(1)
                # Try clicking with JavaScript
                driver.execute_script("arguments[0].click();", price_history_button)
            except Exception:
                try:
                    # Try alternative selector
                    price_history_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Price History')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", price_history_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", price_history_button)
                except Exception as e:
                    st.error("Could not find the Price History button. Please check if the website structure has changed.")
                    driver.quit()
                    return

            # Wait for the table to load
            time.sleep(3)

            all_data = []
            rows_scraped = 0
            page = 1

            while rows_scraped < num_rows:
                status_text.text(f"Scraping page {page}")
                progress_bar.progress(min(rows_scraped / num_rows, 1.0))
                
                if page > 1:
                    try:
                        # Try to find the next page button
                        next_page = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, f"//a[@title='Page {page}']"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", next_page)
                        time.sleep(2)
                    except:
                        break

                page_data = scrape_page(driver)
                if not page_data:
                    break
                
                all_data.extend(page_data[:num_rows - rows_scraped])
                rows_scraped += len(page_data)
                page += 1

            driver.quit()

            if not all_data:
                st.error("No data was scraped. Please check if the website structure has changed.")
                return

            # Write data to CSV file
            filename = f'{symbol}_price_history.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['#', 'Date', 'LTP', '% Change', 'High', 'Low', 'Open', 'Qty.', 'Turnover'])
                writer.writerows(all_data)

            status_text.text(f"Data has been scraped and saved to {filename}")
            st.success(f"Scraping completed successfully! Scraped {len(all_data)} rows.")

            # Display the scraped data
            df = pd.read_csv(filename)
            st.write(df)

        except Exception as e:
            st.error(f"An error occurred during scraping: {str(e)}")
            if 'driver' in locals():
                driver.quit()


def stock_trend_prediction():
    st.title("NEPSE: Stock Analysis and Prediction")

    # Allow the user to upload their own data file
    uploaded_file = st.file_uploader("Upload a CSV file with stock data", type=["csv"])
    if uploaded_file is not None:
        try:
            # Read data from the uploaded CSV file
            df = pd.read_csv(uploaded_file, parse_dates=['Date'])
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True) 
            
            # Display the data in a table
            st.subheader("Data Table")
            st.write(df)

            # Determine which column to use for analysis
            price_column = 'Close' if 'Close' in df.columns else 'Open'
            st.info(f"Using '{price_column}' column for analysis")

            # Convert price column to numeric, replacing any non-numeric values with NaN
            df[price_column] = pd.to_numeric(df[price_column].astype(str).str.replace(',', ''), errors='coerce')
            
            # Drop any rows with NaN values
            df = df.dropna(subset=[price_column])
            
            if len(df) < 100:
                st.error("Not enough valid data points for analysis. Need at least 100 valid price entries.")
                return

            # Visualization
            st.subheader(f"{price_column} Price vs Time chart with 100 MA and 200 MA")

            # Calculate moving averages on cleaned numeric data
            ma100 = df[price_column].rolling(100).mean()
            ma200 = df[price_column].rolling(200).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[price_column], mode='lines', name=f'{price_column} Price'))
            fig.add_trace(go.Scatter(x=df.index, y=ma100, mode='lines', name='100 MA', line=dict(color='red')))
            fig.add_trace(go.Scatter(x=df.index, y=ma200, mode='lines', name='200 MA', line=dict(color='green')))
            fig.update_layout(
                title=f'{price_column} Price and Moving Averages',
                xaxis_title='Date',
                yaxis_title='Price',
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )
            st.plotly_chart(fig)

            # Splitting Data into Training and Testing
            data_training = pd.DataFrame(df[price_column][0:int(len(df)*0.70)])
            data_testing = pd.DataFrame(df[price_column][int(len(df)*0.70):int(len(df))])
            
            # Ensure data is numeric and handle any missing or invalid values
            data_training = data_training.apply(pd.to_numeric, errors='coerce')
            data_testing = data_testing.apply(pd.to_numeric, errors='coerce')
            
            # Drop any NaN values
            data_training = data_training.dropna()
            data_testing = data_testing.dropna()
            
            if len(data_training) < 100 or len(data_testing) < 1:
                st.error("Not enough valid data points for prediction. Please check your data.")
                return
                
            scaler = MinMaxScaler(feature_range=(0, 1))
            data_training_array = scaler.fit_transform(data_training)

            # Load model
            model = load_model("NTC_stock.keras")

            # Prepare testing data
            past_100_days = data_training.tail(100)
            final_df = pd.concat([past_100_days, data_testing])
            
            # Ensure all values are valid numbers
            final_df = final_df.replace([np.inf, -np.inf], np.nan)
            final_df = final_df.dropna()
            
            if len(final_df) < 101:  # Need at least 100 days of data plus 1 day for prediction
                st.error("Not enough consecutive valid data points for prediction.")
                return
                
            input_data = scaler.transform(final_df.values.reshape(-1, 1))
            
            x_test = []
            y_test = []
            
            for i in range(100, len(input_data)):
                x_test.append(input_data[i-100:i])
                y_test.append(input_data[i, 0])
            
            x_test = np.array(x_test)
            y_test = np.array(y_test)
            
            # Check for invalid values before prediction
            if np.any(np.isnan(x_test)) or np.any(np.isinf(x_test)):
                st.error("Invalid values detected in the input data.")
                return
                
            y_predicted = model.predict(x_test)
            
            # Inverse transform to get actual prices
            y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
            y_predicted_actual = scaler.inverse_transform(y_predicted).flatten()
            
            # Check if predictions are valid
            if np.any(np.isnan(y_predicted_actual)) or np.any(np.isinf(y_predicted_actual)):
                st.error("Invalid predictions generated. Please check your data.")
                return

            # Prediction vs Real Price
            st.header("Prediction vs Real Price")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_testing.index, y=y_test_actual, mode='lines', name='Original Price'))
            fig.add_trace(go.Scatter(x=data_testing.index, y=y_predicted_actual, mode='lines', name='Predicted Price'))
            fig.update_layout(
                title='Prediction vs Real Price',
                xaxis_title='Date',
                yaxis_title='Price',
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )
            st.plotly_chart(fig)

            # Predict tomorrow's price
            st.header("Predict Tomorrow's Price")
            last_100_days = input_data[-100:].reshape(1, 100, 1)
            prediction = model.predict(last_100_days)
            tomorrow_price = scaler.inverse_transform(prediction)[0, 0]
            st.write(f"Predicted price for tomorrow: {tomorrow_price:.2f}")

            # Add tomorrow's prediction to the graph
            tomorrow_date = data_testing.index[-1] + pd.Timedelta(days=1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_testing.index, y=y_test_actual, mode='lines', name='Original Price'))
            fig.add_trace(go.Scatter(x=data_testing.index, y=y_predicted_actual, mode='lines', name='Predicted Price'))
            fig.add_trace(go.Scatter(x=[tomorrow_date], y=[tomorrow_price], mode='markers', name="Tomorrow's Prediction", marker=dict(size=10, color='green')))
            fig.update_layout(
                title='Prediction vs Real Price (Including Tomorrow)',
                xaxis_title='Date',
                yaxis_title='Price',
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )
            st.plotly_chart(fig)
            
            # Disclaimer
            st.warning("Please note that this prediction is based on historical data and market trends. "
                    "Actual stock prices may vary due to various factors. Use this information at your own discretion.")
                    
        except Exception as e:
            st.error(f"An error occurred during prediction: {str(e)}")
            st.warning("Please check if your data is properly formatted and contains valid numerical values.")


def home():
    st.title("Welcome to NEPSE Stock Analysis and Prediction")

    st.markdown("""
    This application provides tools for analyzing Nepal Stock Exchange (NEPSE) data, 
    predicting stock trends, and scraping real-time price history.

    ### Features:
    1. **Web Scraping**: Collect real-time price history data from Mero Lagani.
    2. **Stock Trend Prediction**: Use machine learning to predict future stock prices.
    3. **Data Analysis**: Visualize and analyze historical stock data.

    ### How to use:
    - Navigate through different sections using the sidebar on the left.
    - Follow the instructions within each section to analyze data, make predictions, or scrape new data.

    ### Data Sources:
    - Historical data is sourced from [insert your data source].
    - Real-time data is scraped from Mero Lagani (https://merolagani.com/).

    ### Disclaimer:
    This tool is for educational and informational purposes only. Always conduct your own research 
    and consult with a financial advisor before making investment decisions.

    ### About:
    This application was developed by Anuj Nanda Gorkhali. For more information or support, 
    please contact ajngworks@gmail.com.
    """)

    # You can add more elements here, such as:
    # - A sample visualization
    # - Recent news or updates about the app
    # - User testimonials or feedback

    st.info("Start by selecting a section from the sidebar to explore the features of this application.")

def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home","Nepali Stock Scrape","Stock Trend Prediction"])

    if selection == "Home":
        home()
    elif selection == "Nepali Stock Scrape":
        web_scraping()
    elif selection == "Stock Trend Prediction":
        stock_trend_prediction()
    else:
        home()

if __name__ == "__main__":
    main()