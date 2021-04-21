import yaml

__all__ = (
    'config',
)

with open('config.yaml') as f:
    config = yaml.safe_load(f)
