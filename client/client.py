import requests
import json
import getpass

def menu():
        print("What would you like to do today?")
        print("Enter 1 to retrieve encrypted ciphertext")
        print("Enter 2 to retrieve decrypted plaintext")
        print("Enter 3 to encrypt and store plaintext")
        try:
            choice = int(input("Please enter your choice: "))
        except:
            print("Unrecognized Input")
            menu()            
        if choice not in (1,2,3):
            print("Unrecognized Input")
            menu()
        do_stuff(choice)

def do_stuff(choice):
    print(choice)
    req = auth_token
    req["Filename"] = str(input("Please enter the name of the file you wish to access/create: "))
    req["Password"] = str(getpass.getpass("please input the password associated with that file: "))
    if choice == 1:
        res = requests.post("http://10.0.0.27:5000/getcipher", json= req)
    elif choice == 2:
        res = requests.post("http://10.0.0.27:5000/getplain", json= req)
    elif choice == 3:
        req["Message"] = str(input("Please enter the text you wish to encrypt and store: "))
        res = requests.post("http://10.0.0.27:5000/setplain", json= req)
    else:
        print("Mild Inconvenience, Killing myselg")
        exit()
    print(res.content.decode("utf-8"))

try:
    token = open("token", "r")
    raw_token = token.read()
    print(raw_token)
    auth_token = json.loads(raw_token)
    print("Authentication succesful!")
    menu()
except Exception as e:
    print(e)
    url = requests.get("http://10.0.0.27:5000/login")
    print("Please follow this URL to complete authentication: " + url.content.decode("utf-8"))
    auth_token =requests.get("http://10.0.0.27:5000/token").content.decode("utf-8")
    token = open("token", "w")
    token.write(auth_token.json())
    if auth_token.status_code == 200:
        print("Authentication succesful!")
        menu()

