import streamlit as st
from qdrant_client import QdrantClient
import pandas as pd
import re
import altair as alt

st.title("🎬 IMDB Sentiment Explorer")

# Connect to Qdrant
client = QdrantClient(host="qdrant", port=6333)

# Fetch a batch of reviews to populate analytics + dropdown
results, _ = client.scroll(collection_name="imdb_reviews", limit=500)
review_options = {r.payload["text"]: r for r in results}

# --- Sentiment distribution chart ---
labels = [r.payload["label"] for r in results]
df = pd.DataFrame(labels, columns=["label"])
df["sentiment"] = df["label"].map({0: "Negative", 1: "Positive"})
st.write("### Sentiment Distribution of Loaded Reviews")
st.bar_chart(df["sentiment"].value_counts())

# --- Sentiment-specific analytics ---
st.write("### Sentiment Analytics")

# Separate reviews
pos_reviews = [r.payload["text"].lower() for r in results if r.payload["label"] == 1]
neg_reviews = [r.payload["text"].lower() for r in results if r.payload["label"] == 0]

def get_top_keywords(texts, stopwords, n=10):
    words = []
    for t in texts:
        words.extend(re.findall(r"\b[a-z]{3,}\b", t))
    filtered = [w for w in words if w not in stopwords]
    return pd.Series(filtered).value_counts().head(n)

stopwords = {
    "the","and","for","with","that","this","was","but","not","you","are","have","had",
    "they","from","his","her","she","him","their","them","our","out","all","one","just",
    "like","can","will","would","could","should","about","when","what","which"
}

pos_freq = get_top_keywords(pos_reviews, stopwords)
neg_freq = get_top_keywords(neg_reviews, stopwords)

col1, col2 = st.columns(2)
with col1:
    st.write("#### Positive Reviews - Top Keywords")
    st.bar_chart(pos_freq)
with col2:
    st.write("#### Negative Reviews - Top Keywords")
    st.bar_chart(neg_freq)

# --- Metric summary: average review length ---
pos_lengths = [len(r.split()) for r in pos_reviews]
neg_lengths = [len(r.split()) for r in neg_reviews]

avg_pos_len = sum(pos_lengths) / len(pos_lengths) if pos_lengths else 0
avg_neg_len = sum(neg_lengths) / len(neg_lengths) if neg_lengths else 0

st.write("### Review Length Summary")
col3, col4 = st.columns(2)
with col3:
    st.metric("Avg Positive Review Length (words)", f"{avg_pos_len:.1f}")
with col4:
    st.metric("Avg Negative Review Length (words)", f"{avg_neg_len:.1f}")

# --- Trend visualization: histogram or boxplot toggle ---
st.write("### Review Length Distribution by Sentiment")

trend_df = pd.DataFrame({
    "length": pos_lengths + neg_lengths,
    "sentiment": ["Positive"] * len(pos_lengths) + ["Negative"] * len(neg_lengths)
})

view_option = st.radio(
    "Choose visualization type:",
    ("Histogram", "Boxplot"),
    horizontal=True
)

if view_option == "Histogram":
    chart = alt.Chart(trend_df).mark_bar(opacity=0.6).encode(
        x=alt.X("length", bin=alt.Bin(maxbins=30), title="Review Length (words)"),
        y="count()",
        color="sentiment"
    ).properties(width=600, height=400)
else:  # Boxplot
    chart = alt.Chart(trend_df).mark_boxplot().encode(
        x="sentiment",
        y="length",
        color="sentiment"
    ).properties(width=600, height=400)

st.altair_chart(chart, width="stretch")

# --- Dropdown to select a review ---
selected_text = st.selectbox("Choose a review:", list(review_options.keys()))

if selected_text:
    query = review_options[selected_text]

    st.write("### Selected Review")
    st.write(query.payload["text"])
    st.write(f"Sentiment: {'Positive' if query.payload['label'] == 1 else 'Negative'}")

    # --- Word frequency analysis for selected review ---
    text = query.payload["text"].lower()
    words = re.findall(r"\b[a-z]{3,}\b", text)
    filtered = [w for w in words if w not in stopwords]
    freq = pd.Series(filtered).value_counts().head(10)

    st.write("### Top Keywords in Selected Review")
    st.bar_chart(freq)