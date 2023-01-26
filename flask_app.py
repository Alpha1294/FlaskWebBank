from website import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Heroku will set the port envoronment variable for web traffic
    port = os.environ.get("PORT", 5000)
    app.run(debug=True, host="0.0.0.0", port=port)
