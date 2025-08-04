/*---------------------------------------------class labels---------------------------------------------*/
class InfoLabel extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    // Crear tooltip global si no existe aún
    if (!document.querySelector('.erp-tooltip')) {
      const tooltip = document.createElement("div");
      tooltip.className = "erp-tooltip";
      tooltip.style.position = "absolute";
      tooltip.style.pointerEvents = "none";
      tooltip.style.opacity = "0";
      tooltip.style.transition = "opacity 0.3s ease";
      tooltip.style.background = "#333";
      tooltip.style.color = "#fff";
      tooltip.style.padding = "5px 10px";
      tooltip.style.borderRadius = "5px";
      tooltip.style.fontSize = "12px";
      document.body.appendChild(tooltip);
    }

    const tooltip = document.querySelector('.erp-tooltip');

    //get the information that the programmer add to the label
    const keyLabelText = this.getAttribute("label") || "";
    const keyMessage = this.getAttribute("message") || "";

    //her we will translate the text that the programmer add the label
    const labelText = translate_text(keyLabelText);
    const message = translate_text(keyMessage);

    const label = document.createElement("label");
    label.classList.add("info-label-generated");
    //label.setAttribute("t", keyLabelText);

    const span = document.createElement("span");
    span.setAttribute("t", keyLabelText);
    span.textContent = labelText;

    const icon = document.createElement("i");
    icon.className = "fi fi-sr-interrogation"; // Puedes cambiar el ícono

    // Evento tooltip
    icon.addEventListener("mouseenter", () => {
      tooltip.textContent = message;
      tooltip.style.opacity = "1";
    });

    icon.addEventListener("mousemove", (e) => {
      tooltip.style.left = (e.pageX + 15) + "px";
      tooltip.style.top = (e.pageY - 30) + "px";
    });

    icon.addEventListener("mouseleave", () => {
      tooltip.style.opacity = "0";
    });

    label.appendChild(span);
    label.appendChild(icon);

    this.replaceWith(label);
  }
}


class MessagePop extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const title = this.getAttribute('title') || '';
    const translatedTitle = translate_text(title); // Translate the title if needed

    //get the name of the pop, this is for identify the pop when the user do click in the button close
    const name = this.getAttribute('name') || 'pop-default';

    //get the size of the pop
    const width = this.getAttribute('width') || '600px';
    const height = this.getAttribute('height') || '400px';

    //get the container of the element, this can be a element or HTML
    const content = this.innerHTML.trim();

    //If only exist text, save this in a label <p>
    const wrappedContent = content.startsWith('<') ? content : `<p>${content}</p>`;

    //here create the internal HTML
    this.innerHTML = `
        <div id="${name}" class="my-pop">
          <div class="my-pop-content-wrapper">
            <div class="my-pop-header">
              <h4 class="my-pop-title" t="${translatedTitle}">${translatedTitle}</h4>
              <button class="close-btn" onclick="close_my_pop('${name}')" type="button">×</button>
            </div>
            <div class="my-pop-content">
              ${wrappedContent}
            </div>
          </div>
        </div>
      `;
  }
}

