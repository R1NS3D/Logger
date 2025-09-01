# 📊 Crypto Logging Journal

A comprehensive Streamlit application for tracking and analyzing potential cryptocurrency investments. This tool allows you to log detailed entries about crypto opportunities with customizable fields and persistent data storage.

## 🚀 Features

- **Toggleable Fields**: Choose which fields to include in your log entries
- **Dynamic Forms**: Only selected fields appear as input options
- **Data Persistence**: Entries are stored in session state across interactions
- **Export Functionality**: Download your data as CSV or JSON
- **Responsive Design**: Clean, modern interface with helpful tooltips
- **Quick Stats**: Overview of your logged entries
- **Sortable Table**: View and analyze all your entries in a data table

## 📋 Available Fields

The application includes 18 different fields you can toggle on/off:

1. **Coin Symbol/Name** - Cryptocurrency symbol or name
2. **Date Logged** - Auto-populated with current date
3. **Current Price** - Current price in USD
4. **Market Cap** - Market capitalization
5. **24h Trading Volume** - Daily trading volume
6. **Circulating/Total Supply** - Supply information
7. **Established Status** - New, Emerging, or Established
8. **Fib Levels** - Fibonacci retracement levels
9. **Conviction Level** - Your conviction (1-10 slider)
10. **Technical Indicators** - Technical analysis notes
11. **Fundamental Analysis** - Project evaluation
12. **Risk Factors** - Potential risks and concerns
13. **Sentiment/Community** - Community sentiment
14. **Exchange Listings** - Current and potential listings
15. **Entry Strategy** - Your planned entry approach
16. **Target/Exit Strategy** - Price targets and exit plan
17. **News/Events** - Recent news and upcoming events
18. **Overall Score/Rating** - Overall opportunity rating (1-10)
19. **Notes/Updates** - Additional thoughts and observations

## 🛠️ Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. **Run the application**:
   ```bash
   streamlit run crypto_journal.py
   ```

2. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

3. **Customize your fields**:
   - Use the sidebar to select which fields you want to include
   - Each field has helpful descriptions and examples
   - Fields can be toggled on/off at any time

4. **Log your entries**:
   - Fill out the form with your selected fields
   - Click "Log Entry" to save your data
   - View all entries in the sortable table below

5. **Export your data**:
   - Use the export buttons to download your data as CSV or JSON
   - Clear all logs if needed with the "Clear All Logs" button

## 📊 Data Management

- **Session State**: All data is stored in Streamlit's session state
- **Persistence**: Data persists across interactions within the same session
- **Export**: Download your data to keep permanent records
- **Validation**: Required fields are validated before saving

## 🎯 Use Cases

- **Research Tracking**: Log potential investments during research
- **Due Diligence**: Document your analysis process
- **Portfolio Planning**: Track opportunities before investing
- **Market Analysis**: Record market observations and trends
- **Team Collaboration**: Share analysis with team members

## 🔧 Customization

The application is built with modularity in mind. You can easily:

- **Add new fields** by modifying the `FIELD_CONFIGS` dictionary
- **Change field types** (text input, number input, dropdown, etc.)
- **Modify validation rules** in the form submission logic
- **Customize the UI** by editing the Streamlit components

## 📝 Example Usage

1. **Start with basic fields**: Enable only Coin Symbol, Current Price, and Notes
2. **Add technical analysis**: Enable Technical Indicators and Fib Levels
3. **Include fundamental data**: Add Market Cap, Established Status, and Fundamental Analysis
4. **Plan your strategy**: Enable Entry Strategy and Target/Exit Strategy
5. **Track over time**: Use the date field to track when you logged each entry

## 🐛 Troubleshooting

- **No fields selected**: Make sure to check at least one field in the sidebar
- **Form not submitting**: Ensure the Coin Symbol field is filled out
- **Data not persisting**: This is expected behavior - use export to save data permanently
- **Performance issues**: Clear old entries if you have many logged entries

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application!
