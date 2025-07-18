import sqlite3
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea,
    QVBoxLayout, QMessageBox, QInputDialog, QDialog, QListWidget, QHBoxLayout, QFrame, QTextEdit   
)
from PyQt6.QtCore import Qt
from vigenere_creation import duplicate_word, encrypt, decrypt, steps_for_encrypting,reorder_ids, reorder_ids_alphabetically, vig_table, visualize_table, print_table, ABC


# Connect to SQL database
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

class DeleteDialog(QDialog):
    def __init__(self, keyword2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Password")
        self.keyword2 = keyword2
        self.selected_id = None

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Type to search password to delete:"))

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_selected)
        layout.addWidget(self.list_widget)

        self.populate_list()

        self.delete_btn = QPushButton("Delete Selected Password")
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.delete_btn.setEnabled(False)
        layout.addWidget(self.delete_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

    def populate_list(self):
        cursor.execute("SELECT id, name FROM passwords ORDER BY id")
        self.password_items = cursor.fetchall()
        self.update_list(self.password_items)

    def update_list(self, items):
        self.list_widget.clear()
        for pw_id, name in items:
            self.list_widget.addItem(name)  # Only add the name, no number

    def filter_list(self, text):
        text = text.lower()
        filtered = [(pw_id, name) for pw_id, name in self.password_items if text in name.lower()]
        self.update_list(filtered)

    def item_selected(self, item):
        selected_name = item.text()
        # Find ID from name (assuming names are unique)
        for pw_id, name in self.password_items:
            if name == selected_name:
                self.selected_id = pw_id
                break
        self.delete_btn.setEnabled(True)

    def confirm_delete(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "No Selection", "Please select a password to delete.")
            return

        code_word, ok = QInputDialog.getText(self, "Confirm Deletion", "Enter your Code Word 2:")
        if not ok or code_word != self.keyword2:
            QMessageBox.warning(self, "Failed", "Incorrect code word. Deletion canceled.")
            return

        cursor.execute("SELECT name FROM passwords WHERE id = ?", (self.selected_id,))
        row = cursor.fetchone()
        if row is None:
            QMessageBox.warning(self, "Not Found", "Password ID not found.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{row[0]}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            cursor.execute("DELETE FROM passwords WHERE id = ?", (self.selected_id,))
            conn.commit()
            reorder_ids(cursor, conn)
            QMessageBox.information(self, "Success", "Password deleted.")
            self.accept()
        else:
            QMessageBox.information(self, "Canceled", "Deletion canceled.")

class InfoDialog(QDialog):
    def __init__(self, keyword1, keyword2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Password Information")
        self.selected_id = None
        self.keyword1 = keyword1
        self.keyword2 = keyword2

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Type to search for a password:"))

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_selected)
        layout.addWidget(self.list_widget)

        self.populate_list()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def populate_list(self):
        cursor.execute("SELECT id, name FROM passwords ORDER BY id")
        self.password_items = cursor.fetchall()
        self.update_list(self.password_items)

    def update_list(self, items):
        self.list_widget.clear()
        for pw_id, name in items:
            self.list_widget.addItem(name)

    def filter_list(self, text):
        text = text.lower()
        filtered = [(pw_id, name) for pw_id, name in self.password_items if text in name.lower()]
        self.update_list(filtered)

    def item_selected(self, item):
        selected_name = item.text()
        for pw_id, name in self.password_items:
            if name == selected_name:
                self.selected_id = pw_id
                break
        self.show_password_info(self.selected_id)

    def show_password_info(self, pw_id):
        cursor.execute("SELECT name, email, username, password FROM passwords WHERE id = ?", (pw_id,))
        row = cursor.fetchone()
        if row:
            name, email, username, encrypted_password = row

            # Prepare Vigenère table and decryption key
            _, encrypt_kw, _, table = steps_for_encrypting(self.keyword1, self.keyword2, encrypted_password)
            # Duplicate keyword2 to match length of password for decrypt
            decrypt_kw = duplicate_word(encrypted_password, self.keyword2)
            decrypted_pw = decrypt(decrypt_kw, encrypted_password, table)

            info_text = (
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Username: {username}\n"
                f"Password: {decrypted_pw}"
            )
            QMessageBox.information(self, "Password Information", info_text)
        else:
            QMessageBox.warning(self, "Error", "Password information not found.")

class EncryptDialog(QDialog):
    def __init__(self, keyword1, keyword2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Encrypt Text")
        self.resize(300, 150)

        self.inputs = [keyword1, keyword2]

        layout = QVBoxLayout()

        #get text to encrypt
        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        #encrypt button
        encrypt_button = QPushButton("Encrypt")
        encrypt_button.clicked.connect(self.encrypt_text)
        layout.addWidget(encrypt_button)

        #cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def encrypt_text(self):
        text = self.text_input.text()
        _, encrypt_kw, _, table = steps_for_encrypting(self.inputs[0], self.inputs[1], text)
        encrypted_text = encrypt(encrypt_kw, text, table)

        # Create a pop-up dialog to show encrypted text
        dialog = QDialog(self)
        dialog.setWindowTitle("Encrypted Result")
        dialog.resize(400, 200)

        layout = QVBoxLayout(dialog)

        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setPlainText(encrypted_text)  # This allows copy & paste
        layout.addWidget(text_display)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

class DecryptDialog(QDialog):
    def __init__(self, keyword1, keyword2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Decrypt Text")
        self.resize(300, 150)

        self.inputs = [keyword1, keyword2]

        layout = QVBoxLayout()

        #get text to decrypt
        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        #decrypt button
        decrypt_button = QPushButton("Decrypt")
        decrypt_button.clicked.connect(self.decrypt_text)
        layout.addWidget(decrypt_button)

        #cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def decrypt_text(self):
        text = self.text_input.text()
        _, decrypt_kw, _, table = steps_for_encrypting(self.inputs[0], self.inputs[1], text)
        decrypted_text = decrypt(decrypt_kw, text, table)

        # Create a pop-up dialog to show decrypted text
        dialog = QDialog(self)
        dialog.setWindowTitle("Decrypted Result")
        dialog.resize(400, 200)

        layout = QVBoxLayout(dialog)

        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setPlainText(decrypted_text)  # This allows copy & paste
        layout.addWidget(text_display)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()
class SecondWindow(QWidget):
    def __init__(self, inputs):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.resize(400, 300)

        self.inputs = inputs

        # --- Main layout ---
        main_layout = QVBoxLayout(self)

        # --- Top bar ---
        top_bar = QHBoxLayout()
        top_bar.addStretch() 

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedWidth(40)
        self.menu_button.clicked.connect(self.toggle_side_menu)
        top_bar.addWidget(self.menu_button)

        main_layout.addLayout(top_bar)

        # --- Central content layout ---
        self.content_layout = QHBoxLayout()

        # --- Side menu ---
        self.side_menu = QFrame()
        self.side_menu.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_menu.setFixedHeight(300)
        self.side_menu.setFixedWidth(150)
        self.side_menu.setVisible(False) 
        

        side_menu_layout = QVBoxLayout()
        side_menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        side_button1 = QPushButton("Create Vigenere Table")
        side_button2 = QPushButton("Encrypt Text")
        side_button3 = QPushButton("Decrypt Text")
        side_button4 = QPushButton("Change code words")

        side_button1.clicked.connect(self.visualize_table)
        side_button2.clicked.connect(self.encrypt_text)
        side_button3.clicked.connect(self.decrypt_text)
        side_button4.clicked.connect(self.change_code_words)

        # Add more side buttons here

        side_menu_layout.addWidget(side_button1)
        side_menu_layout.addWidget(side_button2)
        side_menu_layout.addWidget(side_button3)
        side_menu_layout.addWidget(side_button4)
        self.side_menu.setLayout(side_menu_layout)



        # --- Main content area ---
        self.main_content = QVBoxLayout()

        greeting = QLabel(f"Welcome, {inputs[0]}!")
        greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_content.addWidget(greeting)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for a password...")
        self.search_bar.textChanged.connect(self.search_passwords)
        self.main_content.addWidget(self.search_bar)

        self.add_btn = QPushButton("Add a new password")
        self.add_btn.clicked.connect(self.add_password)
        self.main_content.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete a password")
        self.delete_btn.clicked.connect(self.delete_password)
        self.main_content.addWidget(self.delete_btn)

        self.view_btn = QPushButton("View all passwords")
        self.view_btn.clicked.connect(self.view_passwords)
        self.main_content.addWidget(self.view_btn)

        self.content_layout.addLayout(self.main_content)
        self.content_layout.addWidget(self.side_menu)

        main_layout.addLayout(self.content_layout)
        

    def toggle_side_menu(self):
        self.side_menu.setVisible(not self.side_menu.isVisible())
    
    def visualize_table(self):
        table = vig_table(self.inputs[1])
        output_lines = visualize_table(table)  # must return a list of strings

        dialog = QDialog(self)
        dialog.setWindowTitle("Password Table")
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        text_box = QTextEdit()
        text_box.setReadOnly(True)

        # 👇 Convert list of lines to one big string for display
        text_output = '\n'.join(' '.join(map(str, row)) for row in output_lines)
        text_box.setPlainText(text_output)

        layout.addWidget(text_box)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec()
    
    def encrypt_text(self):
        dialog = EncryptDialog(self.inputs[1], self.inputs[2], self)
        dialog.exec()
    
    def decrypt_text(self):
        dialog = DecryptDialog(self.inputs[1], self.inputs[2], self)
        dialog.exec()
    
    def change_code_words(self):
        self.first_window = Login()
        self.first_window.show()
        self.hide()
    
    def search_passwords(self):
        dialog = InfoDialog(self.inputs[1], self.inputs[2], self)
        dialog.exec()

    def add_password(self):
        name, ok1 = QInputDialog.getText(self, "Add Password", "App/Service:")
        email, ok2 = QInputDialog.getText(self, "Add Password", "Email:")
        username, ok3 = QInputDialog.getText(self, "Add Password", "Username:")
        password, ok4 = QInputDialog.getText(self, "Add Password", "Password:")

        if not all([ok1, ok2, ok3, ok4]) or not all([name, email, username, password]):
            QMessageBox.warning(self, "Input Error", "All fields must be filled!")
            return

        try:
            keyword1 = self.inputs[1]
            keyword2 = self.inputs[2]
            _, encrypt_kw, text, table = steps_for_encrypting(keyword1, keyword2, password)
            encrypted_password = encrypt(encrypt_kw, text, table)

            cursor.execute(
                "INSERT INTO passwords (name, email, username, password) VALUES (?, ?, ?, ?)",
                (name, email, username, encrypted_password)
            )
            conn.commit()
            reorder_ids_alphabetically(cursor, conn)
            QMessageBox.information(self, "Success", "Password added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong:\n{e}")

    def delete_password(self):
        dialog = DeleteDialog(self.inputs[2], self)
        dialog.exec()

    def view_passwords(self):
        keyword1 = self.inputs[1]
        keyword2 = self.inputs[2]

        cursor.execute("SELECT name, email, username, password FROM passwords ORDER BY name COLLATE NOCASE")
        rows = cursor.fetchall()

        if not rows:
            QMessageBox.information(self, "Empty", "No passwords stored.")
            return

        _, encrypt_kw, _, table = steps_for_encrypting(keyword1, keyword2, "")

        # Create a scrollable dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Stored Passwords")
        dialog.resize(400, 500)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout()

        for row in rows:
            decrypted_pw = decrypt(duplicate_word(row[3], keyword2), row[3], table)
            label = QLabel(
                f"<b>Name:</b> {row[0]}<br>"
                f"<b>Email:</b> {row[1]}<br>"
                f"<b>Username:</b> {row[2]}<br>"
                f"<b>Password:</b> {decrypted_pw}<br>"
                f"<hr>"
            )
            label.setWordWrap(True)
            layout.addWidget(label)

        container.setLayout(layout)
        scroll_area.setWidget(container)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(scroll_area)
        dialog.setLayout(dialog_layout)

        dialog.exec()



class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(300, 200)

        self.layout = QVBoxLayout()

        self.input1 = QLineEdit()
        self.input1.setPlaceholderText("Name")
        self.layout.addWidget(self.input1)

        self.input2 = QLineEdit()
        self.input2.setPlaceholderText("Code Word 1")
        self.layout.addWidget(self.input2)

        self.input3 = QLineEdit()
        self.input3.setPlaceholderText("Code Word 2")
        self.layout.addWidget(self.input3)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.open_second_window)
        self.layout.addWidget(self.submit_btn)

        
        self.input1.returnPressed.connect(self.open_second_window)
        self.input2.returnPressed.connect(self.open_second_window)
        self.input3.returnPressed.connect(self.open_second_window)


        self.setLayout(self.layout)
        self.second_window = None

    def open_second_window(self):
        inputs = [self.input1.text(), self.input2.text(), self.input3.text()]
        if all(inputs):
            self.second_window = SecondWindow(inputs)
            self.second_window.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill all three inputs!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    first_win = Login()
    first_win.show()
    sys.exit(app.exec())

    cursor.close()
    conn.close()