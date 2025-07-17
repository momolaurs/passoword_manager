ABC = "A1234567890'¡qwertyuiop`+asdfghjklñçzxcvbnm,.-!\u00b7$%&/()=?¿QWERTYUIOP^*ASDFGHJKL\u00d1\u00a8\u00c7ZXCVBNM;:_\\|@#~€¬{[]}-"

def vig_table(keyword):
    abc = ABC
    unique_keyword = ""
    seen = set()

    for char in keyword:
        if char not in seen and char in abc:
            unique_keyword += char
            seen.add(char)

    for i in unique_keyword:
        if i in abc:
            abc = abc.replace(i , "")

    vig_tab = unique_keyword + abc
    final_table = []
    for char in range(len(vig_tab)):
        shifted_row = vig_tab[char:] + vig_tab[:char]
        final_table.append(shifted_row)
    return final_table

def print_table(list):
    abc_inx = 0
    final_vg_tb = []
    for row in list:
        if abc_inx == 0:
            final_vg_tb.append(("0", ABC))
            final_vg_tb.append((ABC[abc_inx], row))
            abc_inx += 1
        else:
            final_vg_tb.append((ABC[abc_inx], row))
            abc_inx += 1
    return final_vg_tb

def visualize_table(list):
    abc_inx = 0
    final_vg_tb = []
    for row in list:
        print(ABC[abc_inx], row)
        final_vg_tb.append((ABC[abc_inx], row))
        abc_inx += 1
    return final_vg_tb

def duplicate_word(text, kw2):
    if len(text) <= len(kw2):
        return kw2[:len(text)]
    else:
        multiplier = len(text) // len(kw2) + 1
        return (kw2 * multiplier)[:len(text)]

def encrypt(encrypt_kw, text, vigenere_table):
    final_text = []
    encrypt_kw_idx = 0

    for letter in text:
        if letter in ABC:
            first_row = vigenere_table[0][1]
            index_y = first_row.index(encrypt_kw[encrypt_kw_idx])

            index_x = -1
            for index, (x, _) in enumerate(vigenere_table):
                if x == letter:
                    index_x = index
                    break

            the_letter = vigenere_table[index_x][1][index_y]
            final_text.append(the_letter)
            encrypt_kw_idx += 1
        else:
            final_text.append(letter)
            encrypt_kw_idx += 1

    return "".join(final_text)

def decrypt(encrypt_kw, encrypted_text, vigenere_table):
    decrypted_text = []
    decrypt_kw_inx = 0

    for letter in encrypted_text:
        if letter in ABC:
            first_row = vigenere_table[0][1]
            index_y = first_row.index(encrypt_kw[decrypt_kw_inx])

            index_x = -1
            for index, (x, abcs) in enumerate(vigenere_table[1:]):
                if abcs[index_y] == letter:
                    index_x = index + 1
                    break
            if index_x != -1:
                the_letter = vigenere_table[index_x][0]
                decrypted_text.append(the_letter)
        else:
            decrypted_text.append(letter)
        decrypt_kw_inx += 1

    return "".join(decrypted_text)

def steps_for_encrypting(keyword1, keyword2, text):
    final_table = vig_table(keyword1)
    table = print_table(final_table)
    encrypt_kw = duplicate_word(text, keyword2)
    return (keyword1, encrypt_kw, text, table)

def reorder_ids_alphabetically(cursor, conn):
    # Fetch all passwords ordered by name alphabetically
    cursor.execute("SELECT id, name FROM passwords ORDER BY name ASC")
    rows = cursor.fetchall()
    
    # Temporarily assign negative IDs to avoid UNIQUE constraint conflicts
    temp_id = -1
    for old_id, _ in rows:
        cursor.execute("UPDATE passwords SET id = ? WHERE id = ?", (temp_id, old_id))
        temp_id -= 1
    conn.commit()

    # Assign new sequential positive IDs based on alphabetical order
    new_id = 1
    cursor.execute("SELECT id FROM passwords ORDER BY id ASC")  # This will be in the order of temp negative IDs
    rows = cursor.fetchall()
    for (temp_id,) in rows:
        cursor.execute("UPDATE passwords SET id = ? WHERE id = ?", (new_id, temp_id))
        new_id += 1
    conn.commit()


def reorder_ids(cursor, conn):
    cursor.execute("SELECT id, name FROM passwords ORDER BY name ASC")
    rows = cursor.fetchall()

    new_temp_id = -1
    for row in rows:
        old_id = row[0]
        cursor.execute("UPDATE passwords SET id = ? WHERE id = ?", (new_temp_id, old_id))
        new_temp_id -= 1

    conn.commit()

    new_id = 1
    cursor.execute("SELECT id FROM passwords ORDER BY name ASC")
    rows = cursor.fetchall()
    for row in rows:
        temp_id = row[0]
        cursor.execute("UPDATE passwords SET id = ? WHERE id = ?", (new_id, temp_id))
        new_id += 1

    conn.commit()