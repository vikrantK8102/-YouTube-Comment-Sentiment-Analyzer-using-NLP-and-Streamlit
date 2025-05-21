import streamlit as st
import re
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googleapiclient.errors import HttpError
from langdetect import detect
import matplotlib.pyplot as plt

# Set up YouTube Data API
API_KEY = "AIzaSyAinTHL0TVddb1oDUXDZoUfr3LDNp1Jo0c"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to extract video ID from YouTube video URL


def extract_video_id(url):
    video_id_match = re.search(r"(?<=v=)[\w-]+", url)
    if video_id_match:
        return video_id_match.group(0)
    else:
        return None

# Function to fetch comments from YouTube video
def get_video_comments(video_id):
    try:
        comments = []
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=500,  # adjust as needed
            order="time",    # order by time
            textFormat="plainText"
        )
        response = request.execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            # Filter out non-English comments
            if is_english(comment):
                comments.append(comment)
        return comments
    except HttpError as e:
        if e.resp.status == 404:
            st.error("Video not found. Please enter a valid YouTube Video URL.")
            return []
        else:
            st.error("An error occurred while fetching comments.")
            return []

# Function to check if a comment is in English
def is_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except:
        return False

# Function to perform sentiment analysis and generate pie chart
def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    results = []
    for comment in comments:
        sentiment_score = analyzer.polarity_scores(comment)
        compound_score = sentiment_score['compound']
        if compound_score >= 0.05:
            sentiment_label = 'Positive'
        elif compound_score <= -0.05:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        results.append(sentiment_label)
    
    # Calculate percentage of each sentiment
    total_comments = len(results)
    positive_percentage = (results.count('Positive') / total_comments) * 100
    negative_percentage = (results.count('Negative') / total_comments) * 100
    neutral_percentage = (results.count('Neutral') / total_comments) * 100
    
    # Plotting the pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [positive_percentage, negative_percentage, neutral_percentage]
    colors = ['#66b3ff', '#ff9999', '#99ff99']  # Blue, Red, Green
    explode = (0.1, 0, 0)  # 1st slice (Positive)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  #  pie is drawn as a circle.

    return results, fig1

# Streamlit UI
st.title("YouTube Comment Sentiment Analyzer")

youtube_url = st.text_input("Enter YouTube Video URL:", key="youtube_url_input")
if st.button("Analyze"):
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            comments = get_video_comments(video_id)
            if comments:
                sentiment_results, fig = analyze_sentiment(comments)
                
                positive_comments = [comment for comment, sentiment in zip(comments, sentiment_results) if sentiment == 'Positive']
                negative_comments = [comment for comment, sentiment in zip(comments, sentiment_results) if sentiment == 'Negative']
                neutral_comments = [comment for comment, sentiment in zip(comments, sentiment_results) if sentiment == 'Neutral']
                
                st.subheader("Positive Comments")       
                st.write(positive_comments)
                
                st.subheader("Negative Comments")
                st.write(negative_comments)
                
                st.subheader("Neutral Comments")
                st.write(neutral_comments)
                
                st.subheader("Sentiment Distribution")
                st.pyplot(fig)  # Display the pie chart
                
            else:
                st.warning("No comments found for the given video.")
        else:
            st.warning("Invalid YouTube Video URL. Please enter a valid URL.")
    else:
        st.warning("Please enter a YouTube Video URL.")
