async function send_message_to_the_server(url, data = {}, with_load = true, method = 'POST') {
  // show the overlay
  const screenLoad = document.getElementById('loadingOverlay')
  if (with_load) {
    screenLoad.style.display = 'flex';
  }


  try {
    //here we will to create a fetchOptions for send the information to the server Django
    let fetchOptions = {
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    };

    //now we will see the fetch options. If the type is POST we will add the body
    //else we will to create the new link
    let fetchUrl = url;
    if (method.toUpperCase() === 'POST') {
      fetchOptions.body = JSON.stringify(data);
    } else if (method.toUpperCase() === 'GET') {
      // Convert the 'data' object to query params
      const queryParams = new URLSearchParams(data).toString();
      if (queryParams) {
        fetchUrl += (url.includes('?') ? '&' : '?') + queryParams;
      }
    }


    //send the information to the server with the fetch options
    const response = await fetch(fetchUrl, fetchOptions);

    //first we will see if the response is ok
    if (!response.ok) {
      console.log(url)
      console.log(response)
      //now we will to show the error that send of server and show the information of error that answer the server
      show_alert('alert', response.status, 'Error to load visit the link ' + url, (response.error || response))
      return { success: false, error: 'Error to load visit the link \n' + (response.error || '') + ' \n status: ' + (response.status || '') };
    }

    //get the information that send the server and the return 
    const answer = await response.json();
    return answer;

  } catch (error) {
    console.error(url)
    console.error('Error to load the data:', error);
    return { success: false, error: error };
  } finally {
    screenLoad.style.display = 'none';
  }
}


