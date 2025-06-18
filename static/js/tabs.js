/**----------------------------------TABS----------------------**/
function openTab(evt, tabName) {
  const tabs = document.querySelectorAll('.tab-content');
  const buttons = document.querySelectorAll('.tab-buttons button');

  tabs.forEach(tab => tab.classList.remove('active'));
  buttons.forEach(btn => btn.classList.remove('active'));

  document.getElementById(tabName).classList.add('active');
  evt.currentTarget.classList.add('active');
}

/**----------------------------------MESSAGE POP----------------------**/
function showPop(idOverlay) {
  const overlay = document.getElementById(idOverlay);
  if (overlay) {
    overlay.style.display = 'flex';
  }
}

// Función para ocultar popup
function hidePop(idOverlay) {
  const overlay = document.getElementById(idOverlay);
  if (overlay) {
    overlay.style.display = 'none';
  }
}


/**----------------------------------alert POP----------------------**/
function showAlert(type, title, description, readmoreText = '') {
  const overlay = document.getElementById('alert-overlay');
  const pop = document.getElementById('alert-pop');
  const titleEl = document.getElementById('alert-title');
  const descEl = document.getElementById('alert-description');
  const readmoreEl = document.getElementById('alert-readmore');
  const buttonsEl = document.getElementById('alert-buttons');
  const iconEl = document.getElementById('alert-icon');

  pop.classList.remove('sub-menu-app-pop-info', 'sub-menu-app-pop-alert', 'sub-menu-app-pop-question', 'sub-menu-app-pop-normal');
  pop.classList.add('sub-menu-app-pop-' + type);

  //icon for type
  if (type === 'info') iconEl.innerHTML = '<i class="fi fi-sr-info"></i>';
  else if (type === 'alert') iconEl.innerHTML = '<i class="fi fi-sr-exclamation"></i>';
  else if (type === 'question') iconEl.innerHTML = '<i class="fi fi-sr-interrogation"></i>';
  else iconEl.innerHTML = '';

  //update the text that show the alert pop
  titleEl.textContent = title;
  descEl.textContent = description;
  buttonsEl.innerHTML = '';

  //get the text of the buttons with the language that have the web. This is for update the text of all the button
  const btnTextSuccess = buttonsEl.getAttribute('btnTextSuccess');
  const btnTextCancel = buttonsEl.getAttribute('btnTextCancel');
  const btnTextReadMost = buttonsEl.getAttribute('btnTextReadMost');

  //her we will see if exist most text for show like message of error in code
  readmoreEl.textContent = readmoreText;
  readmoreEl.style.display = 'none';


  //we will see if the message is a question
  if (type === 'question') {
    const btnYes = document.createElement('button');
    btnYes.className = 'sub-menu-app-btn sub-menu-app-btn-primary';
    btnYes.textContent = btnTextSuccess;
    btnYes.onclick = function () {
      hideAlert();
      return true;
    };

    const btnNo = document.createElement('button');
    btnNo.className = 'sub-menu-app-btn sub-menu-app-btn-secondary';
    btnNo.textContent = btnTextCancel;
    btnNo.onclick = function () {
      hideAlert();
      return true;
    };

    buttonsEl.appendChild(btnYes);
    buttonsEl.appendChild(btnNo);
  } else {
    //when the alert not is a question, only exist a button
    const btnClose = document.createElement('button');
    btnClose.className = 'sub-menu-app-btn sub-menu-app-btn-primary';
    btnClose.textContent = btnTextSuccess;

    //when the user do a click in the button, only hidden the alert
    btnClose.onclick = function () {
      hideAlert();
    };
    buttonsEl.appendChild(btnClose);
  }



  overlay.style.display = 'flex';
}

function hideAlert() {
  const overlay = document.getElementById('alert-overlay');
  overlay.style.display = 'none';
}

function toggleReadMore() {
  const content = document.getElementById('alert-readmore');
  const readmoreEl = document.getElementById('alert-readmore');
  if (readmoreEl.textContent !== '') {
    if (content.style.display === 'none' || content.style.display === '') {
      content.style.display = 'block';
    } else {
      content.style.display = 'none';
    }
  }
}



