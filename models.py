from dataclasses import dataclass
from typing import Optional

@dataclass
class Book:
    isbn: str
    title: str
    author: str
    copiesTotal: int
    copiesAvailable: int

@dataclass
class Member:
    MemberID: int
    name: str
    passwordHash: str
    email: str
    joinDate: str  

@dataclass
class Loan:
    LoanID: int
    MemberID: int
    ISBN: str
    IssueDate: str  
    DueDate: str   
    ReturnDate: Optional[str] = None  