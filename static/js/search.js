function update_table_with_seeker(inputId, tableId, searchUrl, delay = 500) {
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
                        data.results.forEach(customer => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${customer.name}</td>
                                <td>${customer.email}</td>
                                <td>${customer.phone || ''}</td>
                                <td>${customer.cellphone || ''}</td>
                                <td>${customer.company_name || ''}</td>
                                <th><button class="btn btn-edit"><i class="fi fi-sr-pencil"></i></button></th>
                            `;

                            //add the container to the table
                            tableBody.appendChild(row);
                        });
                    } else {
                        //if exist an answer, we will show a message to the user
                        tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados</td></tr>';
                    }
                }
                else {
                    console.error('Error en la búsqueda:', error);
                    show_alert('alert', 'Error', 'Error en la búsqueda desde el servidor. Intentalo otra vez.', error)
                    tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:red;">Error en la búsqueda</td></tr>';
                }

            }
        }, delay);
    });
}