/*---------------------------------select search--------------------------*/
function createSmartSelect({ element, fetchUrl, createUrl, placeholder }) {
  let timeout = null;
  let lastQuery = '';

  //create the dropdown of the answers
  const dropdownEl = document.createElement('div');
  dropdownEl.className = 'smart-select-dropdown';
  dropdownEl.style.position = 'absolute';
  dropdownEl.style.zIndex = '9999';
  dropdownEl.style.background = '#fff';
  dropdownEl.style.border = '1px solid #ccc';
  dropdownEl.style.borderRadius = '8px';
  dropdownEl.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.08)';
  dropdownEl.style.display = 'none';
  dropdownEl.style.maxHeight = '220px';
  dropdownEl.style.overflowY = 'auto';
  dropdownEl.style.fontFamily = 'Segoe UI, sans-serif';
  dropdownEl.style.fontSize = '15px';
  dropdownEl.style.color = '#333';
  document.body.appendChild(dropdownEl);

  //save the placeholder if exist
  element.placeholder = placeholder || '';
  element.autocomplete = 'off';

  //first we will see if the user is writing in the search 
  element.addEventListener('input', function () {
    clearTimeout(timeout); //start the timeout
    const query = element.value.trim(); //get the value of the input


    //we will see the time that transcurium
    timeout = setTimeout(async () => {
      //first we will see if the input is empty
      //this is for avoid unnecessary server searches
      if(query==''){
        dropdownEl.innerHTML = ''; //hidden the answer of the server
        return;
      }


      //if not exist change, not send a send to the server for get the new information
      //also this is for avoid unnecessary server searches
      if (query === lastQuery) {
        return;
      }

      //if not is equal to the former word, update the lastQuery and send the application to the server for get the new fata
      lastQuery = query; //update the last query
      const newData=await get_the_new_data_of_the_select_search(fetchUrl,query); 
      create_option_of_the_select(element, dropdownEl, newData, query, createUrl);
    }, 400);
  });
}

async function get_the_new_data_of_the_select_search(fetchUrl, query) {
  /**
   her we will send a method post to the server for get the first answer in the database use the writing of the query that the user
   is writing. The server should send us a JSON with the data id and name. the id is the index of the item that search, and the name 
   is the parameter that we would like show in the select. Example:
    return [
      { id: 1, name: query + ' Customer A' },
      { id: 2, name: query + ' Customer B' },
      { id: 3, name: query + ' Customer C' }
    ];
   */
  return []
  // Simulamos una espera (puedes poner fetch real aquí)
  await new Promise(resolve => setTimeout(resolve, 200));

  // Datos de muestra
  return [
    { id: 1, name: query + ' Cliente A' },
    { id: 2, name: query + ' Cliente B' },
    { id: 3, name: query + ' Cliente C' }
  ];
}

function addItemWithSelec(dropdownEl,createUrl, lastQuery){
  dropdownEl.style.display = 'none'; //hidden the answer
}


function create_option_of_the_select(element, dropdownEl, newDataSelect, lastQuery, createUrl) {
  //clear the dropdown of the select for that not show nothing
  dropdownEl.innerHTML = '';

  //her we will see if not exist answer from the server
  if (newDataSelect.length === 0) {
    //now see if exist a link for add a new item 
    if(createUrl=='' || !createUrl){
      //if not exist the link for create the URL, this select only is for search or for add this item need most requirements and the programmer 
      //need show a message pop most complete. Now show a message saying there are no results
      const createBtn = document.createElement('label');
      createBtn.className = 'smart-select-create-btn';

      createBtn.textContent = `${shortButtons[langCode][6]}`;
      createBtn.style.display = 'block';
      createBtn.style.width = '100%';
      createBtn.style.padding = '12px 16px';
      createBtn.style.border = 'none';
      createBtn.style.background = '#f0f0f0';
      createBtn.style.cursor = 'pointer';
      createBtn.style.color = '#333';
      createBtn.style.fontSize = '14px';
      createBtn.style.textAlign = 'left';
    }else{
      //if exist, this function is for create the button that the user use for add a new item in the database of the select 
      add_the_button_for_create_a_new_item_in_the_select_search(dropdownEl,createUrl,lastQuery);
    }
  } else {
    //if the server send answer, we will show all the item that the server send
    add_all_the_answer_that_the_server_send(element,dropdownEl,newDataSelect);
  }

  //update the position of the dropdown
  const rect = element.getBoundingClientRect();
  dropdownEl.style.left = rect.left + 'px';
  dropdownEl.style.top = (rect.bottom + window.scrollY) + 'px';
  dropdownEl.style.width = rect.width + 'px';
  dropdownEl.style.display = 'block';
}

