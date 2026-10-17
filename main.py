import os
from typing import List

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="eShopCo Config API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def as_bool(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def coerce(config: dict) -> dict:
    result = dict(config)
    result["port"] = int(result["port"])
    result["workers"] = int(result["workers"])
    result["debug"] = as_bool(result["debug"])
    result["log_level"] = str(result["log_level"])
    result["api_key"] = "****"
    return result


def load_effective_config(overrides: List[str]) -> dict:
    # Lowest to highest precedence: defaults, YAML, .env, OS environment, CLI.
    config = DEFAULTS.copy()

    environment = os.getenv("APP_ENV", "development")
    yaml_path = f"config.{environment}.yaml"
    if os.path.exists(yaml_path):
        with open(yaml_path, encoding="utf-8") as file:
            config.update(yaml.safe_load(file) or {})

    env_file = dotenv_values(".env")
    file_mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
        "NUM_WORKERS": "workers",
    }
    for source, target in file_mapping.items():
        if env_file.get(source) is not None:
            config[target] = env_file[source]

    os_mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }
    for source, target in os_mapping.items():
        if source in os.environ:
            config[target] = os.environ[source]

    for item in overrides:
        if "=" in item:
            key, value = item.split("=", 1)
            if key in DEFAULTS:
                config[key] = value

    return coerce(config)


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    return load_effective_config(set)
