const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');

overlay.addEventListener('click', () => {
  sidebar.classList.remove('open');
  overlay.classList.remove('active');
  closeMenu()
});

function filterApps() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  const apps = document.querySelectorAll('.app-container');

  apps.forEach(app => {
    const name = app.querySelector('.app-name').textContent.toLowerCase();
    app.style.display = name.includes(query) ? 'flex' : 'none';
  });
}


//this is for save the history that the user visit after
let sessionHistory = JSON.parse(localStorage.getItem('sessionHistory')) || [];

//this function is for load the web that need
async function load_html_in_the_container(container, html){
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  //her we will update the DOM
  const mainContent = doc.getElementById(container);
  document.getElementById(container).innerHTML = mainContent ? mainContent.innerHTML : html;

  //this is for load the script of the view
  const scripts = doc.querySelectorAll("script");
  scripts.forEach(oldScript => {
    const newScript = document.createElement("script");
    if (oldScript.src) {
      newScript.src = oldScript.src; // scripts external
    } else {
      newScript.textContent = oldScript.textContent; // scripts inline
    }
    document.body.appendChild(newScript);
  });

  //update all the labels that the programmer do with the syntax of the ERP, to the labels that the user can see
  let sessionHistory = JSON.parse(localStorage.getItem('sessionHistory')) || [];
  let lastUrl = sessionHistory[sessionHistory.length - 1];
  transform_my_labels_erp();
  const pathTranslate = get_path_of_the_file_translate_of_the_app(url);
  await load_language(pathTranslate);
}

async function nextWeb(url) {
  if (typeof url !== 'string' || !url.trim()) {
    console.error('Invalid URL provided to nextWeb');
    return;
  }

  //first we will see if the app in the that was the user is the app of calendary 
  //if it the app of calendary we will to refresh the UI 
  // 👇 get last web
  const lastPage = sessionHistory.length > 0 ? sessionHistory[sessionHistory.length - 1] : '/';

  //reset the functions and variable globals for can load the news functions
  Plus.Functions.reset();
  Plus.variables.reset();


  try {
    const pathTranslate = get_path_of_the_file_translate_of_the_app(url);
    await load_language(pathTranslate);

    const response = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const html = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // =========================
    // 🔥 CSS DINÁMICO INTELIGENTE
    // =========================

    const newStyles = Array.from(doc.querySelectorAll('style, link[rel="stylesheet"]'));

    // Obtener estilos actuales dinámicos
    const currentStyles = Array.from(document.querySelectorAll('[data-dynamic-style]'));

    // Crear mapa de estilos nuevos (para evitar duplicados)
    const newStyleKeys = new Set(
      newStyles.map(s => s.tagName === 'LINK' ? s.href : s.textContent)
    );

    // 🧹 Eliminar solo los que ya no existen
    currentStyles.forEach(style => {
      const key = style.tagName === 'LINK' ? style.href : style.textContent;
      if (!newStyleKeys.has(key)) {
        style.remove();
      }
    });

    // ➕ Agregar nuevos estilos (solo si no existen)
    for (const oldStyle of newStyles) {

      let exists = false;

      if (oldStyle.tagName === 'LINK') {
        exists = document.querySelector(`link[href="${oldStyle.href}"]`);
      } else {
        exists = Array.from(document.querySelectorAll('style'))
          .some(s => s.textContent === oldStyle.textContent);
      }

      if (exists) continue;

      let newStyle;

      if (oldStyle.tagName === 'LINK') {
        newStyle = document.createElement('link');
        newStyle.rel = 'stylesheet';
        newStyle.href = oldStyle.href;

        // 🔥 esperar a que cargue
        await new Promise(resolve => {
          newStyle.onload = resolve;
          newStyle.onerror = resolve;
          document.head.appendChild(newStyle);
        });

      } else {
        newStyle = document.createElement('style');
        newStyle.textContent = oldStyle.textContent;
        document.head.appendChild(newStyle);
      }

      newStyle.setAttribute('data-dynamic-style', 'true');
    }

    // =========================
    // 🔥 HTML
    // =========================

    const mainContent = doc.getElementById('main-content');
    document.getElementById('main-content').innerHTML =
      mainContent ? mainContent.innerHTML : html;

    // =========================
    // 🔥 JS DINÁMICO
    // =========================

    document.querySelectorAll('script[data-dynamic-script]')
      .forEach(script => script.remove());

    const scripts = doc.querySelectorAll('script');

    for (const oldScript of scripts) {
      const newScript = document.createElement('script');
      newScript.setAttribute('data-dynamic-script', 'true');

      if (oldScript.src) {
        newScript.src = oldScript.src;
        newScript.async = false;

        await new Promise(resolve => {
          newScript.onload = resolve;
          newScript.onerror = resolve;
        });

      } else {
        newScript.textContent = oldScript.textContent;
      }

      document.body.appendChild(newScript);
    }

    // =========================
    // 🔥 FINAL
    // =========================

    sessionHistory.push(url);
    localStorage.setItem('sessionHistory', JSON.stringify(sessionHistory));

    transform_my_labels_erp();
    await load_language(pathTranslate);

    closeMenu();

    // 👇 only if the user outside of the app of agenda we will to refresh the UI
    if (url!=='/agenda/agenda' && lastPage === '/agenda/agenda') {
      sessionHistory.push(url);
      window.location.reload();
      return;
    }
  } catch (error) {
    console.error('Error to load the container of the body:', error);
  }
}

