from flask import Flask, jsonify, request, render_template
import sqlite3
conn = sqlite3.connect("bstest.db")
import random
from flask_cors import CORS
db_name = "bstest.db"
from twilio.rest import Client
from datetime import datetime
account_sid = 'ACa08340b8e4bdefc5b9e6f69b7339860c'
auth_token = '848f573a09fd474867d647dfe4c1721c'
from_number = '+15077057720'
bag_price = 2
service_fee = 0.05


def db_execute(str):
    conn = sqlite3.connect(db_name)
    conn.execute(str)
    conn.commit()
    conn.close()

def generate_id(type):
    if type == "BAGS":
        len = 8
    elif type == "ACCOUNTS":
        len = 8
    else:
        print ("ID cannot be generated! Type invalid.")
    min = pow(10, len-1)
    max = pow(10, len) - 1
    # Generate random number
    found = False
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    while not found:
        potential_id = random.randint(min, max)
        cursor.execute (f"SELECT status FROM {type} WHERE ID = {potential_id}")
        result = cursor.fetchone()
        if result != None:
            print ("ID already in database! Retrying...")
        else:
           found = True
    conn.close()
    print(f"Generated random new id of {potential_id}")
    return potential_id


def check_in_db(db, check_with, check_with_val, check_for):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {check_for} FROM {db} WHERE {check_with} = {check_with_val}")
    result = cursor.fetchone()
    if result == None:
        return None
    if cursor.fetchone() == None:
        status = result[0]
    else:
        print ("MORE THAN ONE ID ERROR")
        return None
    conn.close()
    return status


#type 0 is for shopping bag, integer for other types
class Bag:
    def __init__(self, id = None, new_bag = False, type = None, location = 0):
        if id != None:
            assert len(str(id)) == 8
            self.id = id
        elif id == None and new_bag == True:
            self.id = generate_id("BAGS")
        else: 
            print("ERROR: ID IS NONE, IF CREATING BAG PLEASE CREATE 8 DIGIT ID")       
        if new_bag:
            self.status = 0
            self.account = 0
            self.uses = 0
            self.days_out = 0
            self.current_location = location
            self.type = type
            db_execute(f"INSERT INTO BAGS VALUES \
                ({self.id}, {self.status}, {self.account}, {self.uses}, {self.days_out}, {self.current_location}, {self.type})")
            print (f"New bag created with id {self.id} and type {self.type}")

        else:
            #status will be an integer 0 , 1, 2, 3
            # 0 = free, 1 = in use, 2 = returned (needs cleaning), 3 being cleaned
            self.status = check_in_db("BAGS", "ID", self.id, "status")
            print (f"bag is status {self.status}")
            self.account = check_in_db("BAGS","ID", self.id, "account")
            self.uses = check_in_db("BAGS","ID", self.id, "uses")
            self.days_out = check_in_db("BAGS","ID", self.id, "days_out")
            self.current_location = check_in_db("BAGS","ID", self.id, "current_location")
            self.type = check_in_db ("BAGS","ID", self.id, "type")
    

    def taken_out(self, account_id):
        if self.status != 0:
            print ("Bag ID is not available to be taken out right now")
        else:
            self.status = 1
            self.account = account_id
            self.uses += 1
            self.days_out = 0
            self.current_location = 0
            print (f"Bag ID: {self.id} taken out by account {self.account}")
            write_bag_to_db(self)

    def is_needs_retirement(self):
        raise NotImplementedError

    def returned(self, location_id):
        if self.status != 1:
            print (f"Bag ID is status {self.status}, cannot be returned")
        else:
            print (f"Bag ID: {self.id} returned by account {self.account}")
            self.status = 2
            self.account = 0
            self.current_location = location_id
            self.days_out = 0
            write_bag_to_db(self)

    def cleaning(self):
        if self.status != 2:
            print (f"Bag ID is status {self.status}, cannot be cleaned")
        else: 
            print(f"Cleaning bag {self.id}....")
            self.status = 3
            write_bag_to_db(self)

    def done_cleaning(self):
        if self.status != 3:
            print (f"Bag ID is status {self.status}, is not being cleaned")
        else: 
            print(f"Done cleaning bag {self.id}")
            self.status = 0
            write_bag_to_db(self)
    
    def check_status(self):
        if self.status == 0:
            print (f"Bag ID {self.id} is free at location {self.current_location}")
        elif self.status == 1:
            print (f"Bag ID {self.id} is taken out by account {self.account}")
        elif self.status == 2:
            print (f"Bag ID {self.id} is returned to location {self.current_location} and needs to be cleaned")
        elif self.status == 3:
            print (f"Bag ID {self.id} is being cleaned at location {self.current_location}")
    
    def get_type(self):
        print (f"Called get_type on id {self.id}, returned type {self.type}")

