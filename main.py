import psycopg2


def create_db(conn, cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(70) NOT NULL,
            email VARCHAR(50) NOT NULL);
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            phone VARCHAR(100) NOT NULL);
    """)
    conn.commit()


def add_client(cur, first_name, last_name, email, phone=None):
    if first_name == None or last_name == None or email == None:
        print('Не все поля заполнены, заполните пожалуйста все поля')
        return
    cur.execute("""
    INSERT INTO clients(first_name, last_name, email) VALUES(%s, %s, %s) RETURNING id, first_name, last_name, email;
    """, (first_name, last_name, email))
    new_client = cur.fetchone()
    if phone is not None:
        cur.execute("""
        INSERT INTO phones(client_id, phone) VALUES(%s, %s);
        """, (new_client[0], phone))
        conn.commit()
    print(f'Добавили нового клиента {new_client}')


def get_phone(cur, client_id, phone):
    cur.execute("""
    SELECT phone FROM phones WHERE client_id=%s AND phone=%s;
    """, (client_id, phone))
    found_phone = cur.fetchall()
    return found_phone


def add_phone(conn, cur, client_id, phone):
    # нужно проверить, есть ли добавляемый телефон в базе:
    found_phone = get_phone(cur, client_id, phone)
    if found_phone is None or len(found_phone) == 0:
        print(found_phone, client_id, phone)
        cur.execute("""
        INSERT INTO phones(client_id, phone) VALUES(%s, %s);
        """, (client_id, phone))
        conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    if first_name is not None:
        cur.execute("""
        UPDATE clients SET first_name=%s WHERE id=%s;
        """, (first_name, client_id))
    if last_name is not None:
        cur.execute("""
        UPDATE clients SET last_name=%s WHERE id=%s;
        """, (last_name, client_id))
    if email is not None:
        cur.execute("""
        UPDATE clients SET email=%s WHERE id=%s;
        """, (email, client_id))
    if phone is not None:
        add_phone(conn, cur, client_id, phone)
    cur.execute("""
    SELECT * FROM clients;
    """)
    cur.fetchall()
    conn.commit()


def delete_phone(cur, client_id, phone):
    cur.execute("""
    DELETE FROM phones WHERE client_id=%s and phone=%s;
    """, (client_id, phone))
    cur.execute("""
            SELECT * FROM phones WHERE client_id=%s;
            """, (client_id,))
    print(cur.fetchall())


def delete_client(cur, client_id):
    cur.execute("""
    DELETE FROM phones WHERE client_id=%s;
    """, (client_id,))
    cur.execute("""
    DELETE FROM clients WHERE id=%s;
    """, (client_id,))
    cur.execute("""
    SELECT * FROM clients;
    """)
    print(cur.fetchall())


def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    if phone is not None:
        cur.execute("""
        SELECT client_id FROM clients
        JOIN phones ON phones.client_id = client_id WHERE phones.phone=%s
        """, (phone,))
    else:
        cur.execute("""
        SELECT id FROM clients WHERE first_name=%s OR last_name=%s OR email=%s;
        """, (first_name, last_name, email))
    print(cur.fetchall())


def all_clients(cur):
    cur.execute("""
    SELECT * FROM clients;
    """)
    print(cur.fetchall())
    cur.execute("""
    SELECT * FROM phones;
    """)
    print(cur.fetchall())


if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        DROP TABLE phones;
                        DROP TABLE clients;
                        """)
            create_db(conn, cur)
            all_clients(cur)
            print('Добавить клиента')
            add_client(cur, 'Игорь', 'Соколов', 'sokolik1063@mail.ru', '+79218895336')
            add_client(cur, 'Николай', 'Зырянов', 'NZyrianov@yandex.ru')
            add_client(cur, 'Оксана', 'Гавриленко', 'oksana1063@bk.ru', '+79531505093')
            add_client(cur, 'Виктория', None, None)
            add_client(cur, 'Рустам', 'Чембарисов', None)
            add_client(cur, 'Андрей', 'Денисов', 'Andi_den@icloud.com')
            all_clients(cur)
            print('Найти телефон')
            print(get_phone(cur, '1', '+79052033603'))
            print('Добавить телефон')
            add_phone(conn, cur, '2', '+79602717127')
            add_phone(conn, cur, '1', '+79052051649')
            add_phone(conn, cur, '3', '+76516831965')
            all_clients(cur)
            print('Изменить данные клиента')
            change_client(conn, '1', 'Феофан')
            change_client(conn, '2', None, 'Петров')
            change_client(conn, '3', None, None, 'og1994@mail.ru')
            change_client(conn, '2', None, None, None, '+79536985789')
            all_clients(cur)
            print('Удалить телефон')
            delete_phone(cur, '1', '+79218895336')
            delete_phone(cur, '2', '+79602717127')
            all_clients(cur)
            print('Найти клиента')
            find_client(cur, 'Феофан')
            find_client(cur, None, 'Гавриленко')
            find_client(cur, None, None, 'Andi_den@icloud.com')
            find_client(cur, None, None, None, '+79536985789')
            all_clients(cur)
            print('Удалить клиента')
            delete_client(cur, 1)

conn.close()
