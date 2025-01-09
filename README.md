## Overview
This project is an analytics dashboard designed to fetch engagement data from mock social media accounts, store it in DataStax Astra DB, and use Langflow with GPT integration to provide actionable insights. It aims to empower social media strategy with data-driven analytics.

## Technologies Used
- **Streamlit**: For building the web application interface.
- **Requests**: For making HTTP requests to APIs.
- **Pandas**: For data manipulation and analysis.
- **Plotly**: For creating interactive visualizations.
- **Python-dotenv**: For managing environment variables.
- **Groq**: For interacting with the Groq API.
- **Langflow**: For workflow creation and GPT integration.
- **DataStax Astra DB**: For database operations.

## Workflow
1. **Data Fetching**: Engagement data is fetched from mock social media accounts.
2. **Data Storage**: The data is stored in DataStax Astra DB.
3. **Data Processing**: Langflow processes the data to calculate engagement metrics.
4. **Insight Generation**: GPT integration provides insights based on the processed data.
5. **Visualization**: The dashboard presents the data and insights interactively.

## Setup Instructions

### Prerequisites
- A DataStax Astra DB account.
- Langflow installed and configured.
- API keys and tokens for necessary services.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/sidharthsajith/supermind-submission.git
   cd supermind-submission
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`:
   ```env
   BASE_API_URL=your_base_api_url
   LANGFLOW_ID=your_langflow_id
   FLOW_ID=your_flow_id
   APPLICATION_TOKEN=your_application_token
   ```
4. Set up DataStax Astra DB:
   - Create a keyspace and table for engagement data.
   - Obtain the connection URL and credentials.

### Running the Application
1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Access the dashboard at `http://localhost:8501`.

## Usage
- Navigate through the tabs to analyze performance, ask questions, and view trends.
- Use the interactive visualizations to explore engagement metrics.
- Refer to the insights section for data-driven recommendations.

## Contributions
Contributions are welcome! Please fork the repository and create a pull request. For major changes, please open an issue first to discuss.

## License
This project is licensed under the MIT License - see the `LICENSE.md` file for details.
