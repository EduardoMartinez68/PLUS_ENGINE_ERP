//This function is for load all the translations of the app of the ERP, this function is called forever that the user change the language or load the web
///example: load the language spanish to the app 'sales'
//load_language('/apps/sales/translate.json');
let languageUser = 'pl'; //get the language of the user example (es,pl,en,fr,etc)
let translateOld={};
let lastUrl=''; //here we will save the last loaded URL for avoid loading the same URL again
function load_language(langUrl) {
  //her we will check if the langUrl is equal to the lastUrl, if it is equal we will not load the language again
  if (lastUrl === langUrl) {
    //if we have save the translation of the web, we will apply the translation to the web evit load the language again
    apply_translation_to_the_web(translateOld);
    return;
  }

  //if we not have save the language, will load the language
  fetch(langUrl)
    .then(res => res.json())
    .then(translations => {
      translateOld=translations; //save the translations in the variable translateOld
      apply_translation_to_the_web(translations); //now translate the web with the new translations
      lastUrl = langUrl; //save the last loaded URL
    })
    .catch(err => {
      console.error('Error to load the language:', err);
    });
}

//this function is for translate the web with the translations loaded or saved. The function is called when the user load the web or change the language
function apply_translation_to_the_web(translations) {
  //get all the elements that have the attribute t 
  document.querySelectorAll('[t]').forEach(el => {
    const key = el.getAttribute('t'); //get the key of the translation
    if (translations[key]) el.textContent = translations[key]; //translate the text of the element
  });

  //get all the elements that have the attribute t-placeholder, normally this attribute is used for input, textarea, etc.
  document.querySelectorAll('[t-placeholder]').forEach(el => {
    const key = el.getAttribute('t-placeholder'); //get the key of the translation
    if (translations[key]) el.setAttribute('placeholder', translations[key]); //translate the placeholder of the element
  });

  //translate the attributes of the elements that have the attribute <info-label>
  document.querySelectorAll('info-label').forEach(el => {
    translate_attributes(el, translations);
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
async function get_language_ERP() {
  try {
    const res = await fetch(`/static/language/${languageUser}/language.json`);
    const translations = await res.json();
    return translations;
  } catch (err) {
    console.error('Error to load the language:', err);
    return {};
  }
}

//her we will load the language of the ERP, this function is called when the user load the web or change the language
let LANG={};
get_language_ERP().then(languages => {
  LANG=languages; //save the translations in the variable LANG
  translate_menu_apps(); // Call this function for translate the menu apps when load the language
});


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
function t(key, listLanguage = LANG) {
  // Check if the key exists in the provided listLanguage
  //if not exist in the listLanguage, we will return the key
  return listLanguage[key] || key;
}

function translate_text(key) {
  // Check if the key exists in the provided listLanguage
  //if not exist in the listLanguage, we will return the key
  return translateOld[key] || key;
}

//this functions is for translate the menu of the apps, this function is called when the user load the web or change the language
function translate_menu_apps(){
  //get the list of the apps in the menu
  const menuApps = document.querySelectorAll('.app-name');
  const searchApp=document.getElementById('searchInput'); //get the search input

  //update the placeholder of the search input
  searchApp.setAttribute('placeholder', LANG['menu.search']);

  //here we will translate all the apps that be in the menu
  menuApps.forEach(app => {
    const key = 'app.'+app.textContent.trim(); //create the key for the translation

    //we will check if exist the key in the translations, if exist we will translate the app
    //if not exist we will not translate the app and we will keep the original text
    if (key && LANG[key]) {
      app.textContent = LANG[key];
    }
  });
}
