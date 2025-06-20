async function send_message_to_the_server(url, data = {}) {
    // Mostrar overlay
    const screenLoad=document.getElementById('loadingOverlay')
    screenLoad.style.display = 'flex';
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
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        return result;

    } catch (error) {
        console.error('Error al cargar datos:', error);
        return { success: false, error: error.message };

    } finally {
        // Ocultar overlay
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
    return await send_message_to_the_server(url,data)
}




send_message_to_the_server();