def acc_id_exists(acc_id):
    conn = sqlite3.connect(db_name)
    ids = conn.execute("SELECT ID FROM ACCOUNTS")
    exists = False
    for row in ids:
        if row[0] == id:
            exists = True
            break
    conn.close()
    if exists:
        print ("Account ID exists")
    return exists

def check_bag_status (bag_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT status FROM BAGS WHERE ID = {bag_id}")
    result = cursor.fetchone()
    if result == None:
        return None
    if cursor.fetchone() == None:
        status = int(result[0])
    else:
        print ("MORE THAN ONE ID ERROR")
        return None
    conn.close()
    return status

def get_id_from_phone (phone):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT ID FROM ACCOUNTS WHERE contact_info = {phone}")
    result = cursor.fetchone()
    if result == None:
        return None
    if cursor.fetchone() == None:
        id = result[0]
    else:
        print ("MORE THAN ONE ID ERROR")
        return None
    conn.close()
    return id

class Account:
    # acc type 0, 1, 2, 0 = customer 1 = store 2 = admin
    #method of contact
    def __init__(self, id = None, is_making_account = False, acc_type = 0, status = 0, 
        payment_method = None, contact_info = None, pin = None):
        if id != None:
            self.id = id
        elif id == None and is_making_account:
            self.id = generate_id("ACCOUNTS")
        else: 
            print("ERROR: ID IS NONE, IF CREATING ACCOUNT PLEASE CREATE 8 DIGIT ID")     
        if is_making_account:
            self.status = status
            self.acc_type = acc_type
            self.payment_method = payment_method
            self.contact_info = contact_info
            self.bags = 0
            self.pin = pin
            db_execute(f"INSERT INTO ACCOUNTS VALUES \
                    ({self.id}, {self.acc_type}, {self.status}, {self.payment_method}, \
                            {self.contact_info}, {self.bags}, {self.pin})")
            print (f"New account created with id {self.id} and type {self.acc_type}")
        else:
            print (f"Collecting info for Account {self.id} from DB")
            self.status = check_in_db("ACCOUNTS", "ID", self.id, "status")
            self.acc_type = check_in_db("ACCOUNTS","ID", self.id, "acc_type")
            self.payment_method = check_in_db("ACCOUNTS","ID", self.id, "payment_method")
            self.contact_info = check_in_db("ACCOUNTS","ID", self.id, "contact_info")
            self.bags = check_in_db("ACCOUNTS","ID", self.id, "bags")
            self.pin = check_in_db("ACCOUNTS","ID", self.id, "pin")

    def get_payment_method(self):
        self.payment_method = check_in_db("ACCOUNTS","ID", self.id, "payment_method")
        return self.payment_method

    def get_contact_info(self):
        self.contact_info = check_in_db("ACCOUNTS","ID", self.id, "contact_info")
        return self.contact_info

    def get_bags_held(self):
        self.bags = check_in_db("ACCOUNTS","ID", self.id, "bags")
        bags_list = []
        k = int(len(str(self.bags))/8)
        temp = self.bags
        for i in range (k):
            temp_bag = 0
            temp_bag = int(temp % 10**8)
            temp -= temp_bag
            temp /= 10**8
            bags_list.append(temp_bag)
        return bags_list
            
    def add_bag(self, new_bag):
        bags = check_in_db("ACCOUNTS","ID", self.id, "bags")
        self.bags = bags *(10**8) + new_bag
        write_acc_to_db(self)
        


    def check_status(self):
        self.status = check_in_db("ACCOUNTS", "ID", self.id, "status")

        

            
def write_bag_to_db (bag):
    # write an object of bag class to the database
    print(f"Writing {bag.id} info to DB")
    conn = sqlite3.connect(db_name)
    conn.execute(f"Update BAGS set status = {bag.status} WHERE ID = {bag.id}")
    conn.commit()
    conn.execute(f"Update BAGS set account = {bag.account} WHERE ID = {bag.id}")
    conn.commit()
    conn.execute(f"Update BAGS set uses = {bag.uses} WHERE ID = {bag.id}")
    conn.commit()
    conn.execute(f"Update BAGS set days_out = {bag.days_out} WHERE ID = {bag.id}")
    conn.commit()
    conn.execute(f"Update BAGS set current_location = {bag.current_location} WHERE ID = {bag.id}")
    conn.commit()
    conn.execute(f"Update BAGS set type = {bag.type} WHERE ID = {bag.id}")
    conn.commit()
    print("Bag info written/updated to DB")
    conn.close()

def write_acc_to_db (account):
    #write an object of account class to the database
    print(f"Writing {account.id} info to DB")
    conn = sqlite3.connect(db_name)
    conn.execute(f"Update ACCOUNTS set status = {account.status} WHERE ID = {account.id}")
    conn.commit()
    conn.execute(f"Update ACCOUNTS set acc_type = {account.acc_type} WHERE ID = {account.id}")
    conn.commit()
    conn.execute(f"Update ACCOUNTS set payment_method = {account.payment_method} WHERE ID = {account.id}")
    conn.commit()
    conn.execute(f"Update ACCOUNTS set contact_info = {account.contact_info} WHERE ID = {account.id}")
    conn.commit()
    conn.execute(f"Update ACCOUNTS set bags = {account.bags} WHERE ID = {account.id}")
    conn.commit()
    conn.execute(f"Update ACCOUNTS set pin = {account.pin} WHERE ID = {account.id}")
    conn.commit()
    print("Account info written/updated to DB")
    conn.close()

def is_credit_card_valid(card_number):
    """
    Checks whether a credit card number is valid or not using the Luhn algorithm.
    Returns True if the card number is valid, False otherwise.
    """
    card_number = str(card_number) # convert the card number to a string
    # reverse the card number and convert each character to an integer
    digits = [int(x) for x in card_number[::-1]] 
    # double every second digit
    doubled_digits = []
    for i, digit in enumerate(digits):
        if i % 2 == 1:
            doubled_digit = digit * 2
            
            # if the result is a two-digit number, add the digits together
            if doubled_digit > 9:
                doubled_digit = doubled_digit - 9
                
            doubled_digits.append(doubled_digit)
        else:
            doubled_digits.append(digit)
    # sum all the digits
    total = sum(doubled_digits)
    # if the total is divisible by 10, the card number is valid
    return total % 10 == 0

def get_location_bag_status(location_id, bag_type):
    print (f"Check the status of all bags at given location {location_id}")
    conn = sqlite3.connect(db_name)
    thing = conn.execute (f"SELECT ID, status, type FROM BAGS WHERE current_location = {location_id}")
    bags_returned = []
    bags_available = []
    returned_cnt = 0
    available_cnt = 0
    for row in thing:
        if bag_type != row[2]:
            continue
        if row[1] == 2:
            bags_returned.append(row[0])
            returned_cnt += 1
        elif row[1] == 0:
            bags_available.append(row[0])
            available_cnt += 1
        else:
            print ("ERROR: get_location_bag_status failed because bag was not status 0 or 2")
    conn.close()
    status_dict = {"bags_returned": bags_returned, "bags_available": bags_available, 
    "returned_cnt": returned_cnt, "available_cnt": available_cnt}
    print (status_dict)
    return status_dict
    
def clean_all_bags(location_id, bag_type):
    bag_status_dict = get_location_bag_status(location_id, bag_type)
    returned_cnt = bag_status_dict["returned_cnt"]
    print (f"Available to clean: {returned_cnt}")
    for bag in bag_status_dict["bags_returned"]:
        bag_obj = Bag(bag, False, bag_type, location_id)
        bag_obj.cleaning()
    print ("Cleaning...")
    print (f"Done cleaning {returned_cnt} bags")
    for bag in bag_status_dict["bags_returned"]:
        bag_obj = Bag(bag, False, bag_type, location_id)
        bag_obj.done_cleaning()


def acc_type_0_run():
    raise NotImplementedError

def acc_type_1_run():
    raise NotImplementedError

def location_bag_share_run(location_id):
    prices_dict = {"0": 0.12}
    #below for testing purposes
    #end testing purposes
    print("Welcome to Bag Share!")



app = Flask(__name__)

@app.route("/api/check_out_bag", methods=["GET","POST"])
def check_out_bag():
    if request.method == "POST":
        response = request.get_data(as_text=True)
        idx_of_pn = response.find("phonenumber") + 14
        pn = int(response[idx_of_pn:(idx_of_pn+10)])
        idx_of_pin = response.find("password") + 11
        pin = int(response[idx_of_pin:(idx_of_pin+4)])
        idx_of_bag = response.find("bag") + 6
        bag = int(response[idx_of_bag:(idx_of_bag+8)])
        idx_of_status = response.find("first_time") + 12
        status_str = response[idx_of_status:idx_of_status+5]
        bag = Bag(bag, False, 0, 0)
        if bag.status != 0:
            return("bagnotavailable")
        if "true" in status_str:
            status = True
        elif "false" in status_str:
            status = False
        if status:
            credit_card_idx =  response.find("creditcardinfo") + 17
            credit_card = int(response [credit_card_idx:credit_card_idx+16])
            if get_id_from_phone(pn) != None:
                return("statusincorrect")
            account = Account(None, True, 0, 0, credit_card, pn, pin)
        else:
            if get_id_from_phone(pn) == None:
                return("statusincorrect")
            account = Account(get_id_from_phone(pn), False)
            if pin != account.pin:
                return("loginincorrect")
        
        bag.taken_out(get_id_from_phone(pn))
        account.add_bag(new_bag = bag.id)
        to_number = '+1'+str(pn)
        message = (f"from BagSHARE: \n\nThank you for using BagSHARE!  \n\nBag ID#{bag.id} TAKEN OUT from location #121 (BCG Toronto Office). \n\nIt is due for return in 14 DAYS. \n\nBags under your account: {account.get_bags_held()}")
        credit_last4 = int(str(account.payment_method)[-4:])
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y")
        message2 = (f"from BagSHARE: \n\nYour reciept from {date_time}: \n\nYou CHECKED OUT Bag ID#{bag.id} \n\nBilled to: \nCredit Card ending in {credit_last4} \n\nService Charge: ${service_fee} \nBag Deposit: ${bag_price} \n(You will recieve this back when you return the bag on time!) \n\nTOTAL: ${service_fee+bag_price} \n\nYou have earned 5 WALMART rewards points from this transaction!" )
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=message, from_=from_number, to=to_number)
        message = client.messages.create(body=message2, from_=from_number, to=to_number)
        write_acc_to_db
        write_bag_to_db

        print(pn)
        print(pin)
        print(bag)
        print(status)

        return ("true")

