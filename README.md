
# SQL Generation Project with Gemini

## Overview

This project integrates Google’s Generative AI model (Gemini) with a Streamlit-based chatbot application to handle conversational responses, SQL query generation, and data summarization. The chatbot interacts with a MySQL database to fetch and display data according to the generated SQL queries.

## Features

- **Generative AI Responses**: Provides responses based on user input and conversation history.
- **SQL Query Generation**: Generates SQL queries for specific questions and executes them.
- **Data Summarization**: Summarizes data retrieved from the database if the query is a SELECT statement.
- **Chat History Handling**: Maintains conversation history to generate relevant responses and summaries.

## Getting Started

### Prerequisites

1. **Google API Key**: You need a Google API key to use the Gemini LLM. Follow the steps below to obtain one.

2. **Python Environment**: Ensure Python is installed on your machine.

### Obtain Google API Key

1. Open [Google API Key Creation Page](https://aistudio.google.com/app/apikey).
2. Click on “Create API Key”.
3. Accept the terms and conditions and click “Create API Key for New Project”.
4. Select the created project and click “Create API Key on existing project”.
5. Copy the secret API Key.

### Setup Environment

1. **Create a Virtual Environment**:
   - Open VS Code.
   - Create a virtual environment using the command:
     ```bash
     python -m venv venv
     ```

2. **Install Required Libraries**:
   - Activate the virtual environment and run:
     ```bash
     pip install streamlit python-dotenv mysql-connector-python google-generativeai pandas
     ```

3. **Create a .env File**:
   - In the project root, create a file named `.env`.
   - Add the following line with your Google API key:
     ```env
     GOOGLE_API_KEY=your_google_api_key
     ```

4. **Create Main Script**:
   - Create a file named `main.py` for the original workflow.

## Workflow

1. **Identify Question Type**:
   - **General**: Generate a response from the Gemini model and display it.
   - **Specific**: 
     - Check for relevant data in the chat history.
     - **If relevant data is found**: Summarize the data using Gemini and display it.
     - **If no relevant data is found**: 
       - Generate an SQL query using Gemini.
       - Execute the query and display the results.
       - Summarize the results if the query is a SELECT statement.

## Code Overview

- **Helper Functions**:
  - **Get Gemini Response**: Interacts with the Generative AI model to get responses based on conversation history and user prompts.
  - **Read SQL Queries**: Executes SQL queries for SELECT statements, converts results to CSV format, and returns them.
  - **Question Handling**: Identifies if the question is general or specific and finds relevant data in provided dataframes.
  - **Main Function**: Handles the overall data flow, uses helper functions, and manages the Streamlit web interface.

## User Manual

1. **Run the Application**:
   - Start the Streamlit application with the following command:
     ```bash
     streamlit run main.py
     ```

2. **Interact with the Chatbot**:
   - Open your web browser and navigate to the URL provided by Streamlit.
   - Type your questions to interact with the chatbot. It will generate and execute SQL queries based on your questions and provide responses.

## Contribution

Feel free to fork this repository and submit pull requests. For any issues or feature requests, please create an issue on GitHub.


