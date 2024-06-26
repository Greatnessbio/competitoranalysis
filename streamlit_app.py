import streamlit as st
import bcrypt
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def check_password(username, password):
    if username in st.secrets["users"]:
        stored_password = st.secrets["users"][username]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
    return False

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
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return [word for word in tokens if word.isalnum() and word not in stop_words]

def perform_swot_analysis(text):
    words = preprocess_text(text)
    word_freq = Counter(words)
    
    # This is a simplified SWOT analysis. In a real-world scenario, you'd need more sophisticated NLP techniques.
    strengths = [word for word in word_freq.most_common(10) if word[0] in ['innovative', 'leading', 'best', 'quality']]
    weaknesses = [word for word in word_freq.most_common(10) if word[0] in ['challenge', 'improve', 'issue']]
    opportunities = [word for word in word_freq.most_common(10) if word[0] in ['growth', 'expansion', 'new']]
    threats = [word for word in word_freq.most_common(10) if word[0] in ['competitor', 'risk', 'challenge']]
    
    return {
        'Strengths': strengths,
        'Weaknesses': weaknesses,
        'Opportunities': opportunities,
        'Threats': threats
    }

def visualize_swot(swot_results):
    fig, ax = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('SWOT Analysis Results', fontsize=16)
    
    for i, (category, words) in enumerate(swot_results.items()):
        row = i // 2
        col = i % 2
        df = pd.DataFrame(words, columns=['Word', 'Frequency'])
        ax[row, col].bar(df['Word'], df['Frequency'])
        ax[row, col].set_title(category)
        ax[row, col].set_xticklabels(df['Word'], rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

def main():
    if not st.session_state.logged_in:
        login()
    else:
        st.title("SWOT Analysis App")
        url = st.text_input("Enter company website URL:")
        
        if st.button("Perform SWOT Analysis"):
            with st.spinner("Analyzing..."):
                text = scrape_website(url)
                swot_results = perform_swot_analysis(text)
                
                st.subheader("SWOT Analysis Results")
                for category, words in swot_results.items():
                    st.write(f"{category}:")
                    st.write(", ".join([word for word, _ in words]))
                
                fig = visualize_swot(swot_results)
                st.pyplot(fig)

if __name__ == "__main__":
    main()
