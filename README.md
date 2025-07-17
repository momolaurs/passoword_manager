# PLACEHOLDER: a password manager
A simple password manager that utilizes the [Vigenère cipher](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher) as its encryption method and SQL as its database.

## Necessary libraries
- sqlite3
- PyQt6

## How to run
- First, run `database_setup.py` to create the `passwords.db` file.
- Then you can run `password_app.py` after making sure `passwords.db` and `vigenere_creation.py` are in the same directory.

## How it works

- After running `password_app.py`, a window will pop up asking for your name and two code words.
> 💡 **Note:**
> \n 1. Make sure you remember these code words as you will need them every time you open the file.
> These words are case sensitive; changes in capitalization will result in errors!
> The accepted characters are: "A1234567890'¡qwertyuiop`+asdfghjklñçzxcvbnm,.-!\u00b7$%&/()=?¿QWERTYUIOP^*ASDFGHJKL\u00d1\u00a8\u00c7ZXCVBNM;:_\\|@#~€¬{[]}-" any different input will result in errors.
- Then, you can freely view, add, and delete your passwords. You will be able to see the decoded version as you input the correct code words; anyone else who doesn't know will only see the encoded version.

## Features
Version 1.0:
- View passwords
- Add passwords
- Delte passwords
