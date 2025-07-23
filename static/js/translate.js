//This function is for load all the translations of the app of the ERP, this function is called forever that the user change the language or load the web
///example: load the language spanish to the app 'sales'
//load_language('/apps/sales/translate.json');
function load_language(langUrl) {
  console.log('load translate from:', langUrl);
  fetch(langUrl)
    .then(res => res.json())
    .then(translations => {
      // Translate the container (textContent)
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[key]) {
          el.textContent = translations[key];
        }
      });

      // Translate the placeholders of the inputs
      document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
          el.setAttribute('placeholder', translations[key]);
        }
      });

      //this is for translate the attributes of the elements that have the attribute data-i18n-attr
      document.querySelectorAll('[data-i18n-attr]').forEach(el => {
        translate_attributes(el, translations);
      });

    })
    .catch(err => {
      console.error('Error cargando idioma:', err);
    });
}


/*
    this function is for translate the attributes of the elements that have the attribute data-i18n-attr
    the value of the attribute is a list of attributes separated by commas, for example: data-i18n-attr="title,alt"
    the function will translate the attributes using the translations object.

    This function is for translate the labels of the ERP, for example:
    <label-info   
    label="language.input_name"
    message="language.input_message"
    data-i18n-attr="label,message">
    </label-info>
*/
function translate_attributes(element, translations) {
  const attrList = element.getAttribute('data-i18n-attr');
  if (!attrList) return;

  attrList.split(',').forEach(attr => {
    const key = element.getAttribute(attr);
    if (translations[key]) {
      element.setAttribute(attr, translations[key]);
    }
  });
}

/*
this function is for translate the text that the programmer do with the alert with help of the alert of the ERP or message pop to the user EXAMPLE:
alert(t("language.error_occurred"));
console.log(t("language.loading"));
*/
let LANG = {
  "es": {
    "success.saved": "Guardado con éxito",
    "success.updated": "Actualizado correctamente",
    "success.deleted": "Eliminado con éxito",
    "success.sent": "Correo enviado",
    "success.added": "Agregado correctamente",

    "error.failed_delete": "No se pudo eliminar",
    "error.failed_save": "No se pudo guardar",
    "error.not_found": "No encontrado",
    "error.unauthorized": "No autorizado",
    "error.required_fields": "Todos los campos son obligatorios",
    "error.general": "Ocurrió un error",

    "warning.unsaved_changes": "Tienes cambios sin guardar",
    "warning.permanent_action": "Esta acción es permanente",
    "warning.no_results": "No se encontraron resultados",

    "info.loading": "Cargando...",
    "info.sending": "Enviando...",
    "info.confirm_delete": "¿Estás seguro de que deseas eliminar esto?",
    "info.welcome": "Bienvenido",
    "info.logout": "Cerrar sesión"
  },

  "pl": {
    "success.saved": "Zapisano pomyślnie",
    "success.updated": "Zaktualizowano pomyślnie",
    "success.deleted": "Pomyślnie usunięto",
    "success.sent": "Wysłano e-mail",
    "success.added": "Pomyślnie dodano",

    "error.failed_delete": "Nie udało się usunąć",
    "error.failed_save": "Nie udało się zapisać",
    "error.not_found": "Nie znaleziono",
    "error.unauthorized": "Brak autoryzacji",
    "error.required_fields": "Wszystkie pola są wymagane",
    "error.general": "Wystąpił błąd",

    "warning.unsaved_changes": "Masz niezapisane zmiany",
    "warning.permanent_action": "Ta akcja jest nieodwracalna",
    "warning.no_results": "Nie znaleziono wyników",

    "info.loading": "Ładowanie...",
    "info.sending": "Wysyłanie...",
    "info.confirm_delete": "Czy na pewno chcesz to usunąć?",
    "info.welcome": "Witamy",
    "info.logout": "Wyloguj się"
  }
};


//the user can add more languages to the app, for example:
// LANG['es'] = { "success.saved": "Guardado con éxito", ... };
let currentLang = 'es'; //get the lenguace of the user
function t(key, listLanguage = LANG) {
  return listLanguage[currentLang][key] || key;
}