function add_all_the_answer_that_the_server_send(element,dropdownEl,newDataSelect){
    //read all the answer of the server for add all the answer of the server in the select
    newDataSelect.forEach(item => {
      //--this is for the styles css of the answer
      const optionEl = document.createElement('div');
      optionEl.className = 'smart-select-option';
      optionEl.style.padding = '12px 16px';
      optionEl.style.cursor = 'pointer';
      optionEl.style.borderBottom = '1px solid #f1f1f1';
      optionEl.style.transition = 'background 0.2s ease';
      optionEl.style.userSelect = 'none';

      //css hover
      optionEl.onmouseenter = function () {
        optionEl.style.background = '#f9f9f9';
      };

      optionEl.onmouseleave = function () {
        optionEl.style.background = '#fff';
      };

      //update the text of the text of the option
      optionEl.textContent = item.name;

      //this function is for hidden the answer of the select when the user do click in a option
      optionEl.onclick = function () {
        element.value = item.name; //get the value
        dropdownEl.style.display = 'none'; //hidden the answer

        const event = new CustomEvent('smart-select-selected', { detail: item });
        element.dispatchEvent(event);
      };

      dropdownEl.appendChild(optionEl);
    });
}

function add_the_button_for_create_a_new_item_in_the_select_search(dropdownEl,createUrl,lastQuery){
    //when not exist a answer of the server is because not exist the item and we can create. 
    const createBtn = document.createElement('button');
    createBtn.className = 'smart-select-create-btn';

    createBtn.textContent = `+ ${shortButtons[langCode][2]} "${lastQuery}"`;
    createBtn.style.display = 'block';
    createBtn.style.width = '100%';
    createBtn.style.padding = '12px 16px';
    createBtn.style.border = 'none';
    createBtn.style.background = '#f0f0f0';
    createBtn.style.cursor = 'pointer';
    createBtn.style.color = '#333';
    createBtn.style.fontSize = '14px';
    createBtn.style.textAlign = 'left';

    // On click → call your function. This is for save the new item that to the user would like add. 
    createBtn.onclick = function () {
      addItemWithSelec(dropdownEl, createUrl, lastQuery);
    };

    //add the button
    dropdownEl.appendChild(createBtn);
}


//this function is for load all the search select in the web.
function create_all_the_select() {

  //her get all select in the web
  const selects = document.querySelectorAll('.select-search');

  //we use a loop for get the information of the select like this 
  selects.forEach(inputEl => {
    const fetchUrl = inputEl.getAttribute('data-fetch-url');
    const createUrl = inputEl.getAttribute('data-create-url');
    const placeholder = inputEl.getAttribute('placeholder');
    const reference = inputEl.getAttribute('reference'); //this is for know where save the id of the select search that the user choose
    const isRequired = inputEl.hasAttribute('required'); //this is for know if this input is required

    //we will see if exist all the information of the server for create the select search. 
    //if not have all the information of the links, we will not create the select
    if (fetchUrl) {

      // We automatically force type text and autocomplete
      inputEl.type = 'text';
      inputEl.autocomplete = 'off';

      //if exist the attribute reference, we will create the input hidden that save the id of the reference of the select search
      if (reference) {
        //Check if a hidden item already exists to avoid duplication
        let hiddenInput = inputEl.parentElement.querySelector(`input[type="hidden"][name="${reference}"]`);
        
        //if not exist the hidden input, we will create
        if (!hiddenInput) {
          //create the input hidden, this input is the that have the information that save in the database when send the form to the server
          hiddenInput = document.createElement('input');
          hiddenInput.type = 'hidden';
          hiddenInput.name = reference;

          //If the original select had "required", we also put it in the hidden
          if (isRequired) {
            hiddenInput.required = true;
          }

          //save the hidden  input after of the visible input
          inputEl.parentElement.insertBefore(hiddenInput, inputEl.nextSibling);
        }
      }

      //her we will create the select
      createSmartSelect({
        element: inputEl,
        fetchUrl: fetchUrl,
        createUrl: createUrl,
        placeholder: placeholder
      });
    }
  });
}


create_all_the_select();