// Function to get CSRF token (Django)
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
    if (data[key] !== undefined) { //this is for save multi inputs
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

//this function is for restart the information of the form when for that the proggramer can restart his form most speed
//this function can be run after of that the form was send to the server with a message of success
// Reinicia todos los plus-select dentro de un formulario
function restart_form(formId) {
  //get the form with his id
  const form = document.getElementById(formId);
  if (!form) return;
  form.reset(); //restart all the input of the form

  // get all the labels PlusPriority that exist in the form 
  const plusPriorityElements = form.querySelectorAll("plus-priority");

  plusPriorityElements.forEach(el => {
    if (typeof el.setValue === "function") {
      el.setValue(0); // restart all the start
    }
  });

  //restart all the select. Here need restart the select that have options #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  const plusSelects = form.querySelectorAll("plus-select");
  plusSelects.forEach(el => {
    if (typeof el.reset === "function") {
      el.reset();
    }
  });

  const plusSwitchElements = form.querySelectorAll("plus-switch");
  plusSwitchElements.forEach(el => {
    const defaultChecked = el.getAttribute('checked');
    const isChecked = defaultChecked === "True" || defaultChecked === "true" || defaultChecked === "1";
    const checkbox = el.querySelector('input[type="checkbox"]');
    if (checkbox && typeof el.setChecked === 'function') {
      el.setChecked(isChecked);
    }
  });

  // ===== restart all the PlusDate =====
  form.querySelectorAll("plus-date").forEach(el => {
    const defaultValue = el.getAttribute('value'); // default value
    const newDate = defaultValue ? new Date(defaultValue) : null;
    change_plus_date(el.id, newDate ? newDate.toISOString().split('T')[0] : '');
  });

  // ===== restart all the PlusTime =====
  form.querySelectorAll("plus-time").forEach(el => {
    const defaultValue = el.getAttribute('value') || "12:00"; // default time
    change_plus_time(el.id, defaultValue);
  });

  // restart elementos <input-color>
  form.querySelectorAll('input-color').forEach(el => {
    const initialValue = el.getAttribute('value') || '#3b82f6';
    el.updateColor?.(initialValue); //use updateColor method if it exists
  });

  //  PlusTag 
  const plusTags = form.querySelector("plus-tags");
  if (plusTags && typeof plusTags.resetTags === "function") {
    plusTags.resetTags();
  }

  // ===== restart all the ImageUploader =====
  form.querySelectorAll("image-uploader").forEach(el => {
    // clear the container of the images
    const shadow = el.shadowRoot;
    if (!shadow) return;
    const container = shadow.querySelector(".uploader-container");
    const addButton = shadow.querySelector(".add-button");

    if (container && addButton) {
      // delete all the .image-box except the button 
      container.querySelectorAll(".image-box").forEach(box => box.remove());
      addButton.style.display = "flex"; // show the button for add a image
    }

    //delete the inputs hidden in the form
    form.querySelectorAll(`input[name^='${el.getAttribute("name") || "image"}']`).forEach(input => input.remove());

    // reload initial images from attributes value-1, value-2...
    const maxImages = parseInt(el.getAttribute("max")) || 1;
    for (let i = 1; i <= maxImages; i++) {
      const url = el.getAttribute(`value-${i}`);
      if (url && url !== "None" && url.trim() !== "") {
        // We reuse the internal function of each image-uploader
        if (typeof el.addImageFromUrl === "function") {
          el.addImageFromUrl(url, i);
        }
      }
    }
  });
}

function valid_all_the_inputs_of_the_form(form) {
    const inputs = form.querySelectorAll('input'); //get all the inputs of the form
    let isValid = true;
    let errors = [];

    inputs.forEach(input => {
        const valor = input.value.trim();
        const nombre = input.getAttribute('name');

        // 1. we will see if the input not is empty and is requested
        if (input.hasAttribute('required') && valor === "") {
            isValid = false;
            errors.push(`El campo ${nombre} es obligatorio.`);
            input.style.border = "2px solid red";
        }

        // 3. Check maximum length (Example: 5 characters)
        const max = input.getAttribute('maxlength');
        if (max && valor.length > parseInt(max)) {
            isValid = false;
            errors.push(`El campo ${nombre} no puede tener más de ${max} caracteres.`);
        }

        // 4. Check if it is a number type and contains invalid characters
        if (input.type === 'number') {
            // The value of an input number is "" if it contains letters in some browsers
            if (isNaN(valor) || valor === "") {
                isValid = false;
                errors.push(`El campo ${nombre} debe ser un número válido.`);
            }
        }
    });

    return {success: isValid, errors: errors};
}

async function send_form_to_the_server(formId, url) {
  const form = document.getElementById(formId);
  if (!form) {
    show_alert('alert', 'Error', 'info.error.this-form-not-exit', 'This form not exist in the Doom: ' + formId)
    return;
  }

  //first we will see if the data of the form are valid 
  const vForm=valid_all_the_inputs_of_the_form(form);
  if(vForm.success){
    const data = formToJSON(form);
    return await send_message_to_the_server(url, data);
  }

  //else if the user not finish all the input that be required, we will to show a message of advertence 
  return { success: false, error: vForm.errors };
}

//this function is for create a form that send the information to the server
//it will add an event listener to the form with the id 'id_form' for that the proggramer only add the if of the form and his id for get infrmation 
async function create_form_for_send_the_server(id_form, url, restart = true) {
  document.getElementById(id_form).addEventListener('submit', async function (e) {
    e.preventDefault(); //this is for that the form not load the web

    //send the information to the server and get his answer
    const result = await send_form_to_the_server(id_form, url);

    //we will see if we can add the new customer
    if (result.success) {
      show_notification('success', result.message || 'info.info-send-with-success');

      if (restart) {
        restart_form(id_form);
      }
    } else {
      show_alert('alert', 'Error', result.message || 'info.not-was-can-send-the-information', (result.error || 'info.not-was-can-send-the-information'))
    }
  });
}

//this function is for update the container that exist in the UI. This is for load information that send the backend while be a animation of load in the UI
async function update_load_container(container_id, link, urlImageFail = null) {
  const containerLoad = document.getElementById(container_id);

  try {
    const backend = await send_message_to_the_server(link, {}, false, 'GET');

    if (backend.success) {
      const html = backend.answer;

      // Parse HTML
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Update container content
      const mainContent = doc.getElementById(container_id);
      containerLoad.innerHTML = mainContent ? mainContent.innerHTML : html;

      //this is for load the script of the view
      const scripts = doc.querySelectorAll("script");
      scripts.forEach(oldScript => {
        const newScript = document.createElement("script");
        if (oldScript.src) {
          newScript.src = oldScript.src; // scripts external
        } else {
          newScript.textContent = oldScript.textContent; // scripts inline
        }
        document.body.appendChild(newScript);
      });

      // Transform labels
      let sessionHistory = JSON.parse(localStorage.getItem('sessionHistory')) || [];
      let lastUrl = sessionHistory[sessionHistory.length - 1];
      transform_my_labels_erp();
      const pathTranslate = get_path_of_the_file_translate_of_the_app(link);
      await load_language(pathTranslate);

    } else {
      // Show error message
      const imageSrc = urlImageFail || 'https://via.placeholder.com/150?text=404';
      containerLoad.innerHTML = `
                    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%;">
                        <img src="${imageSrc}" alt="Error 404" style="max-width:200px; margin-bottom:20px;">
                        <p style="text-align:center; font-size:18px; color:#555;">No can load the container. Error 404</p>
                    </div>
                `;
    }

  } catch (error) {
    console.error("Error al cargar el contenedor:", error);
    const imageSrc = urlImageFail || 'https://via.placeholder.com/150?text=404';
    containerLoad.innerHTML = `
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%;">
                    <img src="${imageSrc}" alt="Error 404" style="max-width:200px; margin-bottom:20px;">
                    <p style="text-align:center; font-size:18px; color:#555;">Error to insert the container</p>
                </div>
            `;
  }
}
