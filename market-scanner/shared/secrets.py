def read_secret(name):
    """
    Reads a docker swarm secret mounted at /run/secrets/{name}.
    Returns None if not found.
    """
    path = f"/run/secrets/{name}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Secret {name} not found at {path}")
        return None
