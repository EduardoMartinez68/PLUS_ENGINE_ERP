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
      // Parse the HTML
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Update main-content
      const mainContent = doc.getElementById('main-content');
      document.getElementById('main-content').innerHTML = mainContent ? mainContent.innerHTML : html;

      // Remove old dynamic scripts
      document.querySelectorAll('script[data-dynamic-script]').forEach(script => script.remove());

      // Add new scripts
      const scripts = doc.querySelectorAll('script');
      scripts.forEach(oldScript => {
        const newScript = document.createElement('script');
        newScript.setAttribute('data-dynamic-script', 'true'); // mark it

        if (oldScript.src) {
          newScript.src = oldScript.src;
          newScript.async = false;
        } else {
          newScript.textContent = oldScript.textContent;
        }

        document.body.appendChild(newScript);
      });

      // Save sessionHistory
      sessionHistory.push(url);
      localStorage.setItem('sessionHistory', JSON.stringify(sessionHistory));

      closeMenu();
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