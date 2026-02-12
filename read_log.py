
try:
    with open('verification_result.log', 'r', encoding='utf-8') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading log: {e}")
