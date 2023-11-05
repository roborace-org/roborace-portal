# roborace-portal

API for Roborace

## How to use

```bash

curl http://127.0.0.1:8000/api/newCompetition -d '{"competition_name":"test", "competition_date":"2023-11-05", "authorization":"hidden"}'

```

## How to install

```bash

pip3 install -r requirements.txt

```

## How to start
- Install `python3-dotenv`
- Write to .env folder
    ```bash

        mysql_server
        mysql_login=
        mysql_pass=

    ```

```bash

python3 main.py

```
