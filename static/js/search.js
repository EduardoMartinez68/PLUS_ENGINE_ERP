
function show_loader_in_the_div_container_of_plus(contenedorId, loadingImage) {
    const contenedor = document.getElementById(contenedorId);
    contenedor.innerHTML = `
    <style>
        .loader img {
            width: 80px;
            height: auto;
            opacity: 0.95;
        }

        .progress-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: #f0f0f0;
            overflow: hidden;
        }

        .progress-bar span {
            display: block;
            width: 30%;
            height: 100%;
            background: #075EAB;
            animation: move 1.2s infinite linear;
        }

        @keyframes move {
            from { margin-left: -30%; }
            to { margin-left: 100%; }
        }
    </style>

    <div class="loader">
    </div>
    <div class="progress-bar"><span></span></div>
    `;
}

function hidden_loader_in_the_div_container_of_plus(contenedorId, contenido) {
    const contenedor = document.getElementById(contenedorId);
    contenedor.innerHTML = contenido;
}

function update_container_with_seeker(inputsId, fieldId, divHtml, searchUrl, method='POST', loadingImage=null, delay = 500, type='tr') {
    /*
      inputsId=this is a array of all the inputs of filter fot search the objects. inputsId[0] is the id of the search input
      fieldId=the field that we will update
      searchUrl=the url where we will search the information of the table
      delay=the time that would like delay 
    */

    //first we will get the input that the user is using for write
    const inputId = Array.isArray(inputsId) ? inputsId[0] : inputsId;
    let input = document.getElementById(inputId);
    const field = document.getElementById(fieldId);
    //const EMPTY_IMAGE_URL = "{% static 'img/info/empty.webp' %}";
    const EMPTY_IMAGE_URL=window.STATIC_URLS.emptyImage;

    //here we will see if the input exist in the UI, if not exist we will to wait 1 second and we will try again
    if (!input) {
        setTimeout(() => {
            update_container_with_seeker(inputsId, fieldId, divHtml, searchUrl, method, loadingImage, delay, type);
        }, 250);
        return; // stop execution here until re-entered
    }

    //when this we will see if send a notification to the server for update the table
    let timer;
    let lastQuery = '';

    //now forever that the user is writing in the seeker, we will see if we need update the container of the table
    const triggerSearch = async()  => {
        const query = input.value.trim(); //get the value of the search
        //this function is for create a delay because if the user is writing
        clearTimeout(timer);
        timer = setTimeout(async () => {

             //if the input have a value different to his last search, this means that need send a notification to the server
            if (query !== lastQuery) {
                lastQuery = query;
                show_loader_in_the_div_container_of_plus(fieldId);
                await send_information_to_the_server()
            }
        }, delay);
    };

    function get_the_value_of_the_input(input){
        //here we will see if the input is a select of plus or a select html normal
        if (input.tagName.toLowerCase() === 'plus-select') {
            return input.getValue();
        } 

        if (input.tagName.toLowerCase() === 'plus-switch') {
            return window.get_status_plus_switch(input)
        } 

        if (input.tagName.toLowerCase() === 'plus-date') {
            return input.value.trim();
        } 

        if (input.tagName.toLowerCase() === 'plus-time') {
            return input.value.trim();
        } 


        return input.value.trim();
    }

    const send_information_to_the_server=async ()=>{
        const query = input.value.trim() || '';

        //after that we send the information to the server, we will see if the user send more inputs for filter
        const allFilters = [query]; //we will save the first input that is the search input
        let data;

        if (Array.isArray(inputsId) && inputsId.length > 1) {
            for (let i = 1; i < inputsId.length; i++) {
                const additionalInput = document.getElementById(inputsId[i]); //get the additional filters if exist

                //we will see if the additional filters exist
                if (additionalInput) {
                    //get the value of the additional filters
                    const val = get_the_value_of_the_input(additionalInput)
                    allFilters.push(val);
                }
            }

            //send a message to the server for get the answer
            data = await window.send_message_to_the_server(searchUrl, { allFilters }, false, method);
        } else {
            //send a message to the server for get the answer
            data = await window.send_message_to_the_server(searchUrl, { query }, false, method);
        }

        //when the server send a answer, we will to hidden the load in the div 
        hidden_loader_in_the_div_container_of_plus(fieldId)

        //we will see if the server can answer with the information or exist a error
        field.innerHTML = ''; //clear the container
        if (data.success) {
            //we will see if exist container for print in screen
            if (data.answer && data.answer.length > 0) {
                //if exist container, we will show in the field
                data.answer.forEach(dataItem => {
                    //here we will get the card or table that need add to the field or table
                    const labelHtml = document.createElement(type);
                    labelHtml.innerHTML = renderTemplate(divHtml, dataItem); //now her create the container of the card or table
                    field.appendChild(labelHtml); //add the new card or row to the container
                });
            } else {
                //if exist an answer, we will show a message to the user
                const answer=t("info.no_results");
                if(loadingImage===null){
                    field.innerHTML = `
                    <div class='full-center' style="width: 100%; height: 100%;">
                            <b>${answer}<b>
                    </div>`;
                }else if(loadingImage===true){
                    field.innerHTML = `
                    <div class='full-center' style="width: 100%; height: 100%;">
                            <img src="${EMPTY_IMAGE_URL}" alt="empty" style="width: 50%; height: auto;"/><br>
                            <b>${answer}<b>
                    </div>`;
                }else{
                    field.innerHTML = `
                    <div class='full-center'>
                        <center>
                            <img src="${loadingImage}" alt="Loading..." style="width: 100%; height: auto;"/>
                            ${answer}
                        </center>
                    </div>`;
                }
            }
        } else {
            //here is when the server answer with a error and not can get nothing information
            const answer=t("message.error.server");
            show_alert('alert', 'Error', `${answer}`, `Error in the search ${searchUrl}: ${data.error}`);

            if(loadingImage===null){
            field.innerHTML = `
                <div class='full-center'>
                    ${answer}
                </div>`;
            }else{
            field.innerHTML = `
                <div class='full-center'>
                    <img src="${loadingImage}" alt="Loading..." style="width: 100%; height: auto;"/>
                    ${answer}
                </div>`;
            }
        }

        translate_dynamic_content(field); //translate the dynamic content of the field
    }


    //Listener for the main input (search)
    if (!input.dataset.initialized) {
        input.addEventListener('input', triggerSearch);
        input.dataset.initialized = "true"; //here we activate the input for that not have other event
    }

    //Add listeners to other filters (selects, dates, etc.)
    if (Array.isArray(inputsId) && inputsId.length > 1) {
        for (let i = 1; i < inputsId.length; i++) {
            const filterInput = document.getElementById(inputsId[i]);
            if (filterInput && !filterInput.dataset.initialized) {
                
                // If it's a PlusSelect, listen for the 'change' event on the element itself
                if (filterInput.tagName.toLowerCase() === 'plus-select') {
                    filterInput.addEventListener('change', send_information_to_the_server);
                } else {
                    //this is for other label of html
                    filterInput.addEventListener('change', send_information_to_the_server);
                }
                
                filterInput.dataset.initialized = "true";
            }
        }
    }



    //this script is for load all the information of the server when the input be visible for the user 
    //this is for when the input and his div container be visible for the user, update the container to the information
    //most new of the 
    const observer = new IntersectionObserver(async (entries, obs) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {                
                show_loader_in_the_div_container_of_plus(fieldId, loadingImage);
                await send_information_to_the_server()
                obs.unobserve(entry.target); //this is for only run once 
            }
        }
    }, {
        root: null,      // viewport
        threshold: 0.1   // al menos 10% visible
    });

    if (input) {
        observer.observe(input);
    }
}

