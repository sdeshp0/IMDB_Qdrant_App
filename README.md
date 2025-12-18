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

## 🚀 How to Run Locally using Docker Compose

### 1. Clone the repo
```bash
git clone https://github.com/sdesh0/IMDB_Qdrant_App.git
cd IMDB_Qdrant_App
```

### 2. Build Images

```bash
docker-compose up --build
```

### 3. Start core services (Qdrant + Streamlit app)

```bash
docker-compose up qdrant app
```

This will:
- Start **Qdrant** on port 6333 with persistent storage
- Launch the **Streamlit app** on port 8501

### 4. Load data manually (one-off job)

```bash
docker-compose run --rm loader
```

This will:
- Delete any existing collection from Qdrant
- Shuffle the IMDB dataset and sample reviews (default: 2000)
- Embed reviews and insert them into Qdrant
- Print the positive/negative distribution for verification

### 5. Open the app

- Streamlit dashboard -> http://localhost:8501
- Qdrant dashboard -> http://localhost:6333/dashboard

### 6. Stop the app

```bash
docker-compose down
```
This will stop and remove containers but will keep volumes so that data persists.

If you also want to remove the volumes, use:

```bash
docker-compose down -v
```

### 🛠 Notes on Persistence

- Qdrant data is stored in a Docker volume (qdrant_storage) so it survives container restarts.
- The loader always resets the collection when run, ensuring reproducibility.
- Each loader run shuffles the dataset, so the sentiment distribution varies (balanced mix of positives/negatives).

### 🔑 Note on Secrets Management

While this demo app does not strictly require secrets, an API key has been created to access the Qdrant client.

The API key has been passed directly in docker-compose.yaml:

```yaml
environment:
  QDRANT__SERVICE__API_KEY: supersecretkey
  QDRANT_API_KEY: supersecretkey
```

A better practice for local development is to store the API key in a .env file and then reference it in Compose
```env
QDRANT_API_KEY=supersecretkey
```

```yaml
env_file:
  - .env
```

---

## ☸️ Kubernetes Quickstart

This project also includes Kubernetes manifests for deployment.

- **Qdrant** → Vector database with persistent storage.
- **Streamlit App** → Interactive dashboard.
- **Loader Job** → One-off job to populate Qdrant with IMDB embeddings.

Deployment Order:
```bash
kubectl apply -f kubernetes/qdrant_secret.yaml
kubectl apply -f kubernetes/qdrant.yaml
kubectl apply -f kubernetes/app.yaml
kubectl apply -f kubernetes/loader_job.yaml
```

## ☸️ Kubernetes Detailed

### 1. Build & Push Images
Make sure your app and loader images are available in a registry (e.g., DockerHub):
```bash
docker build -t your-dockerhub-username/imdb_app:latest ./app
docker build -t your-dockerhub-username/imdb_loader:latest ./loader
docker push your-dockerhub-username/imdb_app:latest
docker push your-dockerhub-username/imdb_loader:latest
```

⚠️ Caveat: If the image name in your manifests does not match exactly what you pushed, pods will fail with ImagePullBackOff.

### 2. Deploy Secrets
```bash
kubectl apply -f kubernetes/qdrant_secret.yaml
```

### 3. Deploy Qdrant
```bash
kubectl apply -f kubernetes/qdrant.yaml
```
- Creates a PersistentVolumeClaim for storage.
- Deploys Qdrant with one replica.
- Injects the secret into Qdrant's environment.
- Exposes it as a Service on port 6333.

check pod status:
```bash
kubectl get pods
```

### 4. Deploy the Streamlit App
```bash
kubectl apply -f kubernetes/app.yaml
```

- Deploys the Streamlit dashboard.
- Exposes it via a Service on port 8501 (NodePort or LoadBalancer).
- References the secret in the app

Check service details:
```bash
kubectl get svc imdb-app
```

Example Output:
```bash
NAME       TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
imdb-app   NodePort   10.96.12.34    <none>        8501:30747/TCP   5m
```
Here, 30747 is the NodePort. In this example the app can be accessed at http://localhost:30747.

As the NodePort has been removed, use the port-forwarding command below so that the app can be accessed at 
http://localhost:8501


On cloud providers, set Service type to LoadBalancer and use the external IP to access the app.

Port forwarding:
```bash
kubectl port-forward svc/imdb-app 8501:8501
```

