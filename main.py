from flask import Flask
from dotenv import load_dotenv
from controllers.routes import setup_routes

# Load environment variables from secrets.env
load_dotenv(dotenv_path="c:\\Users\\thego\\OneDrive\\Desktop\\portfolio\\Experiment 2\\secrets.env")

app = Flask(__name__)

# Setup routes
setup_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
