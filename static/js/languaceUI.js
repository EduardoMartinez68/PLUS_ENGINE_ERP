//Here we will see what language the user has on his/her computer.
const userLang = navigator.language || navigator.userLanguage;
const langCode = userLang.split('-')[0];

// Short month names for Spanish, English and Polish
  const shortMonths = {
    en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    pl: ['sty', 'lut', 'mar', 'kwi', 'maj', 'cze', 'lip', 'sie', 'wrz', 'paź', 'lis', 'gru'],
    es: ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
  };

// Short button names for Spanish, English and Polish
  const shortButtons = {
    en: ['Accept','Cancel', 'Create', 'Edit', 'Delete', 'View','Not exist'],
    pl: ['Akceptuj', 'Anuluj', 'Utwórz', 'Edytuj', 'Usuń', 'Pokaż','Not exist'],
    es: ['Aceptar','Cancelar', 'Crear', 'Editar', 'Eliminar', 'Ver','No existen resultados...']
  };

// Format a date string 'YYYY-MM-DD' to 'DD/mmm/YYYY' based on language
function format_date(dateISO, lang = 'en') {
  if (!dateISO) return '';
  const dateObj = new Date(dateISO);
  if (isNaN(dateObj)) return dateISO; // fallback if invalid date

  const day = String(dateObj.getDate()).padStart(2, '0');
  const month = shortMonths[langCode][dateObj.getMonth()];
  const year = dateObj.getFullYear();

  return `${day}/${month}/${year}`;
}


  /*status*/
 const statusTexts = {
    en: {
      1: "Paid",
      2: "Processing",
      3: "Canceled"
    },
    es: {
      1: "Pagado",
      2: "En proceso",
      3: "Cancelada"
    },
    pl: {
      1: "Zapłacono",
      2: "W trakcie",
      3: "Anulowano"
    }
  };

  // function for add to the class to the CSS with the status
  function getStatusClass(status) {
    switch(status) {
      case 1: return 'status-paid';
      case 2: return 'status-processing';
      case 3: return 'status-canceled';
      default: return '';
    }
  }



function format_date_to_text(dateString, type=1, locale = 'es-ES') {
    // Convertir la cadena ISO a objeto Date
    const date = new Date(dateString);

    if(type==1){
      // Configuración del formateador
      const optionsDate = {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
      };

      const optionsTime = {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
      };

      // Crear los formateadores para fecha y hora
      const formatterDate = new Intl.DateTimeFormat(locale, optionsDate);
      const formatterTime = new Intl.DateTimeFormat(locale, optionsTime);

      // Retornar el resultado como texto
      return `${formatterDate.format(date)} a las ${formatterTime.format(date)}`;
    }
    else{
        // Formato corto: 05/09/2025 15:00
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Mes empieza en 0
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${day}/${month}/${year} ${hours}:${minutes}`;
    } 
}