USERS = {
    'admin': '123',
    'usuario': '123',
    'usu2': '123'
}

def valida_senha(username, password):
    if username in USERS and USERS[username] == password:
        return True
    return False