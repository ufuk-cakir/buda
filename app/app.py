from flask import Flask, render_template, request, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = b"concon/"

# Mock data (in a real application, this would come from a database)
mock_data = {
    "summary": "Your Instagram engagement is above average!",
    "stats": {"likes": 1234, "comments": 567, "posts_viewed": 8901},
    "watching": [
        {"name": "Account A", "value": 400},
        {"name": "Account B", "value": 300},
        {"name": "Account C", "value": 200},
        {"name": "Others", "value": 100},
    ],
    "watchers": [
        {"name": "Follower 1", "value": 500},
        {"name": "Follower 2", "value": 400},
        {"name": "Follower 3", "value": 300},
        {"name": "Others", "value": 200},
    ],
    "heatmaps": {
        "times_of_day": [
            [0, 0, 0, 0, 1, 2, 3, 4, 5, 4, 3, 2],
            [1, 1, 1, 1, 2, 3, 4, 5, 6, 5, 4, 3],
            [2, 2, 2, 2, 3, 4, 5, 6, 7, 6, 5, 4],
            [3, 3, 3, 3, 4, 5, 6, 7, 8, 7, 6, 5],
            [2, 2, 2, 2, 3, 4, 5, 6, 7, 6, 5, 4],
            [1, 1, 1, 1, 2, 3, 4, 5, 6, 5, 4, 3],
            [0, 0, 0, 0, 1, 2, 3, 4, 5, 4, 3, 2],
        ],
        "days_of_week": [
            [1, 2, 3, 4, 5, 6, 7],
            [2, 3, 4, 5, 6, 7, 8],
            [3, 4, 5, 6, 7, 8, 9],
            [4, 5, 6, 7, 8, 9, 10],
            [5, 6, 7, 8, 9, 10, 11],
            [6, 7, 8, 9, 10, 11, 12],
            [7, 8, 9, 10, 11, 12, 13],
        ],
    },
    "advice": [
        "Post more content during peak engagement times to increase your reach.",
        "Engage more with your top followers to boost your account's visibility.",
    ],
}


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/insta_login", methods=["POST"])
def insta_login():
    # Flash the message
    flash("Functionality not ready")
    return render_template("login.html")
    # Redirect the user back to the home page or any other page
    # return redirect(url_for("login"))  # You can also redirect to a different page


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if request.files["file"].filename == "":
            # print("error")
            flash("No file uploaded")
            return render_template("upload.html")
        # Here you would handle the file upload
        # For now, we'll just redirect to the loading page
        return redirect(url_for("loading"))
    return render_template("upload.html")


@app.route("/loading")
def loading():
    # In a real application, you would start processing the data here
    # For now, we'll just render the loading template
    return render_template("loading.html")


@app.route("/results")
def results():
    # In a real application, you would fetch the processed data here
    # For now, we'll use our mock data
    return render_template("results.html", data=mock_data)


if __name__ == "__main__":
    app.run(debug=True)
