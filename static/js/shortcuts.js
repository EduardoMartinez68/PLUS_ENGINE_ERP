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
    filterApps(); // restaurar todas
}


function openMenu(){
  document.getElementById('appMenu').classList.remove('hidden');
  const input = document.getElementById('searchInput');
  if (input) {
    input.focus();
  }
  //sidebar.classList.add('open');
  //overlay.classList.add('active');
}

// Atajos de teclado
document.addEventListener('keydown', (e) => {
  const isMenuOpen = document.getElementById('appMenu').classList.contains('hidden');//navMenuShort.classList.contains('open');

  // Tecla ESC: cerrar menú si está abierto
  if (e.key === 'Escape') {
    if (!isMenuOpen) {
      e.preventDefault();
      closeMenu();
    }else{
      openMenu();
    }
  }

  // Ctrl + 1 para ir al home
  if (e.ctrlKey && e.key === '1') {
    window.location.href = '/';
  }

  // Ctrl + 2 para ir al módulo clientes
  if (e.ctrlKey && e.key === '2') {
    window.location.href = '/clientes';
  }

  // Ctrl + 3 para ir al módulo casos
  if (e.ctrlKey && e.key === '3') {
    window.location.href = '/casos';
  }

  // Agrega más si necesitas...
});
