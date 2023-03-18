from flask import Flask, jsonify, request, render_template
import sqlite3
conn = sqlite3.connect("bstest.db")
import random
from flask_cors import CORS

app = Flask(__name__)

@app.route("/api/check_out_bag", methods=["GET","POST"])
def check_out_bag():
    if request.method == "POST":
        response = request.get_data(as_text=True)
        print(response)
        return ("true")



if __name__ == "__main__":
    app.run(debug=True)


db_name = "bstest.db"

def db_execute(str):
    conn = sqlite3.connect(db_name)
    conn.execute(str)
    conn.commit()
    conn.close()

def id_exists(id):
    conn = sqlite3.connect(db_name)
    ids = conn.execute("SELECT ID FROM BAGS")
    exists = False
    for row in ids:
        if row[0] == id:
            exists = True
            break
    conn.close()
    if exists:
        print ("id exists")
    return exists

def generate_id(type):
    if type == "BAGS":
        len = 6
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
    thing = conn.execute (f"SELECT {check_for} FROM {db} WHERE {check_with} = {check_with_val}")
    cnt = 0
    for row in thing:
        if cnt > 0:
            print ("WARNING: MORE THAN ONE RESULT IN DB FOR SPECIFIED PARAMETERS")
            break
        return_val = row[0]
        cnt += 1
    conn.close()
    return return_val


#type 0 is for shopping bag, integer for other types
class Bag:
    def __init__(self, id = None, new_bag = False, type = None, location = 0):
        if id != None:
            assert len(str(id)) == 6
            self.id = id
        elif id == None and new_bag == True:
            self.id = generate_id("BAGS")
        else: 
            print("ERROR: ID IS NONE, IF CREATING BAG PLEASE CREATE 6 DIGIT ID")       
        if new_bag:
            self.status = 0
            self.account = 0
            self.uses = 0
            self.days_out = 0
            self.current_location = location
            self.type = type
            if id_exists(self.id):
                print("ID is duplicate! Pick a new 6 digit bag ID")
            else:
                db_execute(f"INSERT INTO BAGS VALUES \
                    ({self.id}, {self.status}, {self.account}, {self.uses}, {self.days_out}, {self.current_location}, {self.type})")
                print (f"New bag created with id {self.id} and type {self.type}")

        elif id_exists(id):
            #status will be an integer 0 , 1, 2, 3
            # 0 = free, 1 = in use, 2 = returned (needs cleaning), 3 being cleaned
            self.status = check_in_db("BAGS", "ID", self.id, "status")
            print (f"bag is status {self.status}")
            if self.status == 1:
                self.account = check_in_db("BAGS","ID", self.id, "account")
            self.uses = check_in_db("BAGS","ID", self.id, "uses")
            self.days_out = check_in_db("BAGS","ID", self.id, "days_out")
            self.current_location = check_in_db("BAGS","ID", self.id, "current_location")
            self.type = check_in_db ("BAGS","ID", self.id, "type")
        
        else: 
            print("ID does not exist and you are not trying to create a new Bag!")

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

def account_info_valid(account):
    return_val = True
    try:
        assert len(str(account.id)) == 8
        assert account.acc_type in [0, 1, 2]
        assert account.status in [0, 1]
        assert account.payment_method != None
        assert is_credit_card_valid(account.payment_method)
        assert len(str(account.contact_info)) == 10
        assert type(account.contact_info) == "int"
    except(AssertionError):
        print (AssertionError)
        return_val = False
    return return_val

class Account:
    # acc type 0, 1, 2, 0 = customer 1 = store 2 = admin
    #method of contact
    def __init__(self, id = None, is_making_account = False, acc_type = 0, status = 0, 
        payment_method = None, contact_info = None):
        if id != None:
            assert len(str(id)) == 8
            self.id = id
        elif id == None and is_making_account:
            self.id = generate_id("ACCOUNTS")
        else: 
            print("ERROR: ID IS NONE, IF CREATING ACCOUNT PLEASE CREATE 8 DIGIT ID")     
        if is_making_account:
            if not account_info_valid (id, acc_type, status, payment_method, contact_info):
                print ("ACCOUNT INFO INVALID, CANNOT CREATE ACCOUNT")
            else:
                self.status = status
                self.acc_type = acc_type
                self.payment_method = payment_method
                self.contact_info = contact_info
                self.bags = ""
                self.bags_list = []
                db_execute(f"INSERT INTO ACCOUNTS VALUES \
                        ({self.id}, {self.acc_type}, {self.status}, {self.payment_method}, \
                                {self.contact_info}, {self.bags})")
                print (f"New account created with id {self.id} and type {self.acc_type}")
        else:
            print (f"Collecting info for Account {self.id} from DB")
            self.status = check_in_db("ACCOUNTS", "ID", self.id, "status")
            self.acc_type = check_in_db("ACCOUNTS","ID", self.id, "acc_type")
            self.payment_method = check_in_db("ACCOUNTS","ID", self.id, "payment_method")
            self.contact_info = check_in_db("ACCOUNTS","ID", self.id, "contact_info")
            self.bags = check_in_db("ACCOUNTS","ID", self.id, "bags")
            bags_held = list(self.bags.split(" "))
            for bag in bags_held:
                int(bag)
            self.bags_list = bags_held

        def get_payment_method(self):
            self.payment_method = check_in_db("ACCOUNTS","ID", self.id, "payment_method")
            return self.payment_method

        def get_contact_info(self):
            self.contact_info = check_in_db("ACCOUNTS","ID", self.id, "contact_info")
            return self.contact_info

        def get_bags_held(self):
            self.bags = check_in_db("ACCOUNTS","ID", self.id, "bags")
            bags_held = list(self.bags.split(" "))
            for bag in bags_held:
                int(bag)
            self.bags_list = bags_held
            return self.bags_list
        
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
    account.bags = " ".join(str(e) for e in account.bags_list)
    conn.execute(f"Update ACCOUNTS set bags = {account.bags} WHERE ID = {account.id}")
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

def create_new_account():
    payment_method = None
    while payment_method == None:
        #prompt user for payment method
        if is_credit_card_valid(payment_method):
            break
    new_acc = Account(None, True, 0, 0, payment_method, contact_info)
    if account_info_valid(new_acc):
        write_acc_to_db(new_acc)


def acc_type_0_run():
    raise NotImplementedError

def acc_type_1_run():
    raise NotImplementedError

def location_bag_share_run(location_id):
    prices_dict = {"0": 0.12}
    #below for testing purposes
    #end testing purposes
    print("Welcome to Bag Share!")



