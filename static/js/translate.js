//This function is for load all the translations of the app of the ERP, this function is called forever that the user change the language or load the web
///example: load the language spanish to the app 'sales'
//load_language('/apps/sales/translate.json');
function get_language_of_the_system() {
  // Get the language stored in localStorage, or fallback to the browser's language
  const savedLang = localStorage.getItem('site_lang');
  const browserLang = (navigator.language || navigator.userLanguage || 'es').toLowerCase();

  // Supported language mapping
  const listLanguages = {
    'es': 'es',   // Spanish
    'en': 'es',   // Map English to Spanish by default
    'pl': 'pl',   // Polish
    'pl-pl': 'pl'
  };

  // Determine which language to use: saved language takes priority
  const langToUse = savedLang || browserLang;

  // Extract the main language code (before '-')
  const langCode = langToUse.split('-')[0];

  // Return the mapped language or default to Spanish
  return listLanguages[langCode] || 'es';
}

let languageUser=get_language_of_the_system()//'pl' 'es'; //get the language of the user example (es,pl,en,fr,etc)
let translateOld={};
let lastUrl=''; //here we will save the last loaded URL for avoid loading the same URL again
let numberLanguageLoad=0;
let allTheDictionary=[];
const MAX_DICTIONARIES = 5;
const VERSION_LANGUAGES_PLUS = '1.0.3'; //here is the version of the software PLUS

//here we will see if exist in memory the dictionary that the user can save
const storedDict = localStorage.getItem('allTheDictionary');
if (storedDict) {
  try {
    allTheDictionary = JSON.parse(storedDict);
  } catch (err) {
    console.warn("Error to load the dictionaries from localStorage", err);
  }
}

/*
async function load_language(langUrl) {
  //her we will check if the langUrl is equal to the lastUrl, if it is equal we will not load the language again
  if (lastUrl === langUrl) {
    //if we have save the translation of the web, we will apply the translation to the web evit load the language again
    apply_translation_to_the_web(translateOld);
    return;
  }
  //

  //if we not have save the language, will load the language
  try {
    const res = await fetch(langUrl);
    const translations = await res.json();
    translateOld = translations;
    apply_translation_to_the_web(translations);
    lastUrl = langUrl;


  } catch (err) {
    console.error('Error to load the language:', err);
  }
}
*/

async function load_language(langUrl, first=true) {
  
  if (lastUrl === langUrl) {
    //if we have save the translation of the web, we will apply the translation to the web evit load the language again
    //apply_translation_to_the_web(existing.dictionary);
    //return;
  }

  const MAX_DICTIONARIES = 8;

  //we will see if already exist the dictionary in the memory not coming back to load the dictionary
  //and translate the web 
  const existing = allTheDictionary.find(d => d.name === langUrl);
  if (existing) {
    apply_translation_to_the_web(existing.dictionary);
    return;
  }

  //if not exist the dictionary now we will the download and save in memory
  try {
    const res = await fetch(`${langUrl}?v=${VERSION_LANGUAGES_PLUS}`);
    const translations = await res.json();

    // if the memory of the cache be full, delete the more old
    if (allTheDictionary.length >= MAX_DICTIONARIES) {
      allTheDictionary.shift();
    }

    // save the new dictionary in memory
    allTheDictionary.push({ name: langUrl, dictionary: translations });

    //now we will see if the app have other app like dependencies for load his translate also
    //get the path of the information of the app
    const configUrl = get_base_path_from_lang_url(langUrl) + "config.yaml";
    const infoConfig=await load_config(configUrl);

    //if this app have dependencies, now we will to load his language
    if (infoConfig && infoConfig?.dependencies) {
      for(var i=0;i<infoConfig.dependencies.length;i++){
        const link=`static/${infoConfig.dependencies[i]}/config/locale/${languageUser}/translate.json`;
        await load_language(link, false);
      }
    }

    //save in localStorage
    try {
      localStorage.setItem('allTheDictionary', JSON.stringify(allTheDictionary));
    } catch(e) {
      console.warn("Not can save the dictionaries", e);
    }

    // apply the translate
    if(first){
      lastUrl=langUrl;
    }
    apply_translation_to_the_web(translations);
  } catch (err) {
    console.error('Error loading dictionary:', err);
  }
}

async function load_config(configUrl) {
  try {
    const response = await fetch(configUrl);
    if (!response.ok) throw new Error(`No can load the file YAML in the path: ${configUrl}`);

    const yamlText = await response.text();
    const config = jsyaml.load(yamlText);

    return config;
  } catch (error) {
    console.error('❌ Error to load YAML:', error);
    return null;
  }
}

function get_base_path_from_lang_url(langUrl) {
  return langUrl.replace(/locale\/.*\/translate\.json$/, "");
}


//this function is for translate the web with the translations loaded or saved. The function is called when the user load the web or change the language
function apply_translation_to_the_web(translations) {
  //get all the elements that have the attribute t 
  document.querySelectorAll('[t]').forEach(el => {
    const key = el.getAttribute('t');         // key for translate
    const iconClass = el.getAttribute('icon'); // example: 'fi fi-rr-upload'
    const text = translate_text(key);          // text translate

    // clear the container of the element
    el.textContent = ''; 

    // if exist a icon, we will to create the label <i> 
    if (iconClass) {
      const iconEl = document.createElement('i');
      iconEl.className = iconClass;
      iconEl.style.marginRight = '6px'; // littler space in the text
      el.appendChild(iconEl);
    }

    // add the text with his translate
    el.appendChild(document.createTextNode(text));
  });

  //get all the elements that have the attribute t-placeholder, normally this attribute is used for input, textarea, etc.
  document.querySelectorAll('[t-placeholder]').forEach(el => {
    const key = el.getAttribute('t-placeholder'); //get the key of the translation
    el.setAttribute('placeholder', translate_text(key));  //translate the placeholder of the element
  });

  //translate the attributes of the elements that have the attribute <info-label>
  document.querySelectorAll('info-label').forEach(el => {
    translate_attributes(el, translations);
  });
}

