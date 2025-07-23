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
      const pathTranslate= get_path_of_the_file_translate_of_the_app(url);
      load_language(pathTranslate);

      //update all the labels that the programmer do with the syntax of the ERP, to the labels that the user can see
      transform_my_labels_erp(); 


      closeMenu();
    } catch (error) {
      console.error('Error al cargar contenido:', error);
    }
  } else {
    console.error('URL inválida proporcionada a nextWeb');
  }
}

//her we will see if the user have links save in the cache
const lastPage = sessionHistory.length > 0 ? sessionHistory[sessionHistory.length - 1] : '/';

//if the user not is in tha last web, we will load the container
if (location.pathname !== lastPage) {
  nextWeb(lastPage);
}


function get_path_of_the_app(url){
  const firstSegment = '/' + url.split('/')[1];
  return firstSegment;
}


function get_path_of_the_file_translate_of_the_app(url){
  const basePathTranslate=get_path_of_the_app(url); //get the path of the app
  const language = lenguaceUser; //get the language of the user

  //if exit the path of the app we will load the translate.json
  if (basePathTranslate) { 
    const pathTranslate = `static${basePathTranslate.replace(/\/?$/, '/') }locale/${language}/translate.json`;
    console.log('Path translate:', pathTranslate);
    return pathTranslate;
  } else {
    console.error('No se pudo obtener el path base de la app.');
    return null;
  }
}