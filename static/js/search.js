
function update_container_with_seeker(inputsId, fieldId, divHtml, searchUrl, delay = 500, type='tr') {
    /*
      inputsId=this is a array of all the inputs of filter fot search the objects. inputsId[0] is the id of the search input
      fieldId=the field that we will update
      searchUrl=the url where we will search the information of the table
      delay=the time that would like delay 
    */

    //first we will get the input that the user is using for write
    const inputId = Array.isArray(inputsId) ? inputsId[0] : inputsId;
    const input = document.getElementById(inputId);
    const field = document.getElementById(fieldId);

    //when this we will see if send a notification to the server for update the table
    let timer;
    let lastQuery = '';


    //now forever that the user is writing in the seeker, we will see if we need update the container of the table
    const triggerSearch = () => {
        const query = input.value.trim(); //get the value of the search

        //this function is for create a delay because if the user is writing
        clearTimeout(timer);
        timer = setTimeout(async () => {

             //if the input have a value different to his last search, this means that need send a notification to the server
            if (query !== lastQuery) {
                lastQuery = query;
                await send_information_to_the_server()
            }
        }, delay);
    };

    const send_information_to_the_server=async ()=>{
        const query = input.value.trim();

        //after that we send the information to the server, we will see if the user send more inputs for filter
        const allFilters = [query]; //we will save the first input that is the search input
        let data;

        if (Array.isArray(inputsId) && inputsId.length > 1) {
            for (let i = 1; i < inputsId.length; i++) {
                const additionalInput = document.getElementById(inputsId[i]); //get the additional filters if exist

                //we will see if the additional filters exist
                if (additionalInput) {
                    //get the value of the additional filters
                    const val = additionalInput.value.trim();
                    allFilters.push(val);
                }
            }

            //send a message to the server for get the answer
            data = await send_message_to_the_server(searchUrl, { allFilters }, false);
        } else {
            //send a message to the server for get the answer
            data = await send_message_to_the_server(searchUrl, { query }, false);
        }

        //we will see if the server can answer with the information or exist a error
        if (data.success) {
            field.innerHTML = ''; //clear the container

            //we will see if exist container for print in screen
            if (data.results && data.results.length > 0) {

                //if exist container, we will show in the field
                data.results.forEach(dataItem => {
                    //here we will get the card or table that need add to the field or table
                    const labelHtml = document.createElement(type);
                    labelHtml.innerHTML = renderTemplate(divHtml, dataItem); //now her create the container of the card or table
                    field.appendChild(labelHtml); //add the new card or row to the container
                });
            } else {
                //if exist an answer, we will show a message to the user
                field.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados</td></tr>';
            }
        } else {
            console.error('Error en la búsqueda:', data.message);
            show_alert('alert', 'Error', 'Error en la búsqueda desde el servidor. Inténtalo otra vez.', data.message);
            field.innerHTML = '<tr><td colspan="6" style="text-align:center;color:red;">Error en la búsqueda</td></tr>';
        }
    }


    //Listener for the main input (search)
    input.addEventListener('input', triggerSearch);

    //Add listeners to other filters (selects, dates, etc.)
    if (Array.isArray(inputsId) && inputsId.length > 1) {
        for (let i = 1; i < inputsId.length; i++) {
            const filterInput = document.getElementById(inputsId[i]);
            if (filterInput) {
                // Detect changes in selects and dates
                filterInput.addEventListener('change', send_information_to_the_server);
            }
        }
    }
}



//this function is for remplace the template with the data
// it will replace the {key} in the template with the value from data[key]
function renderTemplate(template, data) {
  return template.replace(/{\s*(\w+)\s*}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : '';
  });
}