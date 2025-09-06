## LIBRARY_MANAGEMENT_PROJECT ##
#this is simple program to manage books and loans.


import csv
import datetime
from datetime import timedelta
import bcrypt
import argparse
from models import Book, Member, Loan
from dataclasses import asdict

#this is our list as for database
books =[]      #this will store books information.
Members = []   #this will store members information.
loans = []     #this will store loan transaction information.

# Session for logged-in user
session = {}

# Data directory
data_dir = None

#1. CSV FILE OPERATIONS
def load_csv():
    global books, Members, loans

    try:
        with open(data_dir + 'books.csv', 'r') as file:
            reader = csv.DictReader(file)
            books = []
            for row in reader:
                book = Book(
                    isbn=row['isbn'],
                    title=row['title'],
                    author=row['author'],
                    copiesTotal=int(row['copiesTotal']),
                    copiesAvailable=int(row['copiesAvailable'])
                )
                books.append(book)
    except FileNotFoundError:
        print("books.csv not found")

    try:
        with open(data_dir + 'members.csv','r') as file:
            reader = csv.DictReader(file)
            Members = []
            for row in reader:
                member = Member(
                    MemberID=int(row['MemberID']),
                    name=row['name'],
                    passwordHash=row['passwordHash'],
                    email=row['email'],
                    joinDate=row['joinDate']
                )
                Members.append(member)
    except FileNotFoundError:
        print("members.csv not found")

    try:
        with open(data_dir + 'loans.csv', 'r') as file:
            reader = csv.DictReader(file)
            loans = []
            for row in reader:
                loan = Loan(
                    LoanID=int(row['LoanID']),
                    MemberID=int(row['MemberID']),
                    ISBN=row['ISBN'],
                    IssueDate=row['IssueDate'],
                    DueDate=row['DueDate'],
                    ReturnDate=row['ReturnDate'] if row['ReturnDate'] else None
                )
                loans.append(loan)
    except FileNotFoundError:
        print("loans.csv not found")

