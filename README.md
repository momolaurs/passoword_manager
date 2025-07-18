# PLACEHOLDER: a password manager
A simple password manager that utilizes the [Vigenère cipher](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher) (double encryption) as its encoding method and SQL as its database.

## Necessary libraries
- sqlite3
- PyQt6

## How to run
- First, run `database_setup.py` to create the `passwords.db` file.
- Then you can run `password_app.py` after making sure `passwords.db` and `vigenere_creation.py` are in the same directory.

## How it works

- After running `password_app.py`, a window will pop up asking for your name and two code words.
- Then, you can freely view, add, and delete your passwords.
- You will only be able to see the decoded version if you input the correct code words at the start; anyone else who doesn't know will only see the encoded version.
> 💡 **Note:**
> 1. Please make sure you remember these code words, as you will need them every time you open the file.
> 
> 2. These words are case-sensitive; changes in capitalization will mean the passwords are not correctly decoded.
> 
> 3. The accepted characters are: "A1234567890'¡qwertyuiop`+asdfghjklñçzxcvbnm,.-!\u00b7$%&/()=?¿QWERTYUIOP^*ASDFGHJKL\u00d1\u00a8\u00c7ZXCVBNM;:_\\|@#~€¬{[]}-" any different input will result in errors.


## Features
**Version 1.0:**
- View/Search passwords
- Add passwords
- Delete passwords

**Version 2.0:**
- Visualize your Vigenère table
- Encrypt/Decrypt text

## Contact
For any issue, error, bug, or just to fangirl about Vigenère Ciphers, feel free to contact the author, Laura Moset Estruch. 

Email: lauramosetestruch@gmail.com || Linkedin: [HERE](https://www.linkedin.com/in/laura-moset-estruch-56b452237/)
