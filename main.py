from app.config import create_app
import os

app = create_app()

@app.route("/")
def welcome():
    return "bro take meds"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # app.run(host="0.0.0.0", port=port, debug=False)