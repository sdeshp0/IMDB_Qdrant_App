k8s_yaml(['kubernetes/qdrant_secret.yaml',
          'kubernetes/qdrant.yaml',
          'kubernetes/loader_job.yaml',
          'kubernetes/app.yaml'
          ])

k8s_resource(
    workload='imdb-app',
    port_forwards='8501:8501'
    )



