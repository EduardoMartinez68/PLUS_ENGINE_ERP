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
function nextWeb(url) {
  if (typeof url === 'string' && url.trim() !== '') {
    fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      return response.text();
    })
    .then(html => {
      //update the container of the web like if was SAP
      document.getElementById('main-content').innerHTML = html; 

      //save the last link that the user visit for after load the web if the user loaded the web
      sessionHistory.push(url);
      localStorage.setItem('sessionHistory', JSON.stringify(sessionHistory));
      closeMenu(); //close the menu of apps
    })
    .catch(error => {
      console.error('Error al cargar contenido:', error);
    });
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