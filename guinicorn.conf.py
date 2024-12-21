# Reduce to 2 workers due to limited RAM
workers = 2

# Use async worker to handle concurrent requests efficiently
worker_class = 'aiohttp.worker.GunicornWebWorker'

# Bind to all network interfaces
bind = "0.0.0.0:10000"

# Keep timeout high for long-running processes
timeout = 600

# Aggressive memory management
max_requests = 50
max_requests_jitter = 5

# Reduce worker memory footprint
worker_tmp_dir = '/dev/shm'
worker_connections = 250

# Memory limits
max_requests_jitter = 5
worker_memory_limit = "200M"  # Limit each worker to 200MB

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'