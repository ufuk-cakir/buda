from ..utils import load_data
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter


def calculate_total_likes(data):
    """Calculate the total number of likes."""
    return len(data["likes_media_likes"])


def extract_hours(data):
    """Extract hours from timestamps for activity analysis."""
    timestamps = [
        item["string_list_data"][0]["timestamp"] for item in data["likes_media_likes"]
    ]
    return [datetime.fromtimestamp(ts).hour for ts in timestamps]


def count_hourly_activity(hours):
    """Count the number of likes by hour."""
    return Counter(hours)


def display_statistics(total_likes, hourly_activity):
    """Print statistics for total likes and likes by hour."""
    print(f"Total number of likes: {total_likes}")
    print("Likes by hour of day:")
    for hour, count in sorted(hourly_activity.items()):
        print(f"{hour}:00 - {count} likes")


def plot_hourly_activity(hourly_activity):
    """Plot the number of likes by hour of the day."""
    plt.bar(hourly_activity.keys(), hourly_activity.values())
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Likes")
    plt.title("Instagram Activity by Hour")
    plt.xticks(range(0, 24))
    plt.show()


def analyze_likes(data):
    """Analyze likes data and display statistics and plot."""
    total_likes = calculate_total_likes(data)
    hours = extract_hours(data)
    hourly_activity = count_hourly_activity(hours)
    display_statistics(total_likes, hourly_activity)
    plot_hourly_activity(hourly_activity)

