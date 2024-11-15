
# Server socket
bind = "0.0.0.0:8050"

# Worker processes
workers = 16
threads = 4  # Optional: thread count per worker
timeout = 200

# Logging
accesslog = "-"  # Access log to stdout
errorlog = "-"   # Error log to stdout
loglevel = "debug"  # Log level (debug, info, warning, error, critical)

# Preload app
preload_app = True