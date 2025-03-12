import os

queries_path = os.path.join(os.path.dirname(__file__), 'sql/queries')

def query_text(name: str) -> str:
    with open(os.path.join(queries_path, f'{name}.sql')) as f:
        return f.read()