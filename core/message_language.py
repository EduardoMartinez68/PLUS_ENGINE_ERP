#here we will add most languages for print a message in the screen
message_form = {
    'required_fields': {
        'es': "Por favor completa todos los campos obligatorios.",
        'pl': "Proszę wypełnić wszystkie wymagane pola."
    },
    'email_taken': {
        'es': "Sucedió un error al crear tu cuenta.",
        'pl': "Wystąpił błąd podczas tworzenia konta."
    },
    'password_mismatch': {
        'es': "Las contraseñas no coinciden.",
        'pl': "Hasła nie są zgodne."
    },
    'success': {
        'es': "Cuenta creada exitosamente.",
        'pl': "Konto zostało pomyślnie utworzone."
    },

    'add_email': {
        'es': "Agrega un email",
        'pl': "Dodaj email"
    },
    'email': {
        'es': "Email",
        'pl': "Email"
    },
    'add_username': {
        'es': "Agrega un nombre de usuario",
        'pl': "Dodaj nazwę użytkownika"
    },
    'username': {
        'es': "Nombre de usuario",
        'pl': "Nazwa użytkownika"
    },
    'add_password': {
        'es': "Agrega una contraseña",
        'pl': "Dodaj hasło"
    },
    'confirm_password': {
        'es': "Confirma tu contraseña",
        'pl': "Potwierdź swoje hasło"
    },
    'password': {
        'es': "contraseña",
        'pl': "hasło"
    }
}
lang='es'


def get_message(key):
    return message_form.get(key, {}).get(lang, "")