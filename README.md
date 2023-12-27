# roborace-portal

API for Roborace

## How to use (API)

```bash

curl http://127.0.0.1:8000/api/newCompetition -d '{"competition_name":"test", "competition_date":"2023-11-05", "authorization":"hidden", "track_length": "string"}'

```

## How to install (API and WebUI)
- Install `python3-dotenv` and dependencies
    
```bash

pip3 install -r requirements.txt

```

## How to start (API)

```bash

python3 main.py

```

## How to start (WebUI)

```bash

./run.sh

```
