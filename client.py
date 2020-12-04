import requests


url = input("Snowflake server URL: ")

while True:
    result = requests.post(url)
    result.raise_for_status()
    result = result.json()
    print(f"Snowflake: {result['snowflake']}")
    input("Press enter to continue: ")
