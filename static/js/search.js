function update_table_with_seeker(inputId, tableId, columns, searchUrl, delay = 500) {
    /**
      inputId=the id of the search input
      tableId=the table that we will update
      columns=the name of the columns with which we save the database. must be the same amount of col as the table
      searchUrl=the url where we will search the information of the table
      delay=the time that would like delay 
     */


    //first we will get the input that the user is using for write
    const input = document.getElementById(inputId);
    const tableBody = document.querySelector(`#${tableId} tbody`); //get the tabla of the UI

    //when this we will see if send a notification to the server for update the tabla
    let timer;
    let lastQuery = '';

    //now forever that the user is writing in the seeker, we will see if we need update the container of the table
    input.addEventListener('input', function () {
        //get the value of the search
        const query = input.value.trim();

        //this function is for create a delate because if the user is writing 
        clearTimeout(timer);
        timer = setTimeout(async () => {

            //if the input have a value different to his last search, this means that need send a notification to the server
            if (query !== lastQuery) {
                lastQuery = query;

                //send a message to the server for get the answer 
                const data = await send_message_to_the_server(searchUrl, { query }, false)

                //we will see if the server can answer with the information or exist a error
                if (data.success) {
                    //clear the table
                    tableBody.innerHTML = '';

                    //we will see if exist container for print in screen
                    if (data.results && data.results.length > 0) {

                        //if exist container, we will show in the table
                        data.results.forEach(dataFromTheServer => {
                            const row = document.createElement('tr');
                            /*
                            her we will create all the cell that the programmer would like show
                            the server sent us data, and with help of the variable columns we will can get the data
                            what would like in screen. 
                            */
                            columns.forEach(col => {
                                //we will read all the col that woudl like show, and get the information from the
                                //list that the server send
                                const td = document.createElement('td');
                                td.textContent = dataFromTheServer[col] || '';
                                row.appendChild(td);
                            });


                            //now her create other row for if the programmer would like add button for edit
                            const actionTd = document.createElement('td');
                            actionTd.innerHTML = `
                                <button class="btn btn-edit">
                                    <i class="fi fi-sr-pencil"></i>
                                </button>
                            `;

                            //add the button of edit
                            row.appendChild(actionTd);

                            //add the container to the table
                            tableBody.appendChild(row);
                        });
                    } else {
                        //if exist an answer, we will show a message to the user
                        tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados</td></tr>';
                    }
                }
                else {
                    console.error('Error en la búsqueda:', data.message);
                    show_alert('alert', 'Error', 'Error en la búsqueda desde el servidor. Intentalo otra vez.', data.message)
                    tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:red;">Error en la búsqueda</td></tr>';
                }

            }
        }, delay);
    });
}

function update_field_with_seeker(inputsId, fieldId, divHtml, searchUrl, delay = 500) {
    /**
      inputsId=this is a array of all the inputs of filter fot search the objects. inputsId[0] is the id of the search input
      fieldId=the field that we will update
      searchUrl=the url where we will search the information of the table
      delay=the time that would like delay 
     */

    //first we will get the input that the user is using for write
    const inputId = Array.isArray(inputsId) ? inputsId[0] : inputsId; //her we will see if the user send a array or a string
    const input = document.getElementById(inputId);
    const field = document.getElementById(fieldId);

    //when this we will see if send a notification to the server for update the tabla
    let timer;
    let lastQuery = '';

    //now forever that the user is writing in the seeker, we will see if we need update the container of the table
    input.addEventListener('input', function () {
        //get the value of the search
        const query = input.value.trim();

        //this function is for create a delate because if the user is writing 
        clearTimeout(timer);
        timer = setTimeout(async () => {

            //if the input have a value different to his last search, this means that need send a notification to the server
            if (query !== lastQuery) {
                lastQuery = query;

                //after that we send the information to the server, we will see if the user send more inputs for filter
                const allFilters=[query]; //we will save the first input that is the search input
                let data;

                if (Array.isArray(inputsId) && inputsId.length > 1) {
                    for (let i = 1; i < inputsId.length; i++) {
                        const additionalFilters = document.getElementById(inputsId[i]); //get the additional filters if exist
                        if (additionalFilters) { //we will see if the additional filters exist

                            //get the value of the additional filters
                            const additionalQuery = additionalFilters.value.trim();
                            allFilters.push(additionalQuery);  //save the additional filters in the array that send to the server
                        }
                    }
                    //send a message to the server for get the answer
                    data = await send_message_to_the_server(searchUrl, { allFilters }, false)
                }
                else{
                    //send a message to the server for get the answer
                    data = await send_message_to_the_server(searchUrl, { query }, false)
                }

                //we will see if the server can answer with the information or exist a error
                if (data.success) {


                    //clear the field
                    field.innerHTML = '';

                    //we will see if exist container for print in screen
                    if (data.results && data.results.length > 0) {

                        //if exist container, we will show in the field
                        data.results.forEach(dataFromTheServer => {

                            //now create a new card for show the information in the field
                            const card = document.createElement('div');

                            //now her create the container of the card
                            card.innerHTML = renderTemplate(divHtml, dataFromTheServer);

                            //add the new card for of field
                            field.appendChild(card);
                        });
                    } else {
                        //if exist an answer, we will show a message to the user
                        field.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados</td></tr>';
                    }
                }
                else {
                    console.error('Error en la búsqueda:', data.message);
                    show_alert('alert', 'Error', 'Error en la búsqueda desde el servidor. Intentalo otra vez.', data.message)
                    field.innerHTML = '<tr><td colspan="6" style="text-align:center;color:red;">Error en la búsqueda</td></tr>';
                }

            }
        }, delay);
    });
}

function renderTemplate(template, data) {
  return template.replace(/{\s*(\w+)\s*}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : '';
  });
}