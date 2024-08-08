import streamlit as st
from dotenv import load_dotenv
import os
import mysql.connector
import google.generativeai as genai
import pandas as pd
import time

# Load environment variables
load_dotenv()

# Configure GenerativeAI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(conversation_history, prompt, retries=3, delay=2):
    model = genai.GenerativeModel('gemini-pro')
    attempts = 0
    while attempts < retries:
        try:
            conversation = "\n".join(
                [
                    f"User: {entry['user']}\nBot: {entry.get('bot', '')}" 
                    for entry in conversation_history 
                    if 'user' in entry
                ]
            )

            summarized_history = "\n".join(
                [
                    f"Previous Summary: {entry['bot']}" 
                    for entry in conversation_history 
                    if 'summary' in entry
                ]
            )
            
            if not conversation:
                conversation = "No previous conversation available."

            final_prompt = f"{prompt}\n\nConversation History:\n{conversation}\n{summarized_history}\nUser: {conversation_history[-1].get('user', '')}\nBot:"
            response = model.generate_content([final_prompt])
            return response.text
        
        except Exception as e:
            st.write(f"Attempt {attempts+1} failed with error: {e}")
            attempts += 1
            if attempts == retries:
                raise e
            time.sleep(delay)

def read_sql_all_query(sql):
    host = 'localhost'
    user = 'root'
    password = 'root'
    database = 'Project_Main'
 
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
 
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def read_sql_query(sql):
    host = 'localhost'
    user = 'root'
    password = 'root'
    database = 'Project_Main'
 
    conn = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database
    )
    cur = conn.cursor()
    cur.execute("SET SESSION sql_mode=(SELECT REPLACE(@@SESSION.sql_mode, 'ONLY_FULL_GROUP_BY', ''))")
    
    all_results = []
    
    for result in cur.execute(sql, multi=True):
        if result.with_rows:
            rows = result.fetchall()
            column_names = [i[0] for i in result.description]
            df = pd.DataFrame(rows, columns=column_names)
            all_results.append(df)
    
    cur.close()
    conn.close()
    
    return all_results

def is_general_question(question):
    general_keywords = ['hello', 'hi', 'who are you', 'introduce', 'help', 'thanks', 'thank you', 'Good Morning', 'Good Afternoon']
    return any(keyword in question.lower() for keyword in general_keywords)

def find_relevant_data(question, dataframes):
    for df in dataframes:
        if not df.empty and any(col in question.lower() for col in df.columns.str.lower()):
            return df
    return None