#this function save data to csv files.
def save_to_CSV(filename, data, fieldnames):
    with open(filename,'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        data_dicts = [asdict(item) for item in data]
        writer.writerows(data_dicts)
        
#this is my function to save csv files.
def save_all_data():
    save_to_CSV(data_dir + 'books.csv',books,['isbn','title','author','copiesTotal','copiesAvailable'])
    save_to_CSV(data_dir + 'members.csv',Members,['MemberID','name','passwordHash','email','joinDate'])
    save_to_CSV(data_dir + 'loans.csv', loans, ['LoanID', 'MemberID', 'ISBN', 'IssueDate', 'DueDate', 'ReturnDate'])

# Authentication functions
def register_member():
    print("\n---- Register New Member ----")
    name = input("Please Enter your name: ").strip()
    email = input("Please Enter your email: ").strip()
    password = input("Please Enter your password: ").strip()

    if not name or not email or not password:
        print("All fields are required.")
        return

    if any(member.email == email for member in Members):
        print("Email already registered.")
        return

    # Generate member_id starting from 1001
    if Members:
        max_existing_id = max(m.MemberID for m in Members)
        member_id = max(max_existing_id + 1, 1001)
    else:
        member_id = 1001

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    join_date = datetime.date.today().isoformat()

    new_member = Member(
        MemberID=member_id,
        name=name,
        passwordHash=hashed,
        email=email,
        joinDate=join_date
    )

    Members.append(new_member)
    save_all_data()
    print(f"Member {name} registered successfully with ID {member_id}.")

def login():
    print("\n---- Login ----")
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    if email == 'librarian@library.com' and password == 'admin':
        session['user'] = {'role': 'librarian', 'email': email}
        return 'librarian'

    for member in Members:
        if member.email == email:
            if bcrypt.checkpw(password.encode('utf-8'), member.passwordHash.encode('utf-8')):
                session['user'] = {'role': 'member', 'member_id': member.MemberID, 'name': member.name}
                return 'member'
            else:
                print("Invalid password.")
                return None

    print("User not found.")
    return None
    

#this is our function to add a book.
def add_book():
    print("\n---- Add a new book----")
    isbn = input(" Enter the book's ISBN: ")
    title = input(" Enter the book title: ")
    author = input(" Enter the book's author: ")
    try:
        copies = int(input(" Enter total copies: "))
    except ValueError:
        print("Invalid number for copies.")
        return

    if not isbn or not title or not author or copies <= 0:
        print("Invalid input. Please provide all details correctly.")
        return

    if any(book.isbn == isbn for book in books):
        print("Book with this ISBN already exists.")
        return

    new_book = Book(
        isbn=isbn,
        title=title,
        author=author,
        copiesTotal=copies,
        copiesAvailable=copies
    )

    books.append(new_book)
    save_all_data()
    print(f"Successfully! Added '{title}' to the library.")

#function to show all books
def show_books():
    print("\n--- All books in the library ---")

    if len(books) == 0:
        print("The library has no books yet.")
        return

    for i, book in enumerate(books):
        status = "Available" if book.copiesAvailable > 0 else "Borrowed"
        print(f"{i+1}. '{book.title}' by {book.author} - {status}")

# Librarian menu
def librarian_menu():
    while True:
        print("\n" + "="*40)
        print("====LIBRARIAN DASHBOARD=====")
        print("="*40)
        print("1. Add Book")
        print("2. Remove Book")
        print("3. Register a new Member")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. View Overdue List")
        print("7. Logout")
        print("="*40)

        choice = input("Choose option: ").strip()
        if choice == "1":
            add_book()
        elif choice == "2":
            remove_book()
        elif choice == "3":
            register_member()
        elif choice == "4":
            issue_book()
        elif choice == "5":
            return_book()
        elif choice == "6":
            view_overdue()
        elif choice == "7":
            session.clear()
            break
        else:
            print("Invalid choice.")

# Member menu
def member_menu():
    while True:
        print("\n" + "="*40)
        print("=====MEMBER DASHBOARD=====")
        print("="*40)
        print("1. Search Catalogue")
        print("2. Borrow Book")
        print("3. My Loans")
        print("4. Logout")
        print("="*40)

        choice = input("Choose option: ").strip()
        if choice == "1":
            search_catalogue()
        elif choice == "2":
            borrow_book()
        elif choice == "3":
            my_loans()
        elif choice == "4":
            session.clear()
            break
        else:
            print("Invalid choice.")

# Librarian functions
def remove_book():
    print("\n---- Remove Book ----")
    isbn = input("Enter ISBN to remove: ").strip()
    for book in books:
        if book.isbn == isbn:
            books.remove(book)
            save_all_data()
            print(f"Book '{book.title}' removed.")
            return
    print("Book not found.")

def issue_book():
    print("\n---- Issue Book ----")
    isbn = input("Enter ISBN: ").strip()
    member_id = input("Enter Member ID: ").strip()
    try:
        member_id = int(member_id)
    except ValueError:
        print("Invalid Member ID.")
        return

    book = next((b for b in books if b.isbn == isbn), None)
    if not book:
        print("Book not found.")
        return
    if book.copiesAvailable <= 0:
        print("Book not available.")
        return
    member = next((m for m in Members if m.MemberID == member_id), None)
    if not member:
        print("Member not found.")
        return

    # Generate loan_id
    loan_id = max([l.LoanID for l in loans] + [0]) + 1
    issue_date = datetime.date.today().isoformat()
    due_date = (datetime.date.today() + timedelta(days=14)).isoformat()

    loan = Loan(
        LoanID=loan_id,
        MemberID=member_id,
        ISBN=isbn,
        IssueDate=issue_date,
        DueDate=due_date,
        ReturnDate=None
    )
    loans.append(loan)
    book.copiesAvailable -= 1
    save_all_data()
    print(f"Book issued. Due on {due_date}.")

def return_book():
    print("\n---- Return Book ----")
    loan_id = input("Enter Loan ID: ").strip()
    try:
        loan_id = int(loan_id)
    except ValueError:
        print("Invalid Loan ID.")
        return

    loan = next((l for l in loans if l.LoanID == loan_id), None)
    if not loan:
        print("Loan not found.")
        return
    if loan.ReturnDate:
        print("Book already returned.")
        return

    loan.ReturnDate = datetime.date.today().isoformat()
    book = next((b for b in books if b.isbn == loan.ISBN), None)
    if book:
        book.copiesAvailable += 1
    save_all_data()
    print("Book returned.")

def view_overdue():
    print("\n---- Overdue Loans ----")
    today = datetime.date.today().isoformat()
    overdue = [l for l in loans if not l.ReturnDate and l.DueDate < today]
    if not overdue:
        print("No overdue loans.")
        return
    for l in overdue:
        member = next((m for m in Members if m.MemberID == l.MemberID), None)
        book = next((b for b in books if b.isbn == l.ISBN), None)
        print(f"Loan ID: {l.LoanID}, Member: {member.name if member else 'Unknown'}, Book: {book.title if book else 'Unknown'}, Due: {l.DueDate}")

# Member functions
def search_catalogue():
    print("\n---- Search Catalogue ----")
    keyword = input("Enter keyword (title or author): ").strip().lower()
    results = [b for b in books if keyword in b.title.lower() or keyword in b.author.lower()]
    if not results:
        print("No books found.")
        return
    for b in results:
        status = "Available" if b.copiesAvailable > 0 else "Borrowed"
        print(f"'{b.title}' by {b.author} - {status}")

def borrow_book():
    if 'user' not in session or session['user']['role'] != 'member':
        print("Not logged in as member.")
        return
    member_id = session['user']['member_id']
    print("\n---- Borrow Book ----")
    isbn = input("Enter ISBN: ").strip()
    book = next((b for b in books if b.isbn == isbn), None)
    if not book:
        print("Book not found.")
        return
    if book.copiesAvailable <= 0:
        print("Book not available.")
        return

    # Generate loan_id
    loan_id = max([l.LoanID for l in loans] + [0]) + 1
    issue_date = datetime.date.today().isoformat()
    due_date = (datetime.date.today() + timedelta(days=14)).isoformat()

    loan = Loan(
        LoanID=loan_id,
        MemberID=member_id,
        ISBN=isbn,
        IssueDate=issue_date,
        DueDate=due_date,
        ReturnDate=None
    )
    loans.append(loan)
    book.copiesAvailable -= 1
    save_all_data()
    print(f"Book borrowed. Due on {due_date}.")

def my_loans():
    if 'user' not in session or session['user']['role'] != 'member':
        print("Not logged in as member.")
        return
    member_id = session['user']['member_id']
    print("\n---- My Loans ----")
    my_loans_list = [l for l in loans if l.MemberID == member_id]
    if not my_loans_list:
        print("No loans.")
        return
    for l in my_loans_list:
        book = next((b for b in books if b.isbn == l.ISBN), None)
        status = "Returned" if l.ReturnDate else "Active"
        print(f"Loan ID: {l.LoanID}, Book: {book.title if book else 'Unknown'}, Issue: {l.IssueDate}, Due: {l.DueDate}, Status: {status}")


def main_menu():
    load_csv()
    while True:
        print("\n" + "="*40)
        print("LIBRARY MANAGEMENT PROJECT")
        print("="*40)
        print("1. Login")
        print("2. self Registration for new Member")
        print("3. Exit")
        print("="*40)

        choice = input("Please choose option from 1-3: ").strip()
        if choice == "1":
            role = login()
            if role == 'librarian':
                librarian_menu()
            elif role == 'member':
                member_menu()
        elif choice == "2":
            register_member()
        elif choice == "3":
            print("THANK YOU! for using Library management system. Goodbye")
            break
        else:
            print("Invalid choice, Please enter 1, 2 or 3")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='data/')
    args = parser.parse_args()
    data_dir = args.data_dir
    main_menu()
