from app import create_app
import os
app = create_app()

# This is for deployment - use environment variable PORT if available
port = int(os.environ.get("PORT", 10000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)