### 5. Run the Loader Job
```bash
kubectl apply -f kubernetes/loader_job.yaml
```

- Runs the loader once to populate Qdrant with IMDB embeddings.
- Injects the secret into the loader job
- Job exits after completion.

⚠️ Caveat: Jobs are immutable. If you re‑apply with changes, you’ll see something like:

```bash
The Job "imdb-loader" is invalid: spec.template: field is immutable
```

Fix this by deleting and re-applying:

```bash
kubectl delete job imdb-loader
kubectl apply -f kubernetes/loader_job.yaml
```

### 6. Watch Logs

Monitor the loader job:
```bash
kubectl logs -f job/imdb-loader
```

Expected Output should have something like:
```bash
✅ Loaded 2000 IMDB reviews into Qdrant (1000 positives, 1000 negatives)
```
This indicates that the imdb-loader job has executed and loaded data into Qdrant

### 7. Verify Data in Qdrant

Open the Qdrant dashboard:
```bash
http://localhost:<qdrant-nodeport>/dashboard
```

Or check collections using CLI:
```bash
kubectl exec -it <qdrant-pod-name> -- curl http://localhost:6333/collections
```

### 8. Common Issues and Fixes

- **ImagePullBackOff** -> Your image name/tag doesn’t match what’s in DockerHub.
  - Run docker push <username>/imdb-app:latest and update manifests.
- **Job immutability error** -> Delete the old job before re‑applying.
  ```bash
  kubectl delete job imdb-loader
  ```
- **Version mismatch warning** ->
  ```bash
  UserWarning: Qdrant client version 1.16.1 is incompatible with server version 1.10.0
  ```
  - Fix by upgrading Qdrant server image in qdrant.yaml:
  image: qdrant/qdrant:v1.16.1

### 9. Access Services (Recap)
- Streamlit app → via NodePort/LoadBalancer on port 8501.
- Qdrant dashboard → via port 6333.

### 10. Stop App and Services (Docker Desktop)

Assuming you are running Kubernetes via Docker Desktop you can stop the app and its services in two ways:
- Stop workloads but keep cluster running:
  ```bash
  kubectl delete -f kubernetes/app.yaml
  kubectl delete -f kubernetes/qdrant.yaml
  kubectl delete -f kubernetes/loader_job.yaml
  ```
- Wipe everything in the namespace:
  ```bash
  kubectl delete all --all 
  ```
- Check the cleanup:
  ```bash
  kubectl get pods
  ```
  This should return something like: No resources found

Docker Desktop keeps Kubernetes running in the background. To fully stop the cluster, you can disable Kubernetes in
Docker Desktop settings: *Preferences -> Kubernetes -> uncheck “Enable Kubernetes”*

⚠️ Note: kubectl only manages workloads. To stop the cluster itself, you must toggle Kubernetes in Docker Desktop.

### 🛠 Notes on Persistence
- Qdrant data is stored in a PVC (qdrant-pvc) so it survives pod restarts.
- The loader job always resets the collection when run, ensuring reproducibility.
- Each loader run shuffles the dataset, so the sentiment distribution varies.

### 🔑 Secrets Management Notes
- Base64 encoding ≠ encryption. Enable encryption at rest for stronger security.
- Use RBAC to restrict access to secrets.
- Don’t commit secrets to Git — use .env for Compose and Secrets for Kubernetes.
- Rotate secrets regularly.
- In production, consider external secret managers (Vault, AWS Secrets Manager, Azure Key Vault).


## ☸️ Using Tilt

With Tilt installed, the kubernetes deployment can be run based on the commands set up in the Tiltfile.

### Tiltfile Contents

```commandline
k8s_yaml(['kubernetes/qdrant_secret.yaml',
          'kubernetes/qdrant.yaml',
          'kubernetes/loader_job.yaml',
          'kubernetes/app.yaml'
          ])

k8s_resource(
    workload='imdb-app',
    port_forwards='8501:8501'
    )
```

The Tiltfile currently contains two commands.
1. The first command ```k8s_yaml()``` is equivalent to running kubectl apply on each of the yaml manifests.
2. The second command ```k8s_resource()``` is used to set up port-forwarding for the imdb-app

### Running Tilt

Run tilt using the command
```bash
tilt up
```

After running this command, note the response shown in the CLI. Hit ```spacebar``` to open the Tilt browser to view the
kubernetes objects in the browser-based Tilt environment.

