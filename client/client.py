import requests
import json
import getpass

def menu():
        """
        Takes input from user
        """
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
    """
    Does stuff.
    """
    req = auth_token
    """
    Makes the appropriate request based on the input provided by the user. Asks the user for the appropriate input as required, and display the response of the request.
    """
    req["Filename"] = str(input("Please enter the name of the file you wish to access/create: "))
    req["Password"] = str(getpass.getpass("please input the password associated with that file: "))
    if choice == 1:
        res = requests.post("https://vinylic.me/getcipher", json= req)
    elif choice == 2:
        res = requests.post("https://vinylic.me/getplain", json= req)
    elif choice == 3:
        req["Message"] = str(input("Please enter the text you wish to encrypt and store: "))
        res = requests.post("https://vinylic.me/setplain", json= req)
    else:
        print("Mild Inconvenience, Killing myselg")
        exit()
    if res.status_code != 200:
        print("Failed. If the auth token is expired, please remove it ('token' file)")
    print(res.content.decode("utf-8"))



"""
Driver Code
"""
try:
    """
    Checks if token is stored locally
    """
    token = open("token", "r")
    raw_token = token.read()
    auth_token = json.loads(raw_token)
    print("Authentication succesful!")
    menu()
except Exception as e:
    print("Please log in to the service")
    """
    Asks the user to sign in through the Auth0 interface, and stores the recieved access token
    """
    url = requests.get("https://vinylic.me/login")
    print("Please follow this URL to complete authentication: " + url.content.decode("utf-8"))
    token_temp =requests.get("https://vinylic.me/token")
    auth_token = token_temp.content.decode("utf-8")
    token = open("token", "w+")
    token.write(auth_token)
    if token_temp.status_code == 200:
        print("Authentication succesful!")
        print("Please run the program again")