/*
<input-field 
label="email"  //lo que dira el label (esto es obligatorio)
name="escribe tu email" //el nombre con que se guardara the input
placeholder="escribe tu email" //lo que dira el placeholder del input

type="email"  //el tipo de input que vas a crear
id="" //el id con el que se guardara el input
></input-field>
*/
class InputField extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    //get the information that the user add to the label
    const labelTextInfo = this.getAttribute("label") || "";
    const labelText = translate_text(labelTextInfo);

    //her is the name with the that the programmer would like send this information to the server
    const name = this.getAttribute("name") || "";

    //her we will see the option that the programmer would like show. 
    //Also we will to valid the type of data that the user added for avoid an error 
    const validTypes = ["text", "email", "password", "number", "date", "tel"];
    const type = validTypes.includes(this.getAttribute("type"))  //her we willl see if the type that the user added, exist in our list of inputs types
      ? this.getAttribute("type") 
      : "text"; //for default is a input type text

    //now we will see if the programmer add a placeholder to the label
    const placeHolderText = this.getAttribute("placeholder");
    let placeholder = '';
    if (placeHolderText) {
      placeholder = translate_text(placeHolderText); //translate the text of the placeholder
    } else {
      //if the programmer not add a placeholder, we will show for default the information of the label
      placeholder = labelText;
    }


    //her we will watch if the input is required or have a max or min of length
    const required = this.hasAttribute("required");
    const maxLength = this.getAttribute("maxlength") || "";
    const minLength = this.getAttribute("minlength") || "";

    //her we will add the information of translate to the input
    const label = document.createElement("label");

    //this class is for when the input be required, the input can show a indicator to the user  
    label.classList.add("input-label");

    label.setAttribute("t", labelTextInfo); //add the information of translate
    label.textContent = labelText; //add the information that was translate

    //create the input and add his information
    const input = document.createElement("input");
    input.classList.add("input-field");
    
    
    input.type = type;
    input.name = name;

    //her we will add more atributes to the input only if the user would like do 
    const pattern = this.getAttribute("pattern");
    const readOnly = this.hasAttribute("readonly");
    const disabled = this.hasAttribute("disabled");

    if (pattern) input.pattern = pattern;
    if (readOnly) input.readOnly = true;
    if (disabled) input.disabled = true;

    //first we will see if exist the information of translate of the placeholder, if not exist save the information of the label for translate after 
    //save the information of translate of the placeholder
    const tPlaceholderKey = (!placeHolderText || placeHolderText.trim() === '')
      ? labelTextInfo
      : placeHolderText;
    input.placeholder = placeholder;
    input.setAttribute("t-placeholder", tPlaceholderKey);

    //config the setting of the input
    if (required) input.required = true;
    if (maxLength) input.maxLength = maxLength;
    if (minLength) input.minLength = minLength;

    //get the value that the user add to the label
    const value = this.getAttribute("value") || "";
    input.value = value;

    //add a event of input for know if the user is writing in the input only if the input be required
    if(required){
        const validateInput = () => {
          //her we will see if exist container in the input
          if (input.value.trim() !== '') {
            //if the input have a value, we will show to user that all is success
            label.classList.remove("plus-input-label-error");
            input.classList.remove("plus-input-error");

            label.classList.add("plus-input-label-success");
            input.classList.add("plus-input-success");
          } else {
            //if the input is void, we will show to user that this input is required
            label.classList.add("plus-input-label-error");
            input.classList.add("plus-input-error");

            label.classList.remove("plus-input-label-success");
            input.classList.remove("plus-input-success");
          }
        };

        input.addEventListener('input', validateInput); //this is when the user is writing in the input
        input.addEventListener('blur', validateInput); // This is when the user out of the input without write nothing
    }

    //add the all the labels to a div and the add to the web
    const wrapper = document.createElement("div");
    wrapper.classList.add("input-wrapper");

    //her we will see if the user would like add a message most to the label 
    const existMessageLabel=this.hasAttribute("message-label");
    if(existMessageLabel){

      //if exist a message label, we will add a label <message-label>
      const messageLabel=this.getAttribute("message-label");
      const labelMessage=document.createElement("info-label");
      labelMessage.setAttribute('label',labelTextInfo);
      labelMessage.setAttribute('message',messageLabel);

      wrapper.appendChild(labelMessage);
    }
    else{
      wrapper.appendChild(label);
    }


    wrapper.appendChild(input);

    this.replaceWith(wrapper);
  }
}