//her we will see if the user have links save in the cache
const lastPage = sessionHistory.length > 0 ? sessionHistory[sessionHistory.length - 1] : '/';

//if the user not is in tha last web, we will load the container
if (location.pathname !== lastPage) {
  nextWeb(lastPage);
}


function get_path_of_the_app(url) {
  const parts = url.replace(/^\/+|\/+$/g, '').split('/');
  return parts[0] || '';
}

function get_path_of_the_file_translate_of_the_app(url) {
  const basePathTranslate = get_path_of_the_app(url); //get the path of the app
  const language = languageUser; //get the language of the user

  //if exit the path of the app we will load the translate.json
  if (basePathTranslate) {
    const pathTranslate = `static/${basePathTranslate}/config/locale/${language}/translate.json`;
    return pathTranslate;
  } else {
    console.error('Not able to obtain the base path of the app.');
    return null;
  }
}


/*--------------THIS SCRIPT IS FOR THAT THE USER CAN MOVE THE APPS WITH A EFECT WITH IF WAS APPS OF CELLPHONE*/
const STORAGE_KEY = 'customAppOrder';


const grid = document.querySelector('.apps-grid');

// Inicializar Sortable
/*
Sortable.create(grid, {
  animation: 200,
  ghostClass: 'ghost',
  filter: '.btn',
  onEnd: saveAppOrder
});
*/
//load the order of all the apps from localStorage
loadAppOrder();


// save the order of all the apps
function saveAppOrder() {
  const appItems = document.querySelectorAll('.plus-app-container[data-id]');
  const order = Array.from(appItems).map(item => item.dataset.id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
}

//load the order from localStorage
function loadAppOrder() {
  const savedOrder = JSON.parse(localStorage.getItem(STORAGE_KEY));
  if (!savedOrder) return;

  const grid = document.querySelector('.apps-grid');
  const itemsMap = {};

  //Map all elements with data-id
  document.querySelectorAll('.plus-app-container[data-id]').forEach(item => {
    itemsMap[item.dataset.id] = item;
  });

  //First we add all the apps according to the saved order
  savedOrder.forEach(id => {
    // Ignoramos el botón de salida aquí
    if (id !== 'app-plus-exit' && itemsMap[id]) {
      grid.appendChild(itemsMap[id]);
    }
  });

  //Finally, always add the exit button at the end.
  const exitForm = document.querySelector('.form-app-exit');
  if (exitForm) grid.appendChild(exitForm);
}