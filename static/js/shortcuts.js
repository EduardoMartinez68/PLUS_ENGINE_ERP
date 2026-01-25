const navMenuShort = document.getElementById('sidebar');

// Función para alternar menú
function toggleMenu() {
  navMenuShort.classList.toggle('open');
  overlay.classList.toggle('active');
}

// Función para cerrar menú
function closeMenu() {
  //sidebar.classList.remove('open');
  //overlay.classList.remove('active');
  document.getElementById('appMenu').classList.add('hidden');
  document.getElementById('searchInput').value = '';
  filterApps(); // restart all the apps
  window.closeModalApp();
}


function openMenu(){
  document.getElementById('appMenu').classList.remove('hidden');
  const input = document.getElementById('searchInput');
  if (input) {
    input.focus();
  }
  window.openModalApp();
  //sidebar.classList.add('open');
  //overlay.classList.add('active');
}

// Atajos de teclado
document.addEventListener('keydown', (e) => {
  const appMenu = document.getElementById("appMenu");
  const isMenuOpen = appMenu.querySelector(".menu").classList.contains("active");
  const navbar= document.getElementById("sideMenu").classList.contains("active")

  if (e.key === 'Escape') {
    if (isMenuOpen || navbar) {
      e.preventDefault();
      closeModalApp();
    }else{
      openModalApp();
    }
  }

});
