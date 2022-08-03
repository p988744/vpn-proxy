# VPN Proxy Server

This is a web service that can be used to create multiple squid service which use network via Surfshark VPN connection
in docker containers.

## requirements

- surfshark-vpn account
- docker
- python 3.9
- poetry

## Installation

- Install docker
- Install python 3.9
- Install poetry (recommended)
- Install dependencies via `poetry install`

## Configure

Recommend to use `dotenv` to set configuration instead of editing `settings.py`.
You can find some example in `.env.example`

## Usage

You can find API documentation in the root of service page. (i.e. `http://localhost:8080/`)

## Contributing

- Clone Project
- Run `poetry install` (or `pip install -r requirements.txt`)
- Create your Feature Branch (never use master)
- Set environment variables (see `.env.example`), you can find additional information in `settings.py`
- Do your work
- Commit your Changes
- Push to the Branch
- Open a Merge Request (Pull Request)