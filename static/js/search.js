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

