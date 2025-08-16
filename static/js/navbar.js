const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const openBtn = document.getElementById('openSidebarBtn');
const closeBtn = document.getElementById('closeSidebarBtn');

openBtn.addEventListener('click', () => {
  openMenu();
  //sidebar.classList.add('open');
  //overlay.classList.add('active');
});

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
async function nextWeb(url) {
  if (typeof url === 'string' && url.trim() !== '') {
    try {
      const response = await fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const html = await response.text();

      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      const mainContent = doc.getElementById('main-content');
      document.getElementById('main-content').innerHTML = mainContent ? mainContent.innerHTML : html;

      // remove the old dynamic scripts
      document.querySelectorAll('script[data-dynamic-script]').forEach(script => script.remove());


      // Add new scripts with for...of (allows using await if you want)
      const scripts = doc.querySelectorAll('script');
      for (const oldScript of scripts) {
        const newScript = document.createElement('script');
        newScript.setAttribute('data-dynamic-script', 'true');

        if (oldScript.src) {
          newScript.src = oldScript.src;
          newScript.async = false;
          // If you want to wait for the script to load:
          await new Promise(resolve => {
            newScript.onload = resolve;
            newScript.onerror = resolve;
          });
        } else {
          newScript.textContent = oldScript.textContent;
        }

        document.body.appendChild(newScript);
      }

      sessionHistory.push(url);
      localStorage.setItem('sessionHistory', JSON.stringify(sessionHistory));

      //translate the language of the app
      const pathTranslate = get_path_of_the_file_translate_of_the_app(url);
      load_language(pathTranslate);

      //update all the labels that the programmer do with the syntax of the ERP, to the labels that the user can see
      transform_my_labels_erp();

      closeMenu();
    } catch (error) {
      console.error('Error to load the container of the body:', error);
    }
  } else {
    console.error('Invalid URL provided to nextWeb');
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
    const pathTranslate = `static/${basePathTranslate}/locale/${language}/translate.json`;
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
Sortable.create(grid, {
  animation: 200,
  ghostClass: 'ghost',
  onEnd: saveAppOrder
});

// Cargar orden desde localStorage
loadAppOrder();


// Guarda el orden actual de las apps
function saveAppOrder() {
  const appItems = document.querySelectorAll('.app-container[data-id]');
  const order = Array.from(appItems).map(item => item.dataset.id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
}

// Carga el orden guardado
function loadAppOrder() {
  const savedOrder = JSON.parse(localStorage.getItem(STORAGE_KEY));
  if (!savedOrder) return;

  const grid = document.querySelector('.apps-grid');
  const itemsMap = {};

  document.querySelectorAll('.app-container[data-id]').forEach(item => {
    itemsMap[item.dataset.id] = item;
  });

  savedOrder.forEach(id => {
    if (itemsMap[id]) {
      grid.appendChild(itemsMap[id]);
    }
  });
}