class ConfirmButton extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    //get the message and onclick attributes
    const textTitle = this.getAttribute("title") || "";
    const title = translateOld[textTitle] || textTitle; //here we will translate the title if exist in the dictionary

    const textMessage = this.getAttribute("message") || "Are you sure?";
    const message = translateOld[textMessage] || textMessage; //here we will translate the message if exist in the dictionary
    const onclickAttr = this.getAttribute("onclick");
    const buttonText = this.textContent.trim();

    const button = document.createElement("button");
    button.textContent = buttonText;
    button.classList.add("confirm-button");

    button.addEventListener("click", () => {
      this.showPopup(title, message, onclickAttr);
    });

    this.replaceWith(button);
  }

  showPopup(title, message, onclickAttr) {
    const overlay = document.createElement("div");
    overlay.className = "confirm-popup-overlay";

    const popup = document.createElement("div");
    popup.className = "confirm-popup";

    const iconCircle = document.createElement("div");
    iconCircle.className = "icon-circle";
    iconCircle.textContent = "?";


    const titleElement = document.createElement("h4");
    titleElement.textContent = title;

    const msg = document.createElement("p");
    msg.textContent = message;

    const buttons = document.createElement("div");
    buttons.className = "popup-buttons";

    const acceptBtn = document.createElement("button");
    acceptBtn.textContent = LANG['message.success'] || "Ok"; //get the translated text for the accept button
    console.log(LANG)
    acceptBtn.className = "popup-accept";

    const cancelBtn = document.createElement("button");
    cancelBtn.textContent = LANG['message.cancel'] || "Cancel"; //get the translated text for the cancel button
    cancelBtn.className = "popup-cancel";

    cancelBtn.onclick = () => overlay.remove();

    acceptBtn.onclick = () => {
      overlay.remove();
      const functionName = onclickAttr.replace(/\(\)/, "");
      if (onclickAttr && typeof window[functionName] === "function") {
        window[functionName]();
      } else {
        console.warn(`The function "${functionName}" was not found in window.`);
      }
    };

    buttons.appendChild(acceptBtn);
    buttons.appendChild(cancelBtn);
    popup.appendChild(iconCircle);
    popup.appendChild(msg);
    popup.appendChild(buttons);
    overlay.appendChild(popup);
    document.body.appendChild(overlay);
  }
}

class ConfirmDialog {
  static show(title, message) {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "confirm-popup-overlay";

      const popup = document.createElement("div");
      popup.className = "confirm-popup";

      //here we will create the icon circle and the title and message of the popup
      const iconCircle = document.createElement("div");
      iconCircle.className = "icon-circle";
      iconCircle.textContent = "?";

      //add the title and message to the popup
      const titleElement = document.createElement("h4");
      titleElement.textContent = translateOld[title] || title; //get the translated title if exists in the dictionary

      const msg = document.createElement("p");
      msg.textContent = translateOld[message] || message; //get the translated message if exists in the dictionary;

      //now we will create the buttons of the popup
      //these buttons are for accept or cancel the action that the user do
      const buttons = document.createElement("div");
      buttons.className = "popup-buttons";

      const acceptBtn = document.createElement("button");
      acceptBtn.textContent = LANG['message.success'] || "Ok"; //get the translated text for the accept button
      acceptBtn.className = "popup-accept";

      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = LANG['message.cancel'] || "Cancel"; //get the translated text for the cancel button
      cancelBtn.className = "popup-cancel";

      cancelBtn.onclick = () => {
        overlay.remove();
        resolve(false);
      };

      acceptBtn.onclick = () => {
        overlay.remove();
        resolve(true);
      };

      buttons.appendChild(acceptBtn);
      buttons.appendChild(cancelBtn);
      popup.appendChild(iconCircle);
      popup.appendChild(titleElement);
      popup.appendChild(msg);
      popup.appendChild(buttons);
      overlay.appendChild(popup);
      document.body.appendChild(overlay);
    });
  }
}

async function show_message_question(title, message) {
  const result = await ConfirmDialog.show(title, message);
  return result;
}




class AppMenu extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const container = document.createElement('nav');
    container.className = 'sub-menu-app-nav';

    const inner = document.createElement('div');
    inner.className = 'sub-menu-app-nav-container';

    //search all the <sub-menu> son
    const items = this.querySelectorAll('sub-menu');
    items.forEach(item => {
      //get the name of the sub menu
      const nameSubMenu = item.getAttribute('name') || '';
      const name = translate_text(nameSubMenu); //now we will translate the container

      const link = item.getAttribute('link') || '#';
      const btnClass = item.getAttribute('class') || 'btn-navbar';

      const navItem = document.createElement('div');
      navItem.className = 'sub-menu-app-nav-item';

      //her we will create the link
      const a = document.createElement('a');
      a.className = 'sub-menu-app-nav-link sub-menu-app-link-base';
      a.setAttribute('onclick', `nextWeb('${link}')`);

      //now we will create the menu
      const button = document.createElement('button');
      button.className = `btn ${btnClass}`;
      button.setAttribute('t', name);
      button.textContent = name;

      //add the container to the menu
      a.appendChild(button);
      navItem.appendChild(a);
      inner.appendChild(navItem);
    });

    container.appendChild(inner);
    this.replaceWith(container);
  }
}

class KeyBind extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const combo = (this.getAttribute("combo") || "").toLowerCase().replace(/\s+/g, '');
    const actionName = this.getAttribute("action");

    if (!combo || !actionName) return;

    // Separar teclas (por ejemplo: shift+v)
    const keys = combo.split('+');
    const pressedKeys = new Set();

    const onKeyDown = (e) => {
      pressedKeys.add(e.key.toLowerCase());

      const allKeysPressed = keys.every(k => pressedKeys.has(k.toLowerCase()));
      if (allKeysPressed) {
        if (typeof window[actionName] === 'function') {
          window[actionName]();
        } else {
          console.warn(`Función '${actionName}' no encontrada en window`);
        }
        pressedKeys.clear(); // evitar repeticiones rápidas
      }
    };

    const onKeyUp = (e) => {
      pressedKeys.delete(e.key.toLowerCase());
    };

    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);

    // Eliminar el nodo del DOM para que no estorbe visualmente
    this.style.display = "none";
  }
}


class PlusModules extends HTMLElement {
  connectedCallback() {
    //hwe we will read the atribute 'col' and we will calculate the propotion of the modules
    const col = parseInt(this.getAttribute('col')) || 4;
    const colSidebar = Math.max(1, Math.min(col, 11));
    const colContent = 12 - colSidebar;

    const modules = Array.from(this.querySelectorAll('plus-module'));
    const names = modules.map(m => m.getAttribute('name'));
    const icons = modules.map(m => m.getAttribute('icon') || '');
    const contents = modules.map(m => m.innerHTML);

    //clear the container for show a new layaout
    this.innerHTML = '';

    //make a sidebar
    const sidebar = document.createElement('div');
    sidebar.className = 'plus-modules-sidebar';
    sidebar.style.width = `${(colSidebar / 12) * 100}%`;

    const ul = document.createElement('ul');

    //her we will read all the moduels and we will create all his container
    names.forEach((name, i) => {
      const li = document.createElement('li');
      li.className = i === 0 ? 'active' : ''; //we will see if this module this active
      li.dataset.index = i;

      //create the icon if exist for the proggramer
      const iconSpan = document.createElement('span');
      iconSpan.className = 'plus-modules-icon';
      iconSpan.innerHTML = icons[i];

      li.appendChild(iconSpan);

      //add the text that the user would like translate
      const translateText = window.translate_text(name) //her we will translate the text if exist in the dictonary
      const p = document.createElement('p');
      p.textContent = translateText;
      p.setAttribute('t',name); //save the index fortranslate the text after if the user recharge the web

      //save the icon and the text
      li.appendChild(p);
      ul.appendChild(li);
    });

    sidebar.appendChild(ul); //add the module to the list of modules

    // Crear contenido
    const content = document.createElement('div');
    content.className = 'plus-modules-content';
    content.style.width = `${(colContent / 12) * 100}%`;

    const panel = document.createElement('div');
    panel.className = 'plus-modules-module-panel';
    panel.innerHTML = contents[0];
    content.appendChild(panel);

    // add to the DOM
    this.classList.add('plus-modules-host');
    this.appendChild(sidebar);
    this.appendChild(content);

    //Click events for tabs
    ul.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        ul.querySelectorAll('li').forEach(i => i.classList.remove('active'));
        li.classList.add('active');
        const index = li.dataset.index;
        panel.innerHTML = contents[index];
      });
    });
  }
}

