import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def check_password(username, password):
    # This is a simple, insecure way to check passwords. Do not use in production!
    return username in st.secrets["users"] and password == st.secrets["users"][username]

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_password(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Incorrect username or password")

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        st.error(f"Error scraping website: {str(e)}")
        return ""

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return [word for word in tokens if word.isalnum() and word not in stop_words]

def perform_swot_analysis(text):
    words = preprocess_text(text)
    word_freq = Counter(words)
    
    # This is a simplified SWOT analysis. In a real-world scenario, you'd need more sophisticated NLP techniques.
    strengths = [word for word, count in word_freq.most_common(10) if word in ['innovative', 'leading', 'best', 'quality']]
    weaknesses = [word for word, count in word_freq.most_common(10) if word in ['challenge', 'improve', 'issue']]
    opportunities = [word for word, count in word_freq.most_common(10) if word in ['growth', 'expansion', 'new']]
    threats = [word for word, count in word_freq.most_common(10) if word in ['competitor', 'risk', 'challenge']]
    
    return {
        'Strengths': strengths,
        'Weaknesses': weaknesses,
        'Opportunities': opportunities,
        'Threats': threats
    }

def visualize_swot(swot_results):
    for category, words in swot_results.items():
        if words:
            df = pd.DataFrame({'Word': words, 'Count': range(len(words), 0, -1)})
            st.subheader(category)
            st.bar_chart(df.set_index('Word'))
        else:
            st.subheader(category)
            st.write("No words found for this category.")

def main():
    if not st.session_state.logged_in:
        login()
    else:
        st.title("SWOT Analysis App")
        url = st.text_input("Enter company website URL:")
        
        if st.button("Perform SWOT Analysis"):
            if url:
                with st.spinner("Analyzing..."):
                    text = scrape_website(url)
                    if text:
                        swot_results = perform_swot_analysis(text)
                        st.subheader("SWOT Analysis Results")
                        visualize_swot(swot_results)
                    else:
                        st.error("Unable to retrieve content from the provided URL.")
            else:
                st.warning("Please enter a URL before performing the analysis.")

if __name__ == "__main__":
    main()
