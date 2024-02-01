# maps-pd-web

## Requirements to get started

- [dotenv-cli](https://www.npmjs.com/package/dotenv-cli)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [GNU make](https://community.chocolatey.org/packages/make)
- [Python 3](https://www.python.org/downloads)

## Getting started

### Clone the repo

```bash
git clone git@gitlab.com:moss-earth/backend/maps-pd-web.git
```

### Access the project directory

```bash
cd maps-pd-web
```

### Create a service account called credential.json

Obtain a service account with the correct permissions from [GCP](https://console.cloud.google.com/welcome) and save it as `credential.json`. If you are unsure how to do this, consult a colleague who is currently working on or has previously worked on this project to provide you with the file.

### Copy the .env.example file

```bash
cp .env.example .env
```

### Configure the .env file

Properly set each environment variable in the `.env` file.
If you don't know which values to use, talk to a colleague who is currently working on or has previously worked on this project.

### Install the dependencies

```bash
make install
```

### Run the project

```bash
make dev
```