customElements.define('plus-modules', PlusModules);

class PlusModule extends HTMLElement {
  connectedCallback() {
    this.classList.add('plus-modules-module');
  }
}

customElements.define('plus-module', PlusModule);






class PlusSelect extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    //get the information that the programmer added to the select
    const textLabel=this.getAttribute('label') || '';
    const textLabelTranslate=window.translate_text(textLabel); //translate the text of the label

    const name = this.getAttribute('name') || '';
    const isRequired = this.hasAttribute('requerid');

    //create a label of text of that the user can know that need do
    const thisLabelHaveAMessage=this.getAttribute('message');
    let label;

    //her we will know if the programmer need show a message to the user
    if(thisLabelHaveAMessage){
      //if the programmer need show a messga, we will to create the special label when the information that need
      label = document.createElement('info-label');
      label.setAttribute('label',textLabel)
      label.setAttribute('message',thisLabelHaveAMessage)
    }else{
      //if the programmer not need show a message, we will create a message normal
      label = document.createElement('label');
      label.setAttribute('t',textLabel);
      label.textContent=textLabelTranslate;
    }



    //Create main wrapper
    const wrapper = document.createElement('div');
    wrapper.classList.add('plus-select-wrapper');

    //Create select visible container
    const select = document.createElement('div');
    select.classList.add('plus-select-select');
    select.innerHTML = `
      <span class="plus-select-selected-text">${textLabelTranslate}</span>
      <i class="fi fi-rr-angle-small-right plus-select-icon"></i>
    `;

    //Create options popup
    const popup = document.createElement('div');
    popup.classList.add('plus-select-popup');

    // Create the container of the seeker 
    const searchWrapper = document.createElement('div');
    searchWrapper.classList.add('plus-select-search-wrapper');
    const txtSearch=t('message.search') || 'search...'; //get the translate global of a seeker
    searchWrapper.innerHTML = `
      <i class="fi fi-rs-search"></i>
      <input type="text" placeholder="${txtSearch}">
    `;
    const searchInput = searchWrapper.querySelector('input');

    //Create the container of the <option>
    const slotOptions = this.querySelectorAll('option');
    const options = [];

    slotOptions.forEach(opt => {
      //get the text of the iformation
      const optionText=opt.getAttribute('t');
      let textTranlate=opt.textContent;

      //we will see if the proggramer need translate this option
      if(optionText){
        textTranlate=window.translate_text(optionText); //translate the text that exist 
      }


      //her we will create the container of the div of the options
      const div = document.createElement('div');
      div.classList.add('plus-select-option');

      div.textContent = textTranlate; //update the text that we will show in the option
      div.dataset.value = opt.getAttribute('value') || textTranlate; //add the value

      //add the option to the select
      options.push(div);
      popup.appendChild(div);
    });

    // Insertar búsqueda antes de las opciones
    popup.insertBefore(searchWrapper, popup.firstChild);

    // Crear input oculto
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = name;
    if (isRequired) hiddenInput.required = true;

    // Evento de clic en el select visible
    select.addEventListener('click', () => {
      popup.classList.toggle('active');
      searchInput.focus();
    });

    // Evento clic en opciones
    options.forEach(opt => {
      opt.addEventListener('click', () => {
        select.querySelector('.plus-select-selected-text').textContent = opt.textContent;
        hiddenInput.value = opt.dataset.value;
        popup.classList.remove('active');
        searchInput.value = '';
        filterOptions('');
      });
    });

    // Filtrado
    searchInput.addEventListener('input', e => {
      filterOptions(e.target.value.toLowerCase());
    });

    function filterOptions(term) {
      options.forEach(opt => {
        opt.style.display = opt.textContent.toLowerCase().includes(term) ? 'block' : 'none';
      });
    }

    // Cerrar si hace clic fuera
    document.addEventListener('click', (e) => {
      if (!wrapper.contains(e.target)) {
        popup.classList.remove('active');
      }
    });

    // Montar estructura final
    wrapper.appendChild(label);
    wrapper.appendChild(select);
    wrapper.appendChild(popup);
    wrapper.appendChild(hiddenInput);

    this.replaceWith(wrapper);
  }
}
/**----------------------------------TABS----------------------**/
function open_tab(evt, tabName) {
  const tabs = document.querySelectorAll('.tab-content');
  const buttons = document.querySelectorAll('.tab-buttons button');

  tabs.forEach(tab => tab.classList.remove('active'));
  buttons.forEach(btn => btn.classList.remove('active'));

  document.getElementById(tabName).classList.add('active');
  evt.currentTarget.classList.add('active');
}

