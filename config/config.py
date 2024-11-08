import yaml

with open("config/config.yaml", "r", encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

DB_HOST = config['credentials']['DB_HOST']
DB_USER = config['credentials']['DB_USER']
DB_PASSWORD = config['credentials']['DB_PASSWORD']
DB_NAME = config['credentials']['DB_NAME']
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
