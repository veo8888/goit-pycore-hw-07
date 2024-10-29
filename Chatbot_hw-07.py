from collections import UserDict
from datetime import datetime, timedelta

class Field:
    """Базовий клас для поля запису."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """Клас для зберігання імені контакту."""
    pass

class Phone(Field):
    """Клас для зберігання номера телефону."""
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:  #Перевірка, чи є номер телефону з 10 цифр.
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    """Клас для зберігання дати народження."""
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    """Клас для зберігання інформації про контакт."""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return f"Phone {phone} removed."
        return f"Phone {phone} not found."

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return f"Phone {old_phone} updated to {new_phone}."
        return f"Phone {old_phone} not found."

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return "Birthday not set."
        today = datetime.today()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = '; '.join(phone.value for phone in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    """Клас для управління адресною книгою."""
    def add_record(self, record):  #Додає запис до книги. Якщо контакт вже є, додає новий номер
        existing_record = self.data.get(record.name.value)
        if existing_record:
            existing_record.phones.extend(record.phones)
        else:
            self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted."
        return "Contact not found."

    def get_upcoming_birthdays(self):
        today = datetime.today()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = [
            f"{record.name.value}: {record.birthday.value.strftime('%d.%m.%Y')}"
            for record in self.data.values() if record.birthday and today <= record.birthday.value.replace(year=today.year) <= next_week
        ]
        return "Upcoming birthdays:\n" + "\n".join(upcoming_birthdays) if upcoming_birthdays else "No upcoming birthdays in the next 7 days."

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter user name."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, address_book):
    if len(args) < 2:
        raise ValueError("Give me name and phone please, separated by a space.")
    name, phone = args[0], args[1]
    record = Record(name)
    record.add_phone(phone)
    address_book.add_record(record)
    return f"Contact {name} added with phone {phone}."

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Give me name and date of birth, separated by a space.")
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    
    record.add_birthday(birthday)
    return f"Birthday for {name} added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None or not record.birthday:
        return "No birthday found for this contact."
    
    return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."

@input_error
def birthdays(args, book):
    return book.get_upcoming_birthdays()

@input_error
def change_contact(args, address_book):
    if len(args) < 2:
        raise ValueError("Give me name and phone please, separated by a space.")
    name, new_phone = args[0], args[1]
    record = address_book.find(name)
    if record:
        old_phone = record.phones[0].value if record.phones else None
        return record.edit_phone(old_phone, new_phone)
    else:
        raise KeyError

@input_error
def get_phone(args, address_book):
    if not args:
        raise IndexError
    name = args[0]
    record = address_book.find(name)
    if record:
        phones_str = '; '.join(phone.value for phone in record.phones)
        return f"Phones for {name}: {phones_str}"
    else:
        raise KeyError
    
@input_error
def del_contact(args, address_book):
    if not args:
        raise IndexError
    name = args[0]
    return address_book.delete(name)

@input_error
def show_all_contacts(address_book):
    if address_book:
        return "\n".join(str(record) for record in address_book.values())
    else:
        return "Address book is empty."

def main():
    address_book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input:
            print("Please enter a command.")
            continue
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))    
        elif command == "change":
            print(change_contact(args, address_book))
        elif command == "delete":
            print(del_contact(args, address_book))
        elif command == "phone":
            print(get_phone(args, address_book))
        elif command == "all":
            print(show_all_contacts(address_book))
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(args, address_book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
