from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

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
    "hourly_activity": {
        "16": 50,
        "17": 49,
        "13": 33,
        "8": 36,
        "19": 39,
        "12": 35,
        "9": 39,
        "18": 49,
        "15": 42,
        "23": 10,
        "21": 18,
        "11": 38,
        "5": 72,
        "10": 31,
        "6": 51,
        "14": 20,
        "0": 4,
        "20": 63,
        "7": 37,
        "22": 8,
        "3": 2,
        "4": 12,
        "1": 1,
        "2": 2,
    },
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
            flash("No file uploaded")
            return render_template("upload.html")
        return redirect(url_for("loading"))
    return render_template("upload.html")


@app.route("/loading")
def loading():
    # In a real application, you would start processing the data here
    # For now, we'll just render the loading template
    return render_template("loading.html")


@app.route("/results")
def results():
    data_dict = mock_data
    file_names = [
        "summary_categories.json",
        "liked_posts_category_counts.json",
        "day_of_week_activity_danny.json",
        "hour_of_day_likes_danny.json",
        "advice.json",
    ]
    data_names = ["watchers", "watching", "daily_activity", "hourly_activity", "advice"]
    data_directory = "data/"

    # Iterate over each file path in the provided list
    for i, file_name in enumerate(file_names):
        file_path = os.path.join(data_directory, file_name)
        if os.path.exists(
            os.path.join(data_directory, file_name)
        ) and file_name.endswith(".json"):
            try:
                with open(file_path, "r") as f:
                    # Load the JSON data from the file
                    data = json.load(f)

                    # Append the data to the dictionary
                    # Assuming data is a dictionary or key-value pairs
                    print(data_names[i])
                    data_dict[data_names[i]] = data

            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {file_name}")
            except Exception as e:
                print(f"An error occurred with file {file_name}: {e}")
        else:
            print(f"File does not exist or is not a JSON file: {file_name}")

    # print(data_dict)

    return render_template("results.html", data=data_dict)


if __name__ == "__main__":
    app.run(debug=True)
