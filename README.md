# 70p.ramenclub

## Requirements

- docker
- awscli
- aws-sam-cli
- direnv

## Environments

- `TWITTER_CONSUMER_KEY`
- `TWITTER_CONSUMER_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `KML_URL`
- `S3_BUCKET`

## Setup

```
cp .envrc.sample .envrc
$EDITOR .envrc
direnv allow
cp env-vars.json.sample env-vars.json
$EDITOR env-vars.json
```

## Build

```
./script/build
```

## Invoke (Locally)

```
./script/invoke
```

## Deploy

```
./script/deploy
```

## Authentication

```
cd utils
pip install -r requirements.txt
python ./auth.py
```