function update_container_from_the_server(inputsId, fieldId, divHtml, searchUrl, method = 'POST', delay = 100, type = 'tr') {
    /*
      inputsId: array de todos los inputs de filtro (usamos solo el primero como búsqueda)
      fieldId: id del contenedor que se actualizará
      divHtml: template HTML para cada item
      searchUrl: URL del backend para buscar la información
      method: método HTTP (POST o GET)
      delay: tiempo de espera antes de enviar la solicitud
      type: tipo de elemento a crear ('tr', 'div', etc.)
    */

    const inputId = Array.isArray(inputsId) ? inputsId[0] : inputsId;
    const input = document.getElementById(inputId);
    const field = document.getElementById(fieldId);

    if (!input || !field) return;

    // Comprueba si el contenedor es visible
    const isVisible = field.offsetParent !== null;
    if (!isVisible) return;

    // Función para obtener valores de inputs (igual que en tu otra función)
    function get_the_value_of_the_input(input) {
        if (input.tagName.toLowerCase() === 'plus-select') return input.getValue();
        if (input.tagName.toLowerCase() === 'plus-switch') return window.get_status_plus_switch(input);
        if (input.tagName.toLowerCase() === 'plus-date') return input.value.trim();
        if (input.tagName.toLowerCase() === 'plus-time') return input.value.trim();
        return input.value.trim();
    }

    // Función principal para enviar datos al servidor
    const send_information_to_the_server = async () => {
        show_loader_in_the_div_container_of_plus(fieldId);

        const query = input.value.trim();
        const allFilters = [query];

        if (Array.isArray(inputsId) && inputsId.length > 1) {
            for (let i = 1; i < inputsId.length; i++) {
                const additionalInput = document.getElementById(inputsId[i]);
                if (additionalInput) allFilters.push(get_the_value_of_the_input(additionalInput));
            }
        }

        const data = Array.isArray(inputsId) && inputsId.length > 1 
            ? await window.send_message_to_the_server(searchUrl, { allFilters }, false, method)
            : await window.send_message_to_the_server(searchUrl, { query }, false, method);

        //when the server send a answer, we will to hidden the load in the div 
        hidden_loader_in_the_div_container_of_plus(fieldId)

        if (data.success) {
            field.innerHTML = '';
            if (data.answer && data.answer.length > 0) {
                data.answer.forEach(item => {
                    const el = document.createElement(type);
                    el.innerHTML = renderTemplate(divHtml, item);
                    field.appendChild(el);
                });
            } else {
                const answer = t("info.no_results");
                field.innerHTML = `<tr><td colspan="6" style="text-align:center;">${answer}</td></tr>`;
            }
        } else {
            const answer = t("info.no_results");
            show_alert('alert', 'Error', answer, data.message);
            field.innerHTML = `<tr><td colspan="6" style="text-align:center;">${answer}</td></tr>`;
        }

        translate_dynamic_content(field);
    };

    // Solo ejecuta la actualización después del delay
    setTimeout(send_information_to_the_server, delay);
}

function refresh_container_from_the_server(inputsId, fieldId, divHtml, searchUrl, method = 'POST', delay = 100, type = 'tr') {
    update_container_from_the_server(inputsId, fieldId, divHtml, searchUrl, method, delay, type);
}


//this function is for remplace the template with the data
// it will replace the {key} in the template with the value from data[key]
function renderTemplate(template, data) {
  return template.replace(/{\s*(\w+)\s*}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : '';
  });
}