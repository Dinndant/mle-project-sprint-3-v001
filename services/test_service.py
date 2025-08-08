import os
import requests
import time
import argparse
import random
import numpy as np
from dotenv import load_dotenv

load_dotenv()
# Base URL of your FastAPI service
BASE_URL = f"http://localhost:{os.getenv('APP_PORT')}"


def generate_random_params():
    """Generate random model parameters matching the exact schema"""
    is_apartment = random.choice([True, False])
    studio = False if is_apartment else random.choice([True, False])
    
    # Ensure studio can't be true if rooms > 0
    rooms = random.randint(0, 4)  # 0 for studio
    if rooms > 0:
        studio = False
    
    total_area = random.uniform(20, 100)
    living_area = random.uniform(0.6, 0.9) * total_area
    kitchen_area = random.uniform(0.1, 0.3) * total_area
    
    # Generate coordinates in Moscow area
    latitude = random.uniform(55.573, 55.915)
    longitude = random.uniform(37.370, 37.857)
    
    return {
        "floor": random.randint(1, 25),
        "is_apartment": is_apartment,
        "kitchen_area": round(kitchen_area, 1),
        "living_area": round(living_area, 1),
        "rooms": rooms,
        "studio": studio,
        "total_area": round(total_area, 1),
        "building_id": random.randint(1000, 9999),
        "build_year": random.randint(1950, 2023),
        "building_type_int": random.randint(1, 5),
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "ceiling_height": round(random.uniform(2.4, 3.2), 2),
        "flats_count": random.randint(10, 200),
        "floors_total": random.randint(5, 25),
        "has_elevator": random.choice([True, False])
    }

def send_request(user_id):
    """Send a single prediction request to the API"""
    url = f"{BASE_URL}/api/price/"
    params = generate_random_params()
    
    query_params = {"user_id": user_id}

    try:
        start_time = time.time()
        response = requests.post(url, params=query_params, json=params)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"Success - User: {user_id}, Duration: {duration:.3f}s")
            return duration, True
        else:
            print(f"Error - User: {user_id}, Status: {response.status_code}, Response: {response.text}")
            return duration, False
    except Exception as e:
        print(f"Exception - User: {user_id}, Error: {str(e)}")
        return 0, False

def run_test(num_requests, interval):
    """Run the load test with specified number of requests and interval"""
    durations = []
    successes = 0
    
    print(f"Starting test with {num_requests} requests at {interval} second intervals...")
    
    for i in range(1, num_requests + 1):
        user_id = f"{i}"
        
        # Send request and collect metrics
        duration, success = send_request(user_id)
        durations.append(duration)
        if success:
            successes += 1
        
        # Wait for the specified interval, except after the last request
        if i < num_requests:
            time.sleep(interval)
    
    # Calculate and print summary statistics
    if durations:
        print("\nTest Summary:")
        print(f"Total Requests: {num_requests}")
        print(f"Successful Requests: {successes} ({successes/num_requests*100:.1f}%)")
        print(f"Average Duration: {np.mean(durations):.3f}s")
        print(f"Min Duration: {np.min(durations):.3f}s")
        print(f"Max Duration: {np.max(durations):.3f}s")
        print(f"Median Duration: {np.median(durations):.3f}s")
        print(f"95th Percentile: {np.percentile(durations, 95):.3f}s")

def main():
    parser = argparse.ArgumentParser(description="Load test for price prediction API")
    parser.add_argument("-n", "--num_requests", type=int, default=10, 
                        help="Number of requests to send (default: 10)")
    parser.add_argument("-i", "--interval", type=float, default=1.0, 
                        help="Time interval between requests in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    run_test(args.num_requests, args.interval)

if __name__ == "__main__":
    main()
