from website import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = os.environ.get("PORT",5000) #Heroku will set the port envoronment variable for web traffic
    app.run(debug=False, host="0.0.0.0", port=port)
