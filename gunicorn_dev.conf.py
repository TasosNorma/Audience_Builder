# Development-specific settings while maintaining production parity
workers = 2  

# Use same worker class for consistency
worker_class = 'sync'

# Bind to localhost instead of 0.0.0.0 for development
bind = "127.0.0.1:10000"

# Match production timeout
timeout = 600

# Match production memory management
max_requests = 50
max_requests_jitter = 5

# Match production worker settings
# worker_tmp_dir = '/dev/shm' / This is commented out because it's linux specific.
worker_connections = 250

# Match production logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Development-specific additions
reload = True  # Enable auto-reload for development