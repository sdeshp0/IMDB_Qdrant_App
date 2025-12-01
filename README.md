# 🎬 IMDB Sentiment Explorer Dashboard

An interactive Streamlit dashboard powered by **Qdrant** and the HuggingFace **IMDB dataset**.  
This project demonstrates how to build a full ML app pipeline with vector search, data visualization, and containerized deployment using Docker Compose (and later Kubernetes).

---

## 📖 What the App Does

- Loads the IMDB movie reviews dataset from HuggingFace.
- Embeds reviews using a SentenceTransformer model (`sentence-transformers/all-MiniLM-L6-v2`).
- Stores embeddings + metadata (review text, sentiment label) in a Qdrant vector database.
- Provides a Streamlit dashboard to:
  - Browse random reviews with sentiment labels.
  - Visualize sentiment distribution (positive vs negative).
  - Explore sentiment analytics:
    - **Top keywords by sentiment** (positive vs negative).
    - **Average review length** metrics.
    - **Trend visualization** of review lengths with a toggle (histogram or boxplot).
  - Explore semantic similarity: pick a review and see its nearest neighbors in embedding space.

This app is designed as a **learning portfolio project** to showcase:

- Machine Learning/NLP (sentiment analysis, embeddings).
- Vector databases (Qdrant).
- Interactive dashboards (Streamlit).
- Containerization & orchestration (Docker, Docker Compose, Kubernetes).

---



## 📂 Project Structure

- IMDB_Qdrant_App
  - docker-compose.yaml
  - loader/
    - load_data.py
    - Dockerfile
    - requirements.txt
  - app/
    - app.py
    - Dockerfile
    - requirements.txt

- **loader/** -> Script + container to load IMDB data into Qdrant (manual job).
- **app/** -> Streamlit dashboard that queries Qdrant.
- **docker-compose.yaml** -> Defines services: Qdrant, Loader, Streamlit app.

---

## 🚀 How to Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/sdesh0/IMDB_Qdrant_App.git
cd IMDB_Qdrant_App
```

### 2. Start core services (Qdrant + Streamlit app)

```bash
docker-compose up app qdrant --build
```

This will:
- Start **Qdrant** on port 6333 with persistent storage
- Launch the **Streamlit app** on port 8501

### 3. Load data manually (on-off job)

```bash
docker-compose run --rm loader
```

This will:
- Delete any existing collection from Qdrant
- Shuffle the IMDB dataset and sample reviews (default: 2000)
- Embed reviews and insert them into Qdrant
- Print the positive/negative distribution for verification

### 3. Open the app

- Streamlit dashboard -> http://localhost:8501
- Qdrant dashboard -> http://localhost:6333/dashboard

## 🛠 Notes on Persistence

- Qdrant data is stored in a Docker volume (qdrant_storage) so it survives container restarts.
- The loader always resets the collection when run, ensuring reproducibility.
- Each loader run shuffles the dataset, so the sentiment distribution varies (balanced mix of positives/negatives).