# eShopCo configuration API

Run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_WORKERS=7 APP_API_KEY=key-ylh10iv4cw uvicorn main:app --reload
```

Test:

```text
http://127.0.0.1:8000/effective-config?set=port=9000&set=debug=true
```
