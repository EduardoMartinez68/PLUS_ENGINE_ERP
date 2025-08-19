async function send_message_to_the_server(url, data = {}, with_load = true) {
    // show the overlay
    const screenLoad = document.getElementById('loadingOverlay')
    if (with_load) {
        screenLoad.style.display = 'flex';
    }


    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()  // Solo si usas Django
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            console.log(url)
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        return result;

    } catch (error) {
        console.log(url)
        console.error('Error al cargar datos:', error);
        return { success: false, error: error.message };

    } finally {
        screenLoad.style.display = 'none';
    }
}


// Función para obtener CSRF token (Django)
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const c = cookie.trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return '';
}

function formToJSON(form) {
    const data = {};
    const formData = new FormData(form);
    for (let [key, value] of formData.entries()) {
        if (data[key] !== undefined) { // Soporte campos múltiples
            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    return data;
}

async function send_form_to_the_server(formId, url) {
    const form = document.getElementById(formId);
    if (!form) {
        console.error('This form not exist:', formId);
        return;
    }

    const data = formToJSON(form);
    return await send_message_to_the_server(url, data)
}

//this function is for create a form that send the information to the server
//it will add an event listener to the form with the id 'id_form' for that the proggramer only add the if of the form and his id for get infrmation 
async function create_form_for_send_the_server(id_form, url) {
    document.getElementById(id_form).addEventListener('submit', async function (e) {
        e.preventDefault(); //this is for that the form not load the web

        //send the information to the server and get his answer
        const result = await send_form_to_the_server(id_form, url);

        //we will see if we can add the new customer
        if (result.success) {
            show_notification('success', result.message || 'Información guardada correctamente');
            //this.reset();
        } else {
            show_alert('alert', 'Error', result.message || 'No se pudo agregar al servidor.', (result.error || 'No se pudo guardar'))
        }
    });
}


