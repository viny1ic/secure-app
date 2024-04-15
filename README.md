# Secure-App
This app uses the Oauth framework to perform Device Authorization Flow using Auth0. <br>
This app uses AES-256-GCM encryption along with PBKDF for key generation. <br>
This app works on a server-client model with the server running on Flask, hosted on a Raspberry Pi Zero w 2. <br>
The server is connected to the internet using Cloudflare DDNS service for hosting over DHCP IP addresses.

## How To Run
Download the file `client/client.py`, and run it using `python3 client.py`<br>
Select the action for the option you wish to perform.

## Sample Files
Sample files are provided in the `sample` folder.<br>

## How to run server
Log into Auth0 and setup account and oauth app using device authorization flow. <br>
```bash
# clone the github repository
git clone https://github.com/viny1ic/secure-app
cd secure-app

# Create virtual environment
pip install virtualenv
python -m venv venv
source env/bin/activate

# Install required packages
pip install pycryptodome flask flask-restful 'python-jose[cryptography]' python-dotenv authlib
```
<br>Save required credentials into the .env file acquired from the auth0 Dashboard<br>
```bash
sudo cp server/secureapp.service
```
