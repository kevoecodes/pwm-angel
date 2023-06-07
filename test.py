import uuid

def generate_unique_id():
    unique_id = str(uuid.uuid4().int)[0:7]
    return unique_id

# Example usage
id = generate_unique_id()
print(f'9{id}')