/*
    this function is for translate the attributes of the elements that have the attribute t
    the value of the attribute is a list of attributes separated by commas, for example: t="title,alt"
    the function will translate the attributes using the translations object.

    This function is for translate the labels of the ERP, for example:
    <label-info   
    label="language.input_name"
    message="language.input_message"
    t="label,message">
    </label-info>
*/
function translate_attributes(element, translations) {
  const keyLabel = element.getAttribute('label');
  if(keyLabel){
    element.setAttribute('label',translate_text(keyLabel));
  }

  const keyMessage = element.getAttribute('message');
  if (keyMessage) {
    element.setAttribute('message', translate_text(keyMessage));
  }
  
}


/*
this function is for translate the text that the programmer do with the alert with help of the alert of the ERP or message pop to the user EXAMPLE:
alert(t("language.error_occurred"));
console.log(t("language.loading"));
*/
async function get_language_ERP() {
  try {
    const res = await fetch(`/static/language/${languageUser}/language.json?v=${VERSION_LANGUAGES_PLUS}`);
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
    const key = el.getAttribute('t');         // key for translate
    const iconClass = el.getAttribute('icon'); // example: 'fi fi-rr-upload'
    const text = translate_text(key);          // text translate

    // clear the container of the element
    el.textContent = ''; 

    // if exist a icon, we will to create the label <i> 
    if (iconClass) {
      const iconEl = document.createElement('i');
      iconEl.className = iconClass;
      iconEl.style.marginRight = '6px'; // littler space in the text
      el.appendChild(iconEl);
    }

    // add the text with his translate
    el.appendChild(document.createTextNode(text));
  });

  container.querySelectorAll('[t-placeholder]').forEach(el => {
    const key = el.getAttribute('t-placeholder');
    el.setAttribute('placeholder', translate_text(key));
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

function has_valid_array_data(arr) {
  return Array.isArray(arr) &&
    arr.some(
      v =>
        v !== null &&
        v !== undefined &&
        (typeof v !== 'string' || v.trim() !== '')
    );
}

function applyKeys(text, keys) {
  if (!keys) return text;

  //if is a string we will to trasnformt this to a array
  if (typeof keys === 'string') {
    keys = [keys];
  }

  // if is an array → remplace the text ${} in order
  if (Array.isArray(keys)) {
    if (!has_valid_array_data(keys)) return text; //if not have nothing in the array
    let i = 0;
    return text.replace(/\$\{\}/g, () => keys[i++] ?? '');
  }

  // if it is a object → ${name}
  if (typeof keys === 'object') {
    return text.replace(/\$\{(\w+)\}/g, (_, key) => {
      return keys[key] ?? '';
    });
  }

  return text;
}

function translate_text(labelKey, keys=null) {
  /*
   here we will to translate a text that the programer send 
   labelKey: app.label.text (this is the key that we will use for know how translate a text)
   keys: {"edward", "1", "2"} (this are the word that use for remplace the text of labelKey)

   example:
   app.label.text: "This is a example for ${}"
   keys: {"you"}

   the text translate be 'This is a example for you' this is only if 'keys' not is null
  translate_text(
    'app.example',
    { name: 'Edward', count: 3 }
  );
  "Hello ${name}, you have ${count} messages"  -> "Hello Edward, you have 3 messages"

  translate_text(
    'app.example',
    ['Edward', 3]
  );
  "Hello ${}, you have ${} messages"  -> "Hello Edward, you have 3 messages"

  -> show_alert('success', ['Hello ${name}, you have ${count} messages', { name: 'Edward', count: 3 }], ['Hello ${}, you have ${} messages', ['Edward', 3 ]])
  */


  // Check if the key exists in the provided listLanguage
  //if not exist in the listLanguage, we will return the key
  let textTranslate=t(labelKey); 

  // if we already found the work success, return the meaning
  if (textTranslate !== labelKey) return applyKeys(textTranslate, keys);

  //now if not found the work in the dictionary global, we will see if can translate the word with help of all the dictionary that exist in memory
  for (const infoDictionary of allTheDictionary) {
    //if we found the work in a dictionary, break the loop and save the translate
    const possibleTranslation = infoDictionary.dictionary[textTranslate];
    if (possibleTranslation) {
      textTranslate = possibleTranslation;
      break; 
    }
  }

  return applyKeys(textTranslate, keys);
}

//this functions is for translate the menu of the apps, this function is called when the user load the web or change the language
function translate_menu_apps(){
  //get the list of the apps in the menu
  const menuApps = document.querySelectorAll('.app-name, .app-name-2');
  const searchApp=document.getElementById('searchInput'); //get the search input
  if (menuApps && searchApp){
    //update the placeholder of the search input
    searchApp.setAttribute('placeholder', LANG['menu.search'] || 'Search an app');

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
  else{
    //if not exist the menu of apps, is because the user is not logged in
    apply_translation_to_the_web(LANG);
  }
}