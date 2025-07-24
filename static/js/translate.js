//This function is for load all the translations of the app of the ERP, this function is called forever that the user change the language or load the web
///example: load the language spanish to the app 'sales'
//load_language('/apps/sales/translate.json');
let translateOld={};
function load_language(langUrl) {
  fetch(langUrl)
    .then(res => res.json())
    .then(translations => {
        translateOld=  translations; //save the translations in the variable translateOld
      // Translate the container (textContent)
      document.querySelectorAll('[t]').forEach(el => {
        const key = el.getAttribute('t');
        if (translations[key]) {
          el.textContent = translations[key];
        }
      });

      // Translate the placeholders of the inputs
      document.querySelectorAll('[t-placeholder]').forEach(el => {
        const key = el.getAttribute('t-placeholder');
        if (translations[key]) {
          el.setAttribute('placeholder', translations[key]);
        }
      });

      //this is for translate the attributes of the elements as info-label
      document.querySelectorAll('info-label').forEach(el => {
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
  console.log('translate_attributes', element, translations);
  const keyLabel = element.getAttribute('label');
  if (keyLabel && translations[keyLabel]) {
    element.setAttribute('label', translations[keyLabel]);
  }

  const keyMessage = element.getAttribute('message');
  if (keyMessage && translations[keyMessage]) {
    element.setAttribute('message', translations[keyMessage]);
  }
  
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
    "info.logout": "Cerrar sesión",
    "info.searching": "Buscando...",
    "info.no_results": "No se encontraron resultados",
    "info.loading_data": "Cargando datos...",

    "menu.search": "Buscar una app...",
    "app.agenda": "Agenda",
    "app.cases": "Casos",
    "app.contracts": "Contratos",
    "app.customers": "Clientes",
    "app.settings": "Configuraciones",
    "app.exit": "Salir"
  },





    "pl": {
    "success.saved": "Pomyślnie zapisano",
    "success.updated": "Pomyślnie zaktualizowano",
    "success.deleted": "Pomyślnie usunięto",
    "success.sent": "E-mail wysłany",
    "success.added": "Pomyślnie dodano",

    "error.failed_delete": "Nie udało się usunąć",
    "error.failed_save": "Nie udało się zapisać",
    "error.not_found": "Nie znaleziono",
    "error.unauthorized": "Brak autoryzacji",
    "error.required_fields": "Wszystkie pola są wymagane",
    "error.general": "Wystąpił błąd",

    "warning.unsaved_changes": "Masz niezapisane zmiany",
    "warning.permanent_action": "Ta czynność jest nieodwracalna",
    "warning.no_results": "Nie znaleziono wyników",

    "info.loading": "Ładowanie...",
    "info.sending": "Wysyłanie...",
    "info.confirm_delete": "Czy na pewno chcesz to usunąć?",
    "info.welcome": "Witamy",
    "info.logout": "Wyloguj się",
    "info.searching": "Wyszukiwanie...",
    "info.no_results": "Nie znaleziono wyników",
    "info.loading_data": "Ładowanie danych...",

    "menu.search": "Szukaj aplikacji...",
    "app.agenda": "plan zadań",
    "app.cases": "Sprawy",
    "app.contracts": "Kontrakty",
    "app.customers": "Klienci",
    "app.settings": "Ustawienia",
    "app.exit": "Wyloguj się"
    }
};

//this function is for translate the new container that the user load in the app, when serach in a table, get information from the server, etc.
function translate_dynamic_content(container) {
  container.querySelectorAll('[t]').forEach(el => {
    const key = el.getAttribute('t');
    if (translateOld[key]) {
      el.textContent = translateOld[key];
    }
  });

  container.querySelectorAll('[t-placeholder]').forEach(el => {
    const key = el.getAttribute('t-placeholder');
    if (translateOld[key]) {
      el.setAttribute('placeholder', translateOld[key]);
    }
  });

  container.querySelectorAll('info-label').forEach(el => {
    translate_attributes(el, translations);
  });
}


//the user can add more languages to the app, for example:
// LANG['es'] = { "success.saved": "Guardado con éxito", ... };
let lenguaceUser = 'pl'; //get the lenguace of the user
function t(key, listLanguage = LANG) {
  return listLanguage[lenguaceUser][key] || key;
}

function translate_text(key) {
  return translateOld[key] || key;
}


function traslate_menu_apps(){
  const menuApps = document.querySelectorAll('.app-name');
  const searchApp=document.getElementById('searchInput');
  searchApp.setAttribute('placeholder', LANG[lenguaceUser]['menu.search']);

  menuApps.forEach(app => {
    const key = 'app.'+app.textContent.trim();
    if (key && LANG[lenguaceUser][key]) {
      app.textContent = LANG[lenguaceUser][key];
    }
  });
}
traslate_menu_apps();