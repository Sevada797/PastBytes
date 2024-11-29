import argparse
import requests
from datetime import datetime, timedelta, timezone

# Function to get Wayback Machine snapshots
def get_wayback_snapshot(url, date):
    api_url = f"http://archive.org/wayback/available?url={url}&timestamp={date}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        snapshots = data.get("archived_snapshots", {})
        closest = snapshots.get("closest", {})
        return closest.get("url"), closest.get("status", None), closest.get("timestamp")
    return None, None, None

# Function to compare byte sizes
def compare_snapshots(url, days, delta=0):
    today = datetime.now(timezone.utc)  # Use timezone-aware datetime in UTC
    day_before = today - timedelta(days=days)

    today_str = today.strftime("%Y%m%d")
    day_before_str = day_before.strftime("%Y%m%d")

    current_snapshot_url, _, _ = get_wayback_snapshot(url, today_str)
    previous_snapshot_url, _, _ = get_wayback_snapshot(url, day_before_str)

    if not current_snapshot_url or not previous_snapshot_url:
        print(f"No snapshots available for {url} on the given dates.")
        return

    # Get byte size for the snapshots
    current_response = requests.get(current_snapshot_url)
    previous_response = requests.get(previous_snapshot_url)

    current_size = len(current_response.content)
    previous_size = len(previous_response.content)

    # Compare sizes
    if abs(current_size - previous_size) > delta:
        print(f"Found major code changes at endpoint {url}: Byte size difference is {abs(current_size - previous_size)} bytes.")
    else:
        print(f"No major changes found for {url}. Difference is within {delta} bytes.")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Monitor website changes using Wayback Machine snapshots.")
    
    # Optionally accept file input or direct URLs
    parser.add_argument("-f", "--file", type=str, help="File containing list of URLs to monitor.")
    parser.add_argument("urls", nargs="*", help="URL or list of URLs to monitor.")
    parser.add_argument("-d", "--days", type=int, default=3, help="Number of days to compare (default: 3).")
    parser.add_argument("--delta", type=int, default=0, help="Delta threshold for byte size changes (default: 0).")

    args = parser.parse_args()

    # If a file is provided, read URLs from the file
    if args.file:
        try:
            with open(args.file, 'r') as file:
                urls_to_check = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            print(f"Error: The file {args.file} was not found.")
            return
    else:
        urls_to_check = args.urls

    # If no URLs are provided, print an error message
    if not urls_to_check:
        print("Error: No URLs or file provided. Please provide URLs either via command line or a file.")
        return

    # Check each URL from the list
    for url in urls_to_check:
        print(f"Checking {url} for changes in the past {args.days} days...")
        compare_snapshots(url, args.days, args.delta)

if __name__ == "__main__":
    main()
