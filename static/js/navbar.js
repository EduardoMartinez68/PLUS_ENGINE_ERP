const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const openBtn = document.getElementById('openSidebarBtn');
const closeBtn = document.getElementById('closeSidebarBtn');

openBtn.addEventListener('click', () => {
  openMenu();
  //sidebar.classList.add('open');
  //overlay.classList.add('active');
});

closeBtn.addEventListener('click', () => {
  closeMenu();
  //sidebar.classList.remove('open');
  //overlay.classList.remove('active');
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

function nextWeb(url){
  if (typeof url === 'string' && url.trim() !== '') {
    window.location.href = url;
  } else {
    console.error('URL inválida proporcionada a nextWeb');
  }
}