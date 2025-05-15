# Stock Market Prediction using LSTM

This project provides tools for analyzing Nepal Stock Exchange (NEPSE) data, predicting stock trends using LSTM (Long Short-Term Memory) neural networks, and scraping real-time price history.

## Features

1. **Web Scraping**

   - Collect real-time price history data from Mero Lagani
   - Automated data collection for any listed company
   - Save data in CSV format

2. **Stock Trend Prediction**

   - LSTM-based machine learning model for price prediction
   - Interactive visualizations of predictions
   - Moving average analysis (100-day and 200-day)
   - Next day price prediction

3. **Data Analysis**
   - Historical data visualization
   - Technical indicators
   - Interactive charts with Plotly

## Requirements

```bash
pandas
numpy
matplotlib
scikit-learn
plotly
tensorflow
streamlit
selenium
```

## Installation

1. Clone the repository:

```bash
git clone [your-repository-url]
cd StockMarket_LSTM
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:

```bash
streamlit run main.py
```

2. Navigate through different sections:

   - Home: Overview and instructions
   - Nepali Stock Scrape: Collect new data
   - Stock Trend Prediction: Analyze and predict stock prices

3. For prediction:
   - Upload a CSV file with stock data
   - Minimum 100 days of data required
   - Data should have Date and price columns

## Data Format

The CSV file should have the following columns:

- Date
- Open/Close price
- High
- Low
- Volume

## Model Details

- LSTM (Long Short-Term Memory) neural network
- Uses 100-day windows for prediction
- 70-30 train-test split
- Normalized data using MinMaxScaler

## Disclaimer

This tool is for educational and informational purposes only. Always conduct your own research and consult with a financial advisor before making investment decisions.

## Author

[Your Name]

## License

[Your License]

![image](https://github.com/user-attachments/assets/50ab7575-27dc-414e-8a27-25c853b9b1c1)

![image](https://github.com/user-attachments/assets/689a48e2-27cd-4438-b622-6ce4f91a6e32)

![image](https://github.com/user-attachments/assets/ea748a28-6f3a-48ac-8741-d4bfca32a447)

![image](https://github.com/user-attachments/assets/5f0f3d09-202c-4279-89dd-d1072b76a4c9)

![image](https://github.com/user-attachments/assets/af7fb39b-b229-4d7a-8d08-a01bd39f8030)