def main():
    MAX_HISTORY_LENGTH = 100

    st.set_page_config(layout="wide")
    st.markdown(
        """
        <style>
        .main {
        background-color: #FFFFFF;
        color: #0e1117;
        }
        .css-1v0mbdj.e1tzin5v0 {
            background-color: #FFFFFF;
        }
        body {
            background-image: url('https://images.rawpixel.com/image_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIyLTA1L3B4MTU4NDgwMy1pbWFnZS1rd3Z4dmxjai5qcGc.jpg');
            background-size: cover;
            color: white;
        }
        .chat-history {
            height: 400px;
            overflow-y: auto;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
        }
        .user-question {
            background: rgba(0, 123, 255, 0.1);
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            
        }
        .bot-response {
            background: rgba(255, 193, 7, 0.1);
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    prompt_1 = """
        You will generate a valid SQL query that fetches the information the user wants from the database. User will be generic in framing his/her request, but you need to understand and relate which tables and columns to fetch that match the user intent.
        For example: User asks "Give me the details of the Product with max price"
        Reasoning: Products details will be in Product table and if you read the table details you will find that the columns to pick out are Price_MRP. You need to generate SQL query to get unique Product max price_mrp. 

        Here is the Schema Description of the database. You will find all the tables and column details. Use those names to insert into your SQL queries. We will run the query to get the response from the database. 
        CompanyX Database Schema (Stores information on customers, products, sales and orders) 
        1. Product:
           - Product_ID (VARCHAR, PK)
           - Product_Name (VARCHAR)
           - Price_MRP (DECIMAL(10,2))
           - Price_SALE (DECIMAL(10,2))
           - Quantity (FLOAT)
         
        2. Customers:
           - Index1 (INT)
           - Customer_Id (VARCHAR, PK)
           - First_Name (VARCHAR)
           - Last_Name (VARCHAR)
           - Company (VARCHAR)
           - City (VARCHAR)
           - Country (VARCHAR)
           - Email (VARCHAR)
           - Subscription_Date (DATE)
           - Sex (CHAR(7))
           - Date_of_birth (DATE)
         
        3. Orders:
           - Order_ID (VARCHAR, PK)
           - Customer_ID (VARCHAR, FK to Customers)
           - Customer_Status (VARCHAR)
           - Date_Order_Placed (DATE)
           - Delivery_Date (DATE)
           - Product_ID (VARCHAR, FK to Product)
           - Quantity_Ordered (INT)
           - Total_Retail_Price (DECIMAL(10,2))
           - Cost_Price_Per_Unit (DECIMAL(10,2))
           - Profit (DECIMAL(10,2))
         
        4. Sales:
           - Invoice_ID (VARCHAR, PK)
           - Customer_ID (VARCHAR, FK to Customers)
           - Product_ID (VARCHAR, FK to Product)
           - Branch (VARCHAR)
           - City (VARCHAR)
           - Customer_Type (VARCHAR)
           - Quantity (INT)
           - Tax_5 (DECIMAL(10,2))
           - Total (DECIMAL(10,2))
           - Sale_Date (DATE)
           - Sale_Time (TIME)
           - Payment (VARCHAR)
           - COGS (DECIMAL(10,2))
           - Gross_Margin_Percentage (DECIMAL(10,2))
           - Gross_Income (DECIMAL(10,2))
           - Rating (DECIMAL(3,1))
           - Price_MRP (DECIMAL(10,2))
           - Price_SALE (DECIMAL(10,2))
           
           For example,
            Example 1 - How many entries of records are present in the Product table?
            Response: SELECT COUNT(*) FROM Product;

            Example 2 - What are the details of the Product with Product_ID '24ABC01'?
            Response: SELECT * FROM Product WHERE Product_ID = '24ABC01';

            Example 3 - List the products whose Price_MRP exceeds 49.
            Response: SELECT * FROM Product WHERE Price_MRP > 49;

            Example 4 - Retrieve products where the Price_MRP falls within the range of 100 to 250.
            Response: SELECT * FROM Product WHERE Price_MRP BETWEEN 100 AND 250;

            Example 5 - What are the details of all products sorted in ascending order based on their Price_MRP?
            Response: SELECT * FROM Product ORDER BY Price_MRP ASC;

            Example 6 - What is the total quantity of all products available?
            Response: SELECT SUM(Quantity) AS Total_Quantity FROM Product;

            Example 7 - Give me top 5 best customers?
            Response: SELECT C.Customer_Id, C.First_Name, C.Last_Name, COUNT(O.Order_ID) AS Number_of_Orders FROM Orders O JOIN Customers C ON O.Customer_ID = C.Customer_Id GROUP BY C.Customer_Id, C.First_Name, C.Last_Name ORDER BY Number_of_Orders DESC LIMIT 5;

            Example 8 - Retrieve all orders along with the first name, last name, and email of the customers who placed them.
            Response: SELECT O.Order_ID, O.Date_Order_Placed, C.First_Name, C.Last_Name, C.Email FROM Orders O JOIN Customers C ON O.Customer_ID = C.Customer_Id;

            Example 9 - Find the total sales amount for each product.
            Response: SELECT P.Product_Name, SUM(S.Total) AS Total_Sales FROM Sales S JOIN Product P ON S.Product_ID = P.Product_ID GROUP BY P.Product_Name;

            Example 10 - List the number of orders placed by customers in each city.
            Response: SELECT C.City, COUNT(O.Order_ID) AS Number_of_Orders FROM Orders O JOIN Customers C ON O.Customer_ID = C.Customer_Id GROUP BY C.City;

            Example 11 - Find the total quantity sold and total sales amount for each product at each branch.
            Response: SELECT S.Branch, P.Product_Name, SUM(S.Quantity) AS Total_Quantity_Sold, SUM(S.Total) AS Total_Sales FROM Sales S JOIN Product P ON S.Product_ID = P.Product_ID GROUP BY S.Branch, P.Product_Name;

            Example 12 - List all products that have never been sold.
            Response: SELECT P.Product_ID, P.Product_Name FROM Product P LEFT JOIN Sales S ON P.Product_ID = S.Product_ID WHERE S.Product_ID IS NULL;
       
            Response Instructions: 
            1. As per the above examples, Give only the SQL query in plain text use 
            2. Don't generate the response with any special characters or symbols like quotes,@,; etc at starting or ending and don't add SQL
            3. If the query is big and need to execute more than 1 query then use subqueries or joins concepts 
            4. When 2 tables information is required then use joins concept and perfectly join both tables and execute the query.
            5. If the user want to create a table in the database, use the database name 
            6. If you have encounter some random question then answer if it is related to Schema or if it is a genral question like introduction or general question part. 
    """

    prompt_2 = """
       The table information above was retrieved from the database to answer the user query. Use only that information and construct a meaningful text response for the user.
        You are an expert in analyzing table information and providing insightful textual summaries by understanding the context of the user query, analyzing the table information and then generating a response.
        Always try to understand how the table information can answer the user's question, if not respond saying the information is not available.
                
        Response Instructions

        1. Always answer in the context of the user's query.
        2. Analyze the table to understand the key points, statistics, and trends relevant to the query.
        3. every time Provide a concise yet informative summary, including any relevant statistical insights, mathematical operations, and meaningful interpretations to provide a comprehensive understanding of the data.
        4. If you have encounter some random question then answer if it is related to Schema or if it is a genral question like introduction or general question part. 
        6. Explain the statistics like mean median mode if needed. 
        7. you need to explain table information in proper english text.
        Example:
        What is the most expensive product?
        The most expensive product in the given table is the “Premia Kashmiri Chilli Powder” with a maximum retail price (MRP) of 880.00. 

        What are the top 3 products in terms of pricing?
        The “Premia Kashmiri Chilli Powder” stands out as the most expensive product with an MRP of 880.00.
        The “Premia Pista Plain (Pistachios)” follows with an MRP of 358.00.
        The “Date Crown Fard (Khajur)” is the least expensive among the top 3, priced at 257.00.
    """

    prompt_general = """
    You are a conversational chatbot designed to answer general questions, provide introductions, and assist users with basic information about the service. Our service excels in summarizing data, Capable of doing CRUD Operations and generating SQL queries to help users interact with their datasets efficiently.

    Example questions:
        Who are you?
        How can you help me?
        Tell me about this service.
        Can you help me summarize my data?
        Can you generate SQL queries for my database?

    Response Instructions:
        Provide a polite and helpful response to general questions.
        Keep the responses short, informative, and engaging.
        Highlight the functionalities of summarizing data and generating SQL queries when relevant.

    This service includes a comprehensive database schema for managing products, customers, orders, and sales:

    Product:
        Product_ID (VARCHAR, PK)
        Product_Name (VARCHAR)
        Price_MRP (DECIMAL(10,2))
        Price_SALE (DECIMAL(10,2))
        Quantity (FLOAT)

    Customers:
        Index1 (INT)
        Customer_Id (VARCHAR, PK)
        First_Name (VARCHAR)
        Last_Name (VARCHAR)
        Company (VARCHAR)
        City (VARCHAR)
        Country (VARCHAR)
        Email (VARCHAR)
        Subscription_Date (DATE)
        Sex (CHAR(7))
        Date_of_birth (DATE)

    Orders:
        Order_ID (VARCHAR, PK)
        Customer_ID (VARCHAR, FK to Customers)
        Customer_Status (VARCHAR)
        Date_Order_Placed (DATE)
        Delivery_Date (DATE)
        Product_ID (VARCHAR, FK to Product)
        Quantity_Ordered (INT)
        Total_Retail_Price (DECIMAL(10,2))
        Cost_Price_Per_Unit (DECIMAL(10,2))
        Profit (DECIMAL(10,2))

    Sales:
        Invoice_ID (VARCHAR, PK)
        Customer_ID (VARCHAR, FK to Customers)
        Product_ID (VARCHAR, FK to Product)
        Branch (VARCHAR)
        City (VARCHAR)
        Customer_Type (VARCHAR)
        Quantity (INT)
        Tax_5 (DECIMAL(10,2))
        Total (DECIMAL(10,2))
        Sale_Date (DATE)
        Sale_Time (TIME)
        Payment (VARCHAR)
        COGS (DECIMAL(10,2))
        Gross_Margin_Percentage (DECIMAL(10,2))
        Gross_Income (DECIMAL(10,2))
        Rating (DECIMAL(3,1))
        Price_MRP (DECIMAL(10,2))
        Price_SALE (DECIMAL(10,2))
    """

    st.title('Gemini Chatbot with Streamlit')

    col1, col2 = st.columns([2, 3])

    with col1:
        st.header("User Interaction")
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'dataframes' not in st.session_state:
            st.session_state.dataframes = []

        question = st.text_input('Enter your question here:')

        if st.button('Get Response'):
            st.session_state.history.append({'user': question})
            
            if len(st.session_state.history) > MAX_HISTORY_LENGTH:
                st.session_state.history = st.session_state.history[-MAX_HISTORY_LENGTH:]
            
            if is_general_question(question):
                try:
                    general_response = get_gemini_response(st.session_state.history, prompt_general)
                    st.session_state.history.append({'bot': general_response})
                    st.write(general_response)
                except Exception as e:
                    error_message = "Error generating response from Gemini API: " + str(e)
                    st.session_state.history.append({'bot': error_message})
                    st.write(error_message)
            else:
                relevant_data = find_relevant_data(question, st.session_state.dataframes)
                if relevant_data is not None:
                    try:
                        summarize_prompt = relevant_data.to_string(index=False) + "\n" + prompt_2
                        summary_response = get_gemini_response(st.session_state.history, summarize_prompt)
                        st.session_state.history.append({'bot': summary_response, 'summary': summary_response})
                        st.write("Summary Response:")
                        st.write(summary_response)
                    except Exception as e:
                        error_message = "Error generating response from Gemini API: " + str(e)
                        st.session_state.history.append({'bot': error_message})
                        st.write(error_message)
                else:
                    try:
                        generated_query = get_gemini_response(st.session_state.history, prompt_1)
                        st.session_state.history.append({'bot': "Generated SQL Query:\n" + generated_query})
                        st.write("Generated SQL Query:")
                        st.write(generated_query)
                        
                        if generated_query.strip().lower().startswith("select"):
                            try:
                                response_dfs = read_sql_query(generated_query)
                                if response_dfs:
                                    for response_df in response_dfs:
                                        st.session_state.dataframes.append(response_df)
                                        st.write(response_df)
                                        df_summary = response_df.to_string(index=False)
                                        summarize_prompt = df_summary + "\n" + prompt_2
                                        summary_response = get_gemini_response(st.session_state.history, summarize_prompt)
                                        st.session_state.history.append({'bot': "Summary Response:\n" + summary_response, 'summary': summary_response})
                                        st.write("Summary Response:")
                                        st.write(summary_response)
                                else:
                                    no_data_message = "No data found."
                                    st.session_state.history.append({'bot': no_data_message})
                                    st.write(no_data_message)
                                    
                            except Exception as e:
                                error_message = "Summarization error" + str(e)
                                st.session_state.history.append({'bot': error_message})
                                st.write(error_message)
                        else:
                            try:
                                read_sql_all_query(generated_query)
                                success_message = "Query executed successfully."
                                st.session_state.history.append({'bot': success_message})
                                st.write(success_message)
                            except Exception as e:
                                error_message = "Error executing SQL query: " + str(e)
                                st.session_state.history.append({'bot': error_message})
                                st.write(error_message)
            
                    except Exception as e:
                        error_message = "Error generating response from Gemini API: " + str(e)
                        st.session_state.history.append({'bot': error_message})
                        st.write(error_message)

    with col2:
        st.header("Chat History")
        if st.session_state.history:
            for entry in st.session_state.history:
                if 'user' in entry:
                    st.markdown(f'<div class="user-question">{entry["user"]}</div>', unsafe_allow_html=True)
                if 'bot' in entry:
                    st.markdown(f'<div class="bot-response">{entry["bot"]}</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()