/**----------------------------------MESSAGE POP----------------------**/
function show_pop(idOverlay) {
  const overlay = document.getElementById(idOverlay);
  if (overlay) {
    overlay.style.display = 'flex';
  }
}

// Función para ocultar popup
function hide_pop(idOverlay) {
  const overlay = document.getElementById(idOverlay);
  if (overlay) {
    overlay.style.display = 'none';
  }
}


/**----------------------------------alert POP----------------------**/
function show_alert(type, title, description, readmoreText = '') {
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
  else if (type === 'success') iconEl.innerHTML = '<i class="fi fi-sr-check-circle"></i>';
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


function show_notification(type = 'info', message = '', duration = 4000) {
  const container = document.getElementById('notifications-container');

  const icons = {
    success: '<i class="fi fi-sr-check-circle"></i>',
    error: '<i class="fi fi-sr-cross-circle"></i>',
    warning: '<i class="fi fi-sr-exclamation"></i>',
    info: '<i class="fi fi-sr-info"></i>'
  };

  const alert = document.createElement('div');
  alert.className = `notification-alert ${type}`;
  alert.innerHTML = `
        <div class="icon">${icons[type] || icons['info']}</div>
        <div class="message">${message}</div>
        <button class="close-btn" onclick="this.parentElement.style.animation='slideOut 0.4s forwards'; setTimeout(()=>this.parentElement.remove(),400);">&times;</button>
    `;

  container.appendChild(alert);

  setTimeout(() => {
    alert.style.animation = 'slideOut 0.4s forwards';
    setTimeout(() => alert.remove(), 400);
  }, duration);
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
      if (query == '') {
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
      const newData = await get_the_new_data_of_the_select_search(fetchUrl, query);
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

function addItemWithSelec(dropdownEl, createUrl, lastQuery) {
  dropdownEl.style.display = 'none'; //hidden the answer
}


function create_option_of_the_select(element, dropdownEl, newDataSelect, lastQuery, createUrl) {
  //clear the dropdown of the select for that not show nothing
  dropdownEl.innerHTML = '';

  //her we will see if not exist answer from the server
  if (newDataSelect.length === 0) {
    //now see if exist a link for add a new item 
    if (createUrl == '' || !createUrl) {
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
    } else {
      //if exist, this function is for create the button that the user use for add a new item in the database of the select 
      add_the_button_for_create_a_new_item_in_the_select_search(dropdownEl, createUrl, lastQuery);
    }
  } else {
    //if the server send answer, we will show all the item that the server send
    add_all_the_answer_that_the_server_send(element, dropdownEl, newDataSelect);
  }

  //update the position of the dropdown
  const rect = element.getBoundingClientRect();
  dropdownEl.style.left = rect.left + 'px';
  dropdownEl.style.top = (rect.bottom + window.scrollY) + 'px';
  dropdownEl.style.width = rect.width + 'px';
  dropdownEl.style.display = 'block';
}

function add_all_the_answer_that_the_server_send(element, dropdownEl, newDataSelect) {
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

function add_the_button_for_create_a_new_item_in_the_select_search(dropdownEl, createUrl, lastQuery) {
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



///---------------------------function for css and js for help to the programmers to work in the frontend------------------
//this function is for auto resize the textarea when the user write in the textarea
function form_auto_resize(id_textarea) {
  const textarea = document.getElementById(id_textarea); //get the textarea that we will resize
  if (textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
}

//this function is for add a short cut in the app that the programmer would like add.
function add_short_cut(keyCombo, callback) {
  //keyCombo= the combination of the keys that the user will use for do the short cut example Control+S
  //callback= the function that we will execute when the user do the short cut


  //we will convert the combination of the keys in a set of key normal
  const combo = keyCombo.toLowerCase().split('+').map(k => k.trim());

  //we listen the event keydown global
  document.addEventListener('keydown', function (event) {
    const keysPressed = [];

    if (event.ctrlKey) keysPressed.push('control');
    if (event.altKey) keysPressed.push('alt');
    if (event.shiftKey) keysPressed.push('shift');
    if (event.metaKey) keysPressed.push('meta'); // Para MacOS Command key

    const key = event.key.toLowerCase();


    // Avoid duplicating if it is already a modifier
    if (!['control', 'alt', 'shift', 'meta'].includes(key)) {
      keysPressed.push(key);
    }

    // Check if all keys match
    const match = combo.every(k => keysPressed.includes(k)) && keysPressed.length === combo.length;
    if (match) {
      event.preventDefault(); // prevent default actions like Ctrl+S
      callback(event);
    }
  });
}

//this function is for add a class to a element when the user do click in other element 
function toggle_class_on_click(triggerSelector, targetSelector, className) {
  //triggerSelector= the selector of the element that we will use for do click
  //targetSelector= the selector of the element that we will add the class
  //className= the class that we will add to the targetSelector

  //her we will get all the elemet that have the selector triggerSelector and targetSelector
  const triggerElement = document.querySelector(triggerSelector);
  const targetElement = document.querySelector(targetSelector);

  //if not exist the element, we will not do nothing
  if (triggerElement && targetElement) {
    //if exist a element, so we will add the event listener
    //when the user do click in the triggerElement, we will add or remove the className in the targetElement
    triggerElement.addEventListener('click', function () {
      targetElement.classList.toggle(className);
    });
  }
}

/*
this is for add a function when the user do click in a element in the web.
this function is for attach a click event to an element with a specific selector
and execute a callback function when the element is clicked.
*/
function attach_click(triggerSelector, callback) {
  //triggerSelector= the selector of the element that we will use for do click
  //callback= the function that we will execute when the user do click in the element

  //her we will get all the element that have the selector triggerSelector
  const triggerElement = document.querySelector(triggerSelector);
  if (triggerElement) {
    //if exist a element with the selector, we will add the event listener
    triggerElement.addEventListener('click', callback);
  }
}

function load_script(src) {
  return new Promise((resolve, reject) => {
    //we will check if the script already exist in the document
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }


    //if not exist the script, we will create a new script element and add it to the document
    const script = document.createElement('script');
    script.src = src;
    script.async = false;
    script.onload = () => resolve();
    script.onerror = () => reject(`The script could not be loaded ${src}`);
    document.head.appendChild(script);
  });
}



/**----------------------------------show message label----------------------**/
function transform_my_labels_erp() {
  //this function is for transform the labels that have the tag info-label in the web
  //this is for add a icon with a tooltip when the user do hover over the icon
  //create_info_labels();
  //customElements.define("info-label", InfoLabel);
  if (!customElements.get("info-label")) {
    customElements.define("info-label", InfoLabel);
  }
  if (!customElements.get("message-pop")) {
    customElements.define("message-pop", MessagePop);
  }

  if (!customElements.get("input-field")) {
    customElements.define("input-field", InputField);
  }

  if (!customElements.get("confirm-button")) {
    customElements.define("confirm-button", ConfirmButton);
  }

  if (!customElements.get("app-menu")) {
    customElements.define("app-menu", AppMenu);
  }

  if (!customElements.get("key-bind")) {
    customElements.define("key-bind", KeyBind);
  }

  if (!customElements.get("plus-modules")) {
    customElements.define("plus-modules", PlusModules);
  }

  if (!customElements.get("plus-module")) {
    customElements.define("plus-module", PlusModule);
  }

  if (!customElements.get("plus-select")) {
    customElements.define("plus-select", PlusSelect);
  }
}

/**---------------------------------SHOW MESSAGE POP PERSONALITY----------------------------- */
function open_my_pop(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'flex';
}

function close_my_pop(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}