@app.route("/api/return_bag", methods=["GET","POST"])
def return_bag():
    if request.method == "POST":      
        response = request.get_data(as_text=True)
        print (response)
        idx_of_bag = response.find("bag") + 6
        bag_id = int(response[idx_of_bag:idx_of_bag+8])
        print(bag_id)
        if check_bag_status(bag_id) == None:
            return ("bagdoesntexist")
        elif check_bag_status(bag_id) != 1:
            return ("bagnotout")
        else:
            bag = Bag(bag_id, False)
            account_id = bag.account
            account = Account(account_id, False)
            bags_list = account.get_bags_held()
            bags_list.remove(bag_id)
            current_bags_int = 0
            num_bags = len(bags_list)
            for i in range (num_bags):
                current_bags_int *= (10**8)
                current_bags_int += bags_list[i]
            account.bags = current_bags_int
            bag.returned(location_id=121)
            write_acc_to_db(account)
            write_bag_to_db(bag)
            to_number = '+1'+str(account.contact_info)
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y")
            message = (f"from BagSHARE: \n\nThank you for using BagSHARE!  \n\nBag ID#{bag.id} RETURNED to location #121 (BCG Toronto Office). \n\nYou will now recieve your deposit as a refund. \n\nBags remaining under your account: {account.get_bags_held()}")
            credit_last4 = int(str(account.payment_method)[-4:])
            message2 = (f"from BagSHARE: \n\nYour reciept from {date_time}: \n\nYou RETURNED Bag ID#{bag.id} \n\nCredit to: \nCredit Card ending in {credit_last4} \nBag Deposit: ${bag_price} (Will be returned in full) \n\nTOTAL: -${bag_price} (REFUND) ")
            client = Client(account_sid, auth_token)
            message = client.messages.create(body=message, from_=from_number, to=to_number)
            message = client.messages.create(body=message2, from_=from_number, to=to_number)
            return("true")



if __name__ == "__main__":
    app.run(debug=True)


