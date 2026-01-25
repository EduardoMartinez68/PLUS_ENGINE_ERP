let currentPopZIndex = 5000;
const colors = {
  color_company: '#2b6cb0',
  color_company_hover: '#064985',
  color_second: '#1d7dd1ff',
  color_container_white:"#ffffffff",


  color_company_black:'#1D1D1F',
  color_second_black: '#303033ff',
  color_icon_black:'#76B5D6',
  color_container_black:"#32323E",
  color_text_black:'#E5E4EA'
}

/*
const toggleTheme = () => {
  const root = document.documentElement;
  const currentTheme = root.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  root.setAttribute("data-theme", newTheme);

  // save the preference of the user
  localStorage.setItem("theme", newTheme);
};

window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
  } else {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  }
});
*/

//this functions is for create a id unique for that not exist a error when create a new element
function generate_unique_dom_id(prefix = "plus-") {
  let id;
  do {
    id = prefix + Math.random().toString(36).substr(2, 9);
  } while (document.getElementById(id));
  return id;
}

//this function is for know if the value of a variable is true or false use all the information 
//1, true , True, 'true' etc
function is_true(value) {
  if (value === true) return true;

  if (typeof value === "string") {
    const val = value.trim().toLowerCase();
    return val === "true" || val === "1" || val === "yes" || val === "on" || val === 'True';
  }

  if (typeof value === "number") {
    return value === 1;
  }

  return false;
}


/*---------------------------------------------class labels---------------------------------------------*/
class InfoLabel extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    // Create global tooltip if it doesn't exist yet
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
    const help=this.getAttribute('help') || '';

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
    this._template = ""; //here we will save the original content of the element
    this._initialized = false;
  }

  connectedCallback() {
    if (!this._initialized) {
      // 1. save the container original of the event
      this._template = this.innerHTML.trim();
      this._initialized = true;
      this.render();
    }
  }

  // This function draw the internal HTML of the element
  render() {
    const title = this.getAttribute('title') || '';
    const translatedTitle = window.translate_text(title); // Translate the title if needed

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



class PlusPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._onOverlayClick = this._onOverlayClick.bind(this);
  }

  connectedCallback() {
    const side = this.getAttribute('side') || 'left';
    const size = this.getAttribute('size') || '400px';
    const titleText = window.translate_text(this.getAttribute('title') || 'Panel');

    let blurBackground = false;
    if(this.hasAttribute('blur-background')){
      blurBackground = this.getAttribute('blur-background') === 'true';
    }

    const closeOnOverlay = this.getAttribute('close-on-overlay') === 'true';

    const containerBg = '#F5F7FA';
    const companyBg = colors.color_company;

    // overlay for all the screen
    const overlay = document.createElement('div');
    overlay.classList.add('plus-panel-overlay');

    // container of the panel
    const container = document.createElement('div');
    container.classList.add('plus-panel-container', side);
    container.style.width = size;

    // navbar
    const navbar = document.createElement('div');
    navbar.classList.add('plus-panel-navbar');

    const title = document.createElement('span');
    title.classList.add('plus-panel-title');
    title.textContent = titleText;

    const closeBtn = document.createElement('button');
    closeBtn.classList.add('plus-panel-close');
    closeBtn.setAttribute('aria-label', 'Cerrar panel');
    closeBtn.innerHTML = '×';
    closeBtn.addEventListener('click', () => this.hide());

    navbar.append(title, closeBtn);

    //container
    const content = document.createElement('div');
    content.classList.add('plus-panel-content');
    const slot = document.createElement('slot');
    content.appendChild(slot);

    container.append(navbar, content);
    overlay.appendChild(container);

    const style = document.createElement('style');
    style.textContent = `
      :host {
        position: fixed;
        inset: 0;
        width: 100%;
        height: 100%;
        pointer-events: none; /* por defecto no interfiere */
        z-index: 9999;
        display: block;
      }

      .plus-panel-overlay {
        position: absolute;
        inset: 0;
        background: transparent;
        backdrop-filter: none;
        transition: background 0.25s ease, backdrop-filter 0.25s ease;
        pointer-events: none; /* bloquea clicks hacia el overlay cuando no visible */
      }

      /* When the host has visible, we activate overlay. */
      :host(.visible) .plus-panel-overlay {
        background: ${blurBackground ? 'rgba(0,0,0,0.4)' : 'rgba(0,0,0,0.25)'};
        backdrop-filter: ${blurBackground ? 'blur(5px)' : 'none'};
        pointer-events: auto; /* ahora acepta clicks (p.ej. para cerrar) */
      }

      .plus-panel-container {
        position: absolute;
        top: 0;
        height: 100%;
        max-width: 100%;
        background: ${containerBg};
        color: inherit;
        box-shadow: 2px 0 14px rgba(0, 0, 0, 0.35);
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        transform: translateX(${side === 'left' ? '-100%' : '100%'});
        transition: transform 0.35s cubic-bezier(.2,.9,.2,1);
      }

      .plus-panel-container.left { left: 0; }
      .plus-panel-container.right { right: 0; left: auto; }

      /* Show panel when host has the visible class */
      :host(.visible) .plus-panel-container {
        transform: translateX(0);
      }

      .plus-panel-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        background: ${companyBg};
        border-bottom: 1px solid ${companyBg};
        color: #fff;
        font-weight: 600;
      }

      .plus-panel-close {
        background: transparent;
        border: none;
        color: #fff;
        font-size: 22px;
        line-height: 1;
        cursor: pointer;
        padding: 0;
      }
      .plus-panel-close:hover { transform: scale(1.08); }

      .plus-panel-content {
        padding: 18px;
        flex: 1;
        overflow-y: auto;
      }

      @media (max-width: 768px) {
        .plus-panel-container { width: 100% !important; border-radius: 0; }
      }
    `;

    // clear and add
    this.shadowRoot.innerHTML = '';
    this.shadowRoot.append(style, overlay);

    // save references for listeners
    this._overlayEl = overlay;
    this._closeOnOverlay = closeOnOverlay;

    //If you want to close by clicking on overlay, listen
    if (this._closeOnOverlay) {
      this._overlayEl.addEventListener('click', this._onOverlayClick);
      // prevent clicks within the panel from triggering the close
      container.addEventListener('click', e => e.stopPropagation());
    }
  }

  // handler para click en overlay (si se habilitó)
  _onOverlayClick(e) {
    // sólo cerrar si el host está visible
    if (this.classList.contains('visible')) {
      this.hide();
    }
  }

  show() {
    currentPopZIndex += 1;
    this.style.zIndex = currentPopZIndex;
    this.classList.add('visible');
    this.style.pointerEvents = 'auto';
  }

  hide() {
    this.classList.remove('visible');
    this.style.pointerEvents = 'none';
  }

  disconnectedCallback() {
    if (this._overlayEl && this._closeOnOverlay) {
      this._overlayEl.removeEventListener('click', this._onOverlayClick);
    }
  }
}


class EditQuantity extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.name = this.getAttribute('name') || 'quantity';
    this.type = this.getAttribute('type') === 'float' ? 'float' : 'int';
    this.stepAttr = this.getAttribute('step') || '1';
    this.step = this.type === 'float' ? parseFloat(this.stepAttr) : parseInt(this.stepAttr);
    this.t = this.getAttribute('t') || this.getAttribute('title') || 'btn.edit-quantity';
    this.titleText = window.translate_text(this.t);

    // Initial value that the input will display
    this._value = this.type === 'float' ? 0.0 : 0;
  }

  connectedCallback() {
    this.renderInput();
  }

  renderInput() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          all: initial;
          display: inline-block;
          font-family: 'Segoe UI', sans-serif;
        }
        input,
        textarea,
        select {
          width: 100%;
          padding: 8px 4px;
          margin-top: 4px;
          border: none;
          border-bottom: 2px solid #d0d5dd;
          background-color: transparent;
          font-size: 1em;
          color: #1d2939;
          outline: none;
          transition: border-color 0.3s;
          margin: 12px 0;
        }

        input:hover{
          cursor: pointer;
        }

        input:focus,
        select:focus {
          border-bottom-color: #2a395b;
        }
      </style>
      <input type="text" class="display-input" readonly value="${this._value}" title="${this.titleText}" name="${this.name}" />
    `;

    this.shadowRoot.querySelector('.display-input').addEventListener('click', () => this.openPopup());
  }

  openPopup() {
    // Crear overlay + popup
    const popup = document.createElement('div');
    popup.classList.add('overlay');
    popup.innerHTML = `
      <style>
        .overlay {
          position: fixed;
          inset: 0;
          background-color: rgba(0,0,0,0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
        }
        .popup {
          background: #fff;
          border-radius: 12px;
          width: 90%;
          max-width: 600px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.2);
          overflow: hidden;
          font-family: 'Segoe UI', sans-serif;
          padding: 0;
        }
        .navbar {
          background: ${colors.color_company};
          color: white;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .navbar h4 {
          margin: 0;
          font-size: 20px;
        }
        .navbar .close-btn {
          background: transparent;
          border: none;
          color: white;
          font-size: 24px;
          cursor: pointer;
        }
        .body {
          padding: 24px 16px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 24px;
        }
        .controls {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .controls input {
          width: 50%;
          text-align: center;
          font-size: 24px;
          padding: 10px;
          border-radius: 10px;
          border: 1px solid #ccc;
        }
        .quantity-btn {
          width: 48px;
          width:25%;
          height: 48px;
          font-size: 28px;
          background-color: ${colors.color_company};
          border: none;
          border-radius: 10px;
          cursor: pointer;
          transition: background 0.3s;
          color: white;
        }
        .quantity-btn:hover {
          background-color: ${colors.color_company_hover};
        }
        .footer {
          width: 100%;
          margin-top: 10px;
        }
        .accept-btn {
          width: 100%;
          padding: 14px 0;
          font-size: 18px;
          border: none;
          border-radius: 10px;
          background-color: ${colors.color_company};
          color: white;
          cursor: pointer;
          transition: background 0.3s;
        }
        .accept-btn:hover {
          background-color: ${colors.color_company_hover};
        }
        /* Responsive */
        @media (max-width: 768px) {
          .popup {
            width: 95%;
            max-width: 90%;
          }
          .controls input {
            width: 100px;
            font-size: 20px;
          }
          .quantity-btn {
            width: 44px;
            height: 44px;
            font-size: 26px;
          }
          .accept-btn {
            font-size: 16px;
            padding: 12px 0;
          }
          .navbar h4 {
            font-size: 18px;
          }
        }
        @media (max-width: 480px) {
          .controls {
            gap: 12px;
          }
          .controls input {
            width: 80px;
            font-size: 18px;
          }
          .quantity-btn {
            width: 40px;
            height: 40px;
            font-size: 24px;
          }
          .accept-btn {
            font-size: 16px;
            padding: 10px 0;
          }
          .navbar h4 {
            font-size: 16px;
          }
        }
      </style>
      <div class="popup">
        <div class="navbar">
          <h4 t='${this.t}'>${this.titleText}</h4>
          <button class="close-btn" title="Cerrar">&times;</button>
        </div>
        <div class="body">
          <div class="controls">
            <button class="quantity-btn" id="decrease">−</button>
            <input type="number" id="quantity" value="${this._value}" step="${this.step}" />
            <button class="quantity-btn" id="increase">+</button>
          </div>
          <div class="footer">
            <button class="accept-btn" id="accept" t='${window.t('message.success')}'>Success</button>
          </div>
        </div>
      </div>
    `;

    // add popup to shadowRoot for that the label is encapsulated
    this.shadowRoot.appendChild(popup);

    const close = () => {
      this.shadowRoot.removeChild(popup);
    };

    const $ = this.shadowRoot;

    //buttons
    popup.querySelector('.close-btn').addEventListener('click', close);

    const inputQuantity = popup.querySelector('#quantity');

    popup.querySelector('#increase').addEventListener('click', () => {
      let currentValue = parseFloat(inputQuantity.value);
      currentValue += this.step;
      inputQuantity.value = this.type === 'int' ? Math.round(currentValue) : currentValue.toFixed(2);
    });

    popup.querySelector('#decrease').addEventListener('click', () => {
      let currentValue = parseFloat(inputQuantity.value);
      currentValue -= this.step;
      inputQuantity.value = this.type === 'int' ? Math.round(currentValue) : currentValue.toFixed(2);
    });

    popup.querySelector('#accept').addEventListener('click', () => {
      this._value = inputQuantity.value;
      // update the input that the user can see
      this.shadowRoot.querySelector('.display-input').value = this._value;
      close();

      // Optional: trigger event to notify that the value has changed
      this.dispatchEvent(new CustomEvent('change', {
        detail: { value: this._value }
      }));
    });
  }

  // Getter for the current value
  get value() {
    return this._value;
  }

  // Setter to update value from outside
  set value(val) {
    this._value = val;
    if (this.shadowRoot.querySelector('.display-input'))
      this.shadowRoot.querySelector('.display-input').value = val;
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
    const help = this.getAttribute("help") || ''; //here get if the user would like create a label of help
    const label = document.createElement(help ? "info-label" : "label");

    //this class is for when the input be required, the input can show a indicator to the user  
    label.classList.add("input-label");

    label.setAttribute("label", labelTextInfo);
    label.setAttribute("message", help);
    label.setAttribute("t", labelTextInfo); //add the information of translate
    label.textContent = labelText; //add the information that was translate

    //create the input and add his information
    const input = document.createElement("input");
    input.classList.add("input-field");


    input.type = type;
    input.name = name;
    input.id = this.getAttribute('id') || name || generate_unique_dom_id();

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
    if (required) {
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
    const existMessageLabel = this.hasAttribute("message-label");
    if (existMessageLabel) {

      //if exist a message label, we will add a label <message-label>
      const messageLabel = this.getAttribute("message-label");
      const labelMessage = document.createElement("info-label");
      labelMessage.setAttribute('label', labelTextInfo);
      labelMessage.setAttribute('message', messageLabel);

      wrapper.appendChild(labelMessage);
    }
    else {
      wrapper.appendChild(label);
    }

    const line = this.getAttribute("line") || true;
    if (!is_true(line)) {
      input.classList.add("no-line");
    }

    wrapper.appendChild(input);

    this.replaceWith(wrapper);
  }
}

class PlusTitle extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    // Texto del label = contenido del componente
    const labelText = this.getAttribute('label');

    // Creamos label
    const label = document.createElement("label");
    if (this.hasAttribute("label")) {
      label.setAttribute("label", this.getAttribute("label"));
    }
    label.setAttribute('t', labelText)
    label.textContent = labelText;

    // Creamos input
    const id = this.getAttribute('id') || generate_unique_dom_id();
    const input = document.createElement("input");
    input.classList.add("case-title-input");
    input.setAttribute('t-placeholder', this.getAttribute('t-placeholder') || this.getAttribute('placeholder') || '');
    input.setAttribute('id', id);

    // Pasamos todos los atributos menos "t" y "class"
    [...this.attributes].forEach(attr => {
      if (attr.name !== "class") {
        input.setAttribute(attr.name, attr.value);
      }
    });

    // Reemplazamos <plus-title> con label + input
    const wrapper = document.createDocumentFragment();
    wrapper.appendChild(label);
    wrapper.appendChild(input);

    this.replaceWith(wrapper);
  }
}

       
class PlusQuantity extends HTMLElement {
  static formAssociated = true;

  constructor() {
    super();
    this.internals = this.attachInternals();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
  }

  static get observedAttributes() {
    return ['value', 'min', 'max', 'step', 'label', 'name'];
  }

  // Getters y Setters
  get value() { return this.getAttribute('value') || 0; }
  set value(val) {
    const min = parseFloat(this.getAttribute('min')) || -Infinity;
    const max = parseFloat(this.getAttribute('max')) || Infinity;

    // We ensure that the value is within limits and is a number
    let newValue = Math.max(min, Math.min(max, parseFloat(val) || min));
    
    this.setAttribute('value', newValue);
    if (this.input) this.input.value = newValue;
    this.internals.setFormValue(newValue);

    // Update the visual state of the buttons
    this.updateButtonState();
  }

  updateValue(delta) {
    const step = parseFloat(this.getAttribute('step')) || 1;
    this.value = parseFloat(this.value) + (delta * step);
  }

  // Disable buttons if the limit is reached
  updateButtonState() {
    if(!this.btnMinus || !this.btnPlus) return;
    const min = parseFloat(this.getAttribute('min')) || -Infinity;
    const max = parseFloat(this.getAttribute('max')) || Infinity;
    const currentVal = parseFloat(this.value);

    this.btnMinus.classList.toggle('disabled', currentVal <= min);
    this.btnPlus.classList.toggle('disabled', currentVal >= max);
  }

  render() {
    const label = this.getAttribute('label') || 'Cantidad';
    const min = this.getAttribute('min') || 0;
    const max = this.getAttribute('max') || 100;
    const step = this.getAttribute('step') || 1;

    this.shadowRoot.innerHTML = `
      <style>
        /* Reset and base styles for adaptability */
        :host {
          display: block;
          width: 100%; /* Ocupa todo el ancho disponible */
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          box-sizing: border-box;
        }
        *, *::before, *::after { box-sizing: inherit; }

        /* Main container, white card style */
        .container {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: #ffffff;
          padding: 1rem 1.5rem; 
          border-radius: 12px; 
          transition: box-shadow 0.3s ease;
        }
        
        /* Label text on the left */
        .label {
          font-weight: 500;
          color: #4a4a4a;
          font-size: 1rem;
          margin-right: 1rem;
        }

        /* Container of controls on the right */
        .controls {
          display: flex;
          align-items: center;
          gap: 1rem; /* Space between icons and number */
        }

        /* Style the numeric input to look like text on a line */
        input {
          width: 40px;
          border: none;
          border-bottom: 1px solid #e0e0e0;
          background: transparent;
          text-align: center;
          font-size: 1rem;
          font-weight: 400;
          color: #333;
          padding-bottom: 4px;
          outline: none;
          -moz-appearance: textfield;
        }

        /* Remove native spinners in Webkit/Chrome */
        input::-webkit-outer-spin-button,
        input::-webkit-inner-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }

        /* Button (icon) styles */
        button {
          background: none;
          border: none;
          padding: 0;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: ${colors.color_company}; 
          transition: color 0.2s, transform 0.1s;
        }
        button:hover { color: ${colors.color_company_hover}; }
        button:active { transform: scale(0.95); }

        /* SVG Icons styling */
        .icon-svg {
            width: 26px;
            height: 26px;
            fill: currentColor;
        }
        
        /* Specific style for the minus button to make it gray as in the photo */
        #btn-minus { color: #a0a0a0; }
        #btn-minus:hover { color: #7f7f7f; }

        /* Visually disabled status */
        button.disabled {
          color: #e0e0e0 !important;
          cursor: not-allowed;
          pointer-events: none;
        }
      </style>

      <div class="container">
        <span class="label">${label}</span>
        <div class="controls">
          <button type="button" id="btn-minus" aria-label="Disminuir cantidad">
            <svg class="icon-svg" viewBox="0 0 24 24">
              <path d="M12,2A10,10 0 1,0 22,12A10,10 0 0,0 12,2Zm4,11H8a1,1 0 0,1 0-2h8a1,1 0 0,1 0,2Z"/>
            </svg>
          </button>

          <input type="number" 
                 value="${this.value}" 
                 min="${min}" 
                 max="${max}" 
                 step="${step}">

          <button type="button" id="btn-plus" aria-label="Aumentar cantidad">
             <svg class="icon-svg" viewBox="0 0 24 24">
               <path d="M12,2A10,10 0 1,0 22,12A10,10 0 0,0 12,2Zm5,11H13v4a1,1 0 0,1-2,0V13H7a1,1 0 0,1 0-2h4V7a1,1 0 0,1 2,0v4h4a1,1 0 0,1 0,2Z"/>
             </svg>
          </button>
        </div>
      </div>
    `;

    this.input = this.shadowRoot.querySelector('input');
    this.btnMinus = this.shadowRoot.getElementById('btn-minus');
    this.btnPlus = this.shadowRoot.getElementById('btn-plus');

    //Initialize button value and state
    this.internals.setFormValue(this.value);
    this.updateButtonState();

    // Event Listeners
    this.btnMinus.onclick = () => this.updateValue(-1);
    this.btnPlus.onclick = () => this.updateValue(1);
    this.input.onchange = (e) => { this.value = e.target.value; };
  }
}

class SearchBar extends HTMLElement {
  constructor() {
    super();
    this._typingTimer = null;
    this._doneTypingInterval = 500;
  }

  connectedCallback() {
    const labelTextInfo = this.getAttribute("label") || "";
    const labelText = labelTextInfo || "message.search";
    const name = this.getAttribute("name") || "";
    const placeHolderText = this.getAttribute("placeholder") || "";
    const required = this.hasAttribute("required");
    const readOnly = this.hasAttribute("readonly");
    const disabled = this.hasAttribute("disabled");
    const value = this.getAttribute("value") || "";

    //we will see if the proggramer added a placeholder
    const placeholder = placeHolderText || "message.search";

    const tPlaceholderKey = placeHolderText || "message.search";

    //create the elements
    const wrapper = document.createElement("div");
    wrapper.classList.add("search-wrapper");

    //her we will to create a label 
    const label = document.createElement("label");
    label.setAttribute('t', labelText);
    label.textContent = window.translate_text(labelTextInfo);

    //her we will to create the inputs
    const input = document.createElement("input");
    input.type = "search";
    input.classList.add("search-input");
    input.name = name;
    input.id = this.getAttribute("id") || generate_unique_dom_id();
    input.placeholder = window.translate_text(placeholder);
    input.value = value;
    input.setAttribute("t-placeholder", tPlaceholderKey);


    if (required) input.required = true;
    if (readOnly) input.readOnly = true;
    if (disabled) input.disabled = true;

    const icon = document.createElement("i");
    icon.className = "fi fi-br-search search-icon";

    wrapper.appendChild(input);
    wrapper.appendChild(icon);

    // Detect attribute function 'function'
    const callbackFnName = this.getAttribute("function-callback");

    if (callbackFnName && typeof window[callbackFnName] === "function") {

      // Debounce input events
      input.addEventListener('input', () => {
        clearTimeout(this._typingTimer);
        this._typingTimer = setTimeout(() => {
          const currentText = input.value;
          window[callbackFnName](currentText);
        }, this._doneTypingInterval);
      });

      //run the function if the user do a enter also
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          clearTimeout(this._typingTimer);
          window[callbackFnName](input.value);
        }
      });
    }

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
      overlay.style.zIndex = currentPopZIndex;

      const popup = document.createElement("div");
      popup.className = "confirm-popup";
      popup.style.zIndex = currentPopZIndex;

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

function get_text_and_keys(struct){
  let text = ''; //is the text to translate exaple: app.label.text 
  let keys = null; //here be the key that we will to remplace in the text. example: { name: 'Edward', count: 3 } or ['Edward', 3]
  

  if (typeof struct === 'string') {
    text = struct;

  } else if (Array.isArray(struct)) {
    text = struct[0];
    keys = struct[1];

  } else if (typeof struct === 'object' && struct !== null) {
    text = struct.text;
    keys = struct.keys;
  }

  return { text, keys };
}

async function show_message_question(title, message) {
  currentPopZIndex += 1

  //now update the z index of the menu of the apps
  const appMenu = document.getElementById('appMenu');
  let currentZIndex = window.getComputedStyle(appMenu).getPropertyValue('z-index');

  //we will see if have a z-index, if have we will aument 1 to his value
  if (!isNaN(currentZIndex)) {
    let newZIndex = currentZIndex + 1;
    appMenu.style.zIndex = newZIndex;
  } else {
    //if not have a z-index, we will to create a z-index
    appMenu.style.zIndex = 1000;
  }

  //Here we will to see if the programmer have a struct in the text
  //-> show_message_question(['Hello ${name}, you have ${count} messages', { name: 'Edward', count: 3 }], ['Hello ${}, you have ${} messages', ['Edward', 3 ]])
  let titleStruct=get_text_and_keys(title);
  let messageStruct=get_text_and_keys(message);

  const result = await ConfirmDialog.show(window.translate_text(titleStruct.text, titleStruct.keys), window.translate_text(messageStruct.text, messageStruct.keys));
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
    const col = parseInt(this.getAttribute('col')) || 4;
    const colSidebar = Math.max(1, Math.min(col, 11));
    const colContent = 12 - colSidebar;

    const modules = Array.from(this.querySelectorAll('plus-module'));
    const names = modules.map(m => m.getAttribute('name'));
    const icons = modules.map(m => m.getAttribute('icon') || '');
    const descs = modules.map(m => m.getAttribute('desc') || '');
    const onVisibles = modules.map(m => m.getAttribute('on-visible') || null); // Save the functions 

    let lastWidth = window.innerWidth; // We define lastWidth to avoid errors

    // Sidebar
    const sidebar = document.createElement('div');
    sidebar.className = 'plus-modules-sidebar';
    sidebar.style.width = `${(colSidebar / 12) * 100}%`;
    sidebar.style.transition = 'all 0.3s ease';

    const ul = document.createElement('ul');

    names.forEach((name, i) => {
      const li = document.createElement('li');
      li.className = i === 0 ? 'active' : '';
      li.dataset.index = i;

      li.style.display = 'flex';
      li.style.alignItems = 'center';
      li.style.justifyContent = 'space-between';
      li.style.padding = '10px 12px';
      li.style.cursor = 'pointer';
      li.style.borderBottom = '1px solid #eee';

      const leftContainer = document.createElement('div');
      leftContainer.style.display = 'flex';
      leftContainer.style.alignItems = 'center';
      leftContainer.style.gap = '12px';

      if (icons[i]) {
        const iconSpan = document.createElement('i');
        iconSpan.className = `fi ${icons[i]}`;
        iconSpan.style.fontSize = '1.5em';
        iconSpan.style.width = '30px';
        iconSpan.style.color = colors.color_company;
        iconSpan.style.textAlign = 'center';
        leftContainer.appendChild(iconSpan);
      }

      const textContainer = document.createElement('div');
      textContainer.className = 'plus-modules-text';
      const translateText = window.translate_text ? window.translate_text(name) : name;

      const pName = document.createElement('p');
      pName.className = 'plus-modules-name';
      pName.style.margin = '0';
      pName.style.fontWeight = '500';
      pName.textContent = translateText;
      pName.setAttribute('t', name);
      textContainer.appendChild(pName);

      if (descs[i]) {
        const pDesc = document.createElement('p');
        pDesc.className = 'plus-modules-desc';
        pDesc.style.margin = '0';
        pDesc.style.fontSize = '0.8em';
        pDesc.style.color = `${colors.color_second}`;
        pDesc.textContent = descs[i];
        textContainer.appendChild(pDesc);
      }

      leftContainer.appendChild(textContainer);
      li.appendChild(leftContainer);

      const arrow = document.createElement('i');
      arrow.className = 'fi fi-rr-angle-right';
      arrow.style.fontSize = '1em';
      li.appendChild(arrow);

      ul.appendChild(li);
    });

    sidebar.appendChild(ul);

    // Content
    const content = document.createElement('div');
    content.className = 'plus-modules-content';
    content.style.width = `${(colContent / 12) * 100}%`;
    content.style.padding = '20px';
    content.style.position = 'relative';
    content.style.transition = 'all 0.3s ease';

    const panelContainer = document.createElement('div');
    panelContainer.className = 'plus-modules-module-panel-container';
    content.appendChild(panelContainer);

    const panels = modules.map((m, i) => {
        const panel = document.createElement('div');
        panel.className = 'plus-modules-module-panel';
        
        //We move the children of the original to the panel directly.
        while (m.firstChild) {
            panel.appendChild(m.firstChild);
        }

        panel.style.display = i === 0 ? 'block' : 'none';
        panelContainer.appendChild(panel);
        return panel;
    });

    // X button for mobile
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'X';
    closeBtn.style.position = 'absolute';
    closeBtn.style.top = '10px';
    closeBtn.style.right = '10px';
    closeBtn.style.display = 'none';
    closeBtn.style.width = '32px';
    closeBtn.style.height = '32px';
    closeBtn.style.border = 'none';
    closeBtn.style.background = `${colors.color_company}`;
    closeBtn.style.color = 'white';
    closeBtn.style.fontWeight = 'bold';
    closeBtn.style.fontSize = '16px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
    closeBtn.style.transition = 'all 0.2s ease';

    content.appendChild(closeBtn);

    this.classList.add('plus-modules-host');

    this.replaceChildren(sidebar, content);

    // --- FUNCTION EXECUTION LOGIC ---
    const triggerVisibleFunction = (index) => {
        const scriptStr = onVisibles[index];
        if (scriptStr) {
            try {
                //This executes the string as code (in: "initial schedules(2)")
                const execute = new Function(scriptStr);
                execute();
            } catch (e) {
                console.error("Error al ejecutar on-visible:", scriptStr, e);
            }
        }
    };

    //Run for the first default module
    triggerVisibleFunction(0);

    // Mobile features
    const showContentMobile = () => {
      if (window.innerWidth < 768) {
        sidebar.style.width = '0';
        sidebar.style.display = 'none';
        content.style.width = '100%';
        content.style.display = 'block';
        closeBtn.style.display = 'block';
      }
    };

    const showSidebarMobile = () => {
      if (window.innerWidth < 768) {
        sidebar.style.width = '100%';
        sidebar.style.display = 'block';
        content.style.display = 'none';
        closeBtn.style.display = 'none';
      }
    };

    // Click en módulo
    ul.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        ul.querySelectorAll('li').forEach(i => i.classList.remove('active'));
        li.classList.add('active');
        const index = li.dataset.index;

        panels.forEach((p, j) => {
          p.style.display = j == index ? 'block' : 'none';
        });

        // Llamamos a la función cuando se hace click
        triggerVisibleFunction(index);
        showContentMobile();
      });
    });

    closeBtn.addEventListener('click', () => {
      showSidebarMobile();
    });

    window.addEventListener('resize', () => {
      const newWidth = window.innerWidth;
      if (Math.abs(newWidth - lastWidth) < 50) return;
      lastWidth = newWidth;

      if (newWidth >= 768) {
        sidebar.style.width = `${(colSidebar / 12) * 100}%`;
        sidebar.style.display = 'block';
        content.style.width = `${(colContent / 12) * 100}%`;
        content.style.display = 'block';
        closeBtn.style.display = 'none';
      } else {
        showSidebarMobile();
      }
    });

    if (window.innerWidth < 768) {
      showSidebarMobile();
    }
  }
}

class PlusModule extends HTMLElement {
  connectedCallback() {
    this.classList.add('plus-modules-module');
  }
}


class PlusSelect extends HTMLElement {
  constructor() {
    super();
    this._hiddenInput = null;
    this._selectText = null;
    this._selectElement = null;
    this._thisSlectSendDataToTheServer = false;
    this._textSelected = null;
    this._textLabelTranslate=null;
    this._method = 'GET'
  }

  async connectedCallback() {
    const originalSelect = this.cloneNode(true);
    this._selectElement = originalSelect;

    this._method = this.getAttribute('method') || 'GET'

    //get the information that the programmer added to the select
    const textLabel = this.getAttribute('t') || this.getAttribute('label') || '';
    const textLabelTranslate = window.translate_text(textLabel); //translate the text of the label
    

    const name = this.getAttribute('name') || '';
    const isRequired = this.hasAttribute('requerid');

    //create a label of text of that the user can know that need do
    const thisLabelHaveAMessage = this.getAttribute('message');
    let label;

    //get the value for if the programmer would like show other message that not be the default
    const tilteBtn = this.getAttribute('btn_delete_title') || '';
    const textBtn = this.getAttribute('btn_delete_text') || '';
    this._textLabelTranslate=textLabelTranslate;
    
    //her we will know if the programmer need show a message to the user
    if (thisLabelHaveAMessage) {
      //if the programmer need show a messga, we will to create the special label when the information that need
      label = document.createElement('info-label');
      label.setAttribute('label', textLabel)
      label.setAttribute('t', textLabel)
      label.textContent = textLabelTranslate;
      label.setAttribute('message', thisLabelHaveAMessage)
    } else {
      //if the programmer not need show a message, we will create a message normal
      label = document.createElement('label');
      label.setAttribute('label', textLabel)
      label.setAttribute('t', textLabel);
      label.textContent = textLabelTranslate;
    }



    //Create main wrapper
    const wrapper = document.createElement('div');
    wrapper.classList.add('plus-select-wrapper');

    //Create select visible container
    const select = document.createElement('div');
    select.classList.add('plus-select-select');

    const valueShow = this.getAttribute('value') || textLabel; //this is for know what value we will show in the select when the user not selected nothing

    select.innerHTML = `
      <span class="plus-select-selected-text" t='${valueShow}'>${textLabelTranslate}</span>
      <i class="fi fi-rr-angle-small-right plus-select-icon"></i>
    `;
    this._selectText = select.querySelector('.plus-select-selected-text'); //save the span of the text that was selected
    this._textSelected = this.getAttribute('data-text') || null; //save the text that was selected

    //Create options popup
    const popup = document.createElement('div');
    popup.classList.add('plus-select-popup');

    // Create the container of the seeker 
    const searchWrapper = document.createElement('div');
    searchWrapper.classList.add('plus-select-search-wrapper');
    const txtSearch = window.t('message.search') || 'search...'; //get the translate global of a seeker

    //we will see if exist a pop for add a new data to this select 
    if (this.hasAttribute('add')) {
      const functionName = this.getAttribute('add');

      searchWrapper.innerHTML = `
      <i class="fi fi-rs-search"></i>
      <input type="text" placeholder="${txtSearch}">
      <button class="search-add-btn" title="${window.t('message.add')}" type="button">
        <i class="fi fi-br-plus"></i>
      </button>
    `;

      // Asegúrate de que el DOM ya tiene el botón antes de agregar el evento
      const addButton = searchWrapper.querySelector('.search-add-btn');
      if (addButton && typeof window[functionName] === 'function') {
        addButton.addEventListener('click', window[functionName]);
      }
    } else {
      //if not exist the attribute 'add' we only show the input
      searchWrapper.innerHTML = `
        <i class="fi fi-rs-search"></i>
        <input type="text" placeholder="${txtSearch}">
      `;
    }


    const searchInput = searchWrapper.querySelector('input');

    //firsrt we will see if this select, can update 
    const thisSlectSendDataToTheServer = this.hasAttribute('link');
    this._thisSlectSendDataToTheServer = thisSlectSendDataToTheServer;

    //also we will see if this data can be edit or delete 
    const delete_data = this.hasAttribute('delete_data');
    const edit_data = this.hasAttribute('edit_data');
    const functionDelete = this.getAttribute('delete_data')?.replace('()', ''); //this is for remplace the () of the function example delete_customer() to delete_customer
    const functionEdit = this.getAttribute('edit_data')?.replace('()', '');
    const linkDelete = this.getAttribute('delete_data')?.replace('()', '');
    const link = this.getAttribute('link');
    //Create the container of the <option>
    const slotOptions = this.querySelectorAll('option');
    let options = [];

    //--this is when in the frontend the proggramer added options
    slotOptions.forEach(opt => {
      //get the text of the iformation
      const optionText = opt.getAttribute('t') || opt.textContent || '';

      //we will see if the proggramer need translate this option
      let textTranlate = window.translate_text(optionText); //translate the text that exist 



      //her we will create the container of the div of the options
      const div = document.createElement('div');
      div.classList.add('plus-select-option');
      div.setAttribute('t', optionText);

      div.textContent = textTranlate; //update the text that we will show in the option
      div.dataset.value = opt.getAttribute('value') || textTranlate; //add the value

      //add the option to the select
      options.push(div);
      popup.appendChild(div);
    });


    //----
    slotOptions.forEach(opt => opt.remove()); //clear the DOOM of the after options



    //Insert search before options
    popup.insertBefore(searchWrapper, popup.firstChild);

    //Create hidden input
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = name;
    hiddenInput.id = this.getAttribute('id') || generate_unique_dom_id();
    if (isRequired) hiddenInput.required = true;
    this._hiddenInput = hiddenInput;

    //Click event on select visible. This is when the user do clic in the select.
    let left = 0;
    let width = 0;
    select.addEventListener('click', async () => {
      popup.classList.toggle('active');
      popup.style.zIndex = currentPopZIndex;
      searchInput.focus();

      if (popup.classList.contains('active')) {
        positionPopup(select, popup);
        positionPopup(select, popup);
      }


      if (thisSlectSendDataToTheServer) {
        await update_option_for_the_server('');
      }
    });
    this._selectText = select.querySelector('.plus-select-selected-text');

    // Event clic in options
    options.forEach(opt => {
      opt.addEventListener('click', () => {
        select.querySelector('.plus-select-selected-text').textContent = opt.textContent;
        hiddenInput.value = opt.dataset.value;
        popup.classList.remove('active');
        searchInput.value = '';
        filterOptions('');
        this.dispatchEvent(new Event('change', { bubbles: true }));
      });
    });


    // Filter
    let debounceTimer;
    searchInput.addEventListener('input', async e => {
      //we will see if the select will send data to the server
      if (thisSlectSendDataToTheServer) {
        clearTimeout(debounceTimer);
        const value = e.target.value.toLowerCase();
        debounceTimer = setTimeout(async () => {
          await filterOptions(value);
        }, 500); // 500ms after stopping typing
      } else {
        await filterOptions(e.target.value.toLowerCase()); //if not send data to the server, we will filter to the instant 
      }
    });

    function positionPopup(selectElement, popupElement) {
      // get the position in the screen
      const rect = selectElement.getBoundingClientRect();
      const popupRect = popupElement.getBoundingClientRect();

      // position for default of the select 
      let left = rect.left + window.scrollX + rect.width;
      let top = rect.bottom + window.scrollY - 43;

      // Check if the popup goes off the screen (right side)
      if (left + popupRect.width > window.innerWidth) {
          // If it goes outside, move it to the left of the select
          //here we will to calculate the excess of the border
          const overflowRight = left + popupRect.width - window.innerWidth;

          // Adjust left by subtracting the excess
          left = left - overflowRight-16;
      }


      //here we will see if the user be in the cellphone 
      if (window.innerWidth <= 768) {
        popupElement.style.width = `${window.innerWidth-64}px`;
        left = rect.left + window.scrollX;
        top = rect.bottom + window.scrollY + 8;
      }

      //update the positions
      popupElement.style.left = `${left}px`;
      popupElement.style.top = `${top}px`;
    }

    async function filterOptions(term) {
      //Standardize the search term: lowercase letters and no accents
      const normalizedTerm = term
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, ""); // remove accents and diacritical marks

      if (thisSlectSendDataToTheServer) {
        await update_option_for_the_server(term);
      } else {
        options.forEach(opt => {
          // Standardize the text of the option
          const normalizedText = opt.textContent
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");

          opt.style.display = normalizedText.includes(normalizedTerm) ? 'block' : 'none';
        });
      }
    }

    async function update_option_for_the_server(textFilter) {
      //after of send the message to the server, we will clear all the container of the previous options
      clear_option_select();

      //her we will create a loading for that the user know that the app is search his data
      const loadingDiv = document.createElement('div');
      loadingDiv.classList.add('plus-select-option');
      loadingDiv.textContent = window.t('info.loading');
      options.push(loadingDiv);
      popup.appendChild(loadingDiv);

      //if have a link of search, send this information to the server for get the information. 
      //the that the server can retur is {id:0, text:'name', color: '#ffff}
      //send the information to the server and get his answer
      const result = await window.send_message_to_the_server(link, { query: textFilter }, false, 'GET'); //with this have a error for translate the label

      //when get the answer of the server, other clear all the container 
      clear_option_select();

      //we will see if we can add the new customer
      if (result.success) {
        //get the data that send the server
        const anserServer = result.answer;

        //read all the data that the server send 
        anserServer.forEach(data => {
          const div = document.createElement('div');
          div.classList.add('plus-select-option');
          div.dataset.value = data.id;

          // contenedor horizontal (texto + acciones)
          const contentContainer = document.createElement('div');
          contentContainer.classList.add('plus-select-content');

          //square of color
          let redSquare;
          if (data.color) {
            redSquare = document.createElement('span');
            redSquare.style.display = 'inline-block';
            redSquare.style.width = '12px';
            redSquare.style.height = '12px';
            redSquare.style.backgroundColor = data.color;
            redSquare.style.marginRight = '8px'; // space between square and text
            redSquare.style.verticalAlign = 'middle';
          }

          const photo=data.photo || data.avatar; 
          if (photo) {
            const imgThumb = document.createElement('img');
            imgThumb.src = photo;
            imgThumb.alt = data.text || data.name;
            imgThumb.loading = 'lazy';
            imgThumb.style.width = '24px';
            imgThumb.style.height = '24px';
            imgThumb.style.objectFit = 'cover';
            imgThumb.style.borderRadius = '4px';
            imgThumb.style.marginRight = '8px';
            imgThumb.style.verticalAlign = 'middle';

            //if the image not exit, show a image for default
            imgThumb.onerror = function() {
              this.onerror = null;
              this.src = window.STATIC_URLS.imageDefault; //path for default
            };

            contentContainer.appendChild(imgThumb);
          }

          // text
          const textSpan = document.createElement('span');
          textSpan.classList.add('option-text');
          textSpan.textContent = data.text || data.name;

          // Contenedor de botones
          const actionsContainer = document.createElement('div');
          actionsContainer.classList.add('plus-select-actions');

          if (edit_data) {
            const editBtn = document.createElement('button');
            editBtn.setAttribute('type', 'button');
            editBtn.classList.add('edit-btn');
            editBtn.innerHTML = '<i class="fi fi-sr-pencil"></i>';
            editBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              window[functionEdit](data.id); // run the function with the ID
            });
            actionsContainer.appendChild(editBtn);
          }

          if (delete_data) {
            //create the button of delete and hsi characters
            const deleteBtn = document.createElement('button');
            deleteBtn.setAttribute('type', 'button');
            deleteBtn.setAttribute('message', '')
            //deleteBtn.classList.add('delete-btn');
            deleteBtn.innerHTML = '<i class="fi fi-sr-trash"></i>';
            deleteBtn.addEventListener('click', async (e) => {
              e.stopPropagation();

              //her we will see if the user delete the item
              if (await plus_delete_with_help_button(data.id, linkDelete, tilteBtn, textBtn)) {
                await update_option_for_the_server(''); //update the input when the user delete a item
              }
            });
            actionsContainer.appendChild(deleteBtn);
          }

          // add the option
          if (data.color) {
            contentContainer.appendChild(redSquare);
          }
          contentContainer.appendChild(textSpan);
          if (edit_data || delete_data) {
            contentContainer.appendChild(actionsContainer);
          }
          div.appendChild(contentContainer);

          // Option selection event
          div.addEventListener('click', () => {
            select.querySelector('.plus-select-selected-text').textContent = data.text || data.name;
            hiddenInput.value = data.id;
            popup.classList.remove('active');
            searchInput.value = '';
            filterOptions('');
            this.dispatchEvent(new Event('change', { bubbles: true }));
          });

          options.push(div);
          popup.appendChild(div);
        });
      } else {
        console.error(result.message || 'error to get information of the server for the select')
        const text = t('error.general'); //if exit a error to connect with the server show a message 

        //now we will create the container of the div of the options
        const div = document.createElement('div');
        div.classList.add('plus-select-option');

        div.textContent = text;

        //add the option to the select
        options.push(div);
        popup.appendChild(div);
      }
    }

    function clear_option_select() {
      options.forEach(opt => opt.remove());
      options = [];
    }


    // Clouse if the user do clic outside 
    document.addEventListener('click', (e) => {
      if (!wrapper.contains(e.target)) {
        popup.classList.remove('active');
      }
    });


    //show structure of the label
    wrapper.appendChild(label);
    wrapper.appendChild(select);
    wrapper.appendChild(hiddenInput);
    this.appendChild(wrapper);

    // mover el popup al body para que no rompa el layout
    document.body.appendChild(popup);

    //if the select have a value for dafault
    const defaultValue = this.getAttribute('value');
    this.setValue(defaultValue);
  }

  setValue(value, text = null) {
    if (!this._selectElement) return;
    
    if (this._textSelected) {
      this._selectText.setAttribute('t', this._textSelected);
      this._selectText.textContent = this._textSelected;
      this._hiddenInput.value = value;
      return; //if the user selected a text, we not will update the select
    }
    
    //her we will see if exist the information of the select
    const option = Array.from(this._selectElement.querySelectorAll('option'))
      .find(opt => opt.getAttribute('value') === value + '');


      
      
    //her we will verifiy if exist this option in the select
    if (option) {
      //if the option exist in the select, we will get his information and set it in the hidden input and the select text
      if (this._hiddenInput) {
        this._hiddenInput.value = option.getAttribute('value');
      }

      if (this._selectText) {
        const text = this._textSelected || option.getAttribute('t') || option.getAttribute('data-text') || option.textContent;
        this._selectText.setAttribute('t', text);
        this._selectText.textContent = window.translate_text(text);
      }
    } else {
      
      //if not exist in the select of the options is because is a data of a tabla of search 
      if (this._thisSlectSendDataToTheServer) {
        this._hiddenInput.value = value;

        var info;
        if(option!=null){
          info = text || value || option.getAttribute('data-text');
        }else{
          info = text || value || window.translate_text(this._textLabelTranslate);
        }

        this._selectText.setAttribute('t', info);
        this._selectText.textContent = info;
      }
    }
  }

  //this return the value of the hidden input
  getValue() {
    return this._hiddenInput ? this._hiddenInput.value : null;
  }

  //this is for restart the form when a form be send
  reset() {
    if (this._hiddenInput) {
      this._hiddenInput.value = "";
    }
    if (this._selectText) {
      const defaultLabel = this.getAttribute("t") || this.getAttribute("label") || "";
      this._selectText.textContent = window.translate_text(defaultLabel);
    }
  }
}

class PlusCountry extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    //List of countries with ISO code and name
    const countries = [
      // América del Norte
      { code: "US", name: "United States" },
      { code: "CA", name: "Canada" },
      { code: "MX", name: "México" },

      // América Latina
      { code: "AR", name: "Argentina" },
      { code: "BO", name: "Bolivia" },
      { code: "CL", name: "Chile" },
      { code: "CO", name: "Colombia" },
      { code: "CR", name: "Costa Rica" },
      { code: "CU", name: "Cuba" },
      { code: "DO", name: "Dominican Republic" },
      { code: "EC", name: "Ecuador" },
      { code: "SV", name: "El Salvador" },
      { code: "GT", name: "Guatemala" },
      { code: "HN", name: "Honduras" },
      { code: "NI", name: "Nicaragua" },
      { code: "PA", name: "Panama" },
      { code: "PY", name: "Paraguay" },
      { code: "PE", name: "Peru" },
      { code: "UY", name: "Uruguay" },
      { code: "VE", name: "Venezuela" },

      // Europa
      { code: "ES", name: "Spain" },
      { code: "PL", name: "Poland" }
    ];

    const flagEmojiMap = {
      US: '🇺🇸', CA: '🇨🇦', MX: '🇲🇽',
      AR: '🇦🇷', BO: '🇧🇴', CL: '🇨🇱', CO: '🇨🇴', CR: '🇨🇷', CU: '🇨🇺',
      DO: '🇩🇴', EC: '🇪🇨', SV: '🇸🇻', GT: '🇬🇹', HN: '🇭🇳', NI: '🇳🇮',
      PA: '🇵🇦', PY: '🇵🇾', PE: '🇵🇪', UY: '🇺🇾', VE: '🇻🇪',
      ES: '🇪🇸', PL: '🇵🇱'
    };

    // create the plus-select
    const plusSelect = document.createElement('plus-select');
    const value = this.getAttribute('value') || 'MX';
    // Pass attributes from the plus-country tag to the plus-select tag
    plusSelect.setAttribute('label', 'info.select-a-country')
    if (this.hasAttribute('t')) plusSelect.setAttribute('t', this.getAttribute('t') || 'info.select-a-country');
    if (this.hasAttribute('name')) plusSelect.setAttribute('name', this.getAttribute('name'));
    if (this.hasAttribute('requerid')) plusSelect.setAttribute('requerid', '');
    if (this.hasAttribute('link')) plusSelect.setAttribute('link', this.getAttribute('link'));

    //Add all country options
    countries.forEach(country => {
      const option = document.createElement('option');
      option.value = country.code;
      option.setAttribute('t', country.name);

      option.textContent = `${flagEmojiMap[country.code] || ''} ${country.name}`;
      plusSelect.appendChild(option);
    });

    this.replaceWith(plusSelect);
    setTimeout(() => {
      plusSelect.setValue(value);
    }, 0);
  }
}

function set_value_plus_select(id, newValue, newText = null) {
  const mySelect = document.getElementById(id);
  if (!mySelect) return;

  if (typeof mySelect.setValue === 'function') {
    mySelect.setValue(newValue, newText);
  }
}

function get_value_plus_select(id) {
  const mySelect = document.getElementById(id);
  if (!mySelect) return null;

  if (typeof mySelect.getValue === 'function') {
    return mySelect.getValue();
  }
  return null;
}

async function plus_delete_with_help_button(id, link, title = '', message = '' ,title_success='', message_success='') {
  //her we will see if the proggramer would like show other message that not be the default
  const titleToTranslate = title || 'info.confirm_delete';
  const messageToTranslate = message || 'info.description_delete';


  const titleDelete = window.translate_text(titleToTranslate);
  const messageDelete = window.translate_text(messageToTranslate);

  if (await show_message_question(titleDelete, messageDelete)) {
    const answer = await send_message_to_the_server(link, { id }, true);
    if (answer.success) {
      const title=title_success || 'success.deleted'
      const message=message_success || 'success.deleted'
      show_alert('success', title, message)
      return true;
    } else {
      show_alert('alert', window.t('error.general'), window.t('error.to_delete'), answer.error)
      console.error(answer.message || 'Error to delete the item in the server');
      console.error(answer.error);
    }
  }

  return false;
}

class PlusSwitch extends HTMLElement {
  constructor() {
    super();
    this._checkbox = null;
    this._rendered = false; // Flag for evit the duplicates
  }

  connectedCallback() {
    // if already rendered, do nothing
    if (this._rendered) return; 

    //first we will get the text that the user would like show in the switch 
    const text = this.getAttribute('text') || ''; //first we will get the text that the user have save in the label
    const t = this.getAttribute('t') || text; //if the user would like add the label of translate , else save the text that added in the atributte text
    const textTranlsate = window.translate_text(t); //her translate the text. This allows trasnlate the text of two forms


    const name = this.getAttribute('name') || ''; //get the name for if the switch is in a form 

    //we will see if the proggramer would like that the switch is selected 
    const valueCheck = this.getAttribute('checked') || this.getAttribute('value') || false;
    const isChecked = is_true(valueCheck);

    // Create parent container
    const container = document.createElement('div');

    const wrapper = document.createElement('div');
    wrapper.classList.add('plus-switch');

    let labelText = document.createElement('span');
    labelText.classList.add('plus-switch-label');
    labelText.setAttribute('t', t);

    // Check if an icon is defined
    const iconClass = this.getAttribute('icon');
    if (iconClass) {
      const iconEl = document.createElement('i');
      iconEl.className = iconClass;
      iconEl.style.marginRight = '6px'; // spacing between icon and text
      iconEl.style.fontSize = '16px';
      iconEl.style.color = 'var(--primary)';
      labelText.appendChild(iconEl);
    }

    // Add text after icon
    labelText.appendChild(document.createTextNode(textTranlsate));

    //we will see if the proggramer wants show a label with message. The label with message is show 
    const labelTitle = this.getAttribute('lable') || text;
    const message = this.getAttribute('message');
    if (message) {
      //if the programmer need show a messga, we will to create the special label when the information that need
      const infoLabel = document.createElement('info-label');
      infoLabel.setAttribute('label', labelTitle);
      infoLabel.setAttribute('message', message);

      container.appendChild(infoLabel);
    }

    // Create visual switch
    const switchContainer = document.createElement('label');
    switchContainer.classList.add('plus-switch-toggle');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = isChecked;
    checkbox.name = name;
    checkbox.id = this.getAttribute('id') || generate_unique_dom_id();
    this._checkbox = checkbox;

    const slider = document.createElement('span');
    slider.classList.add('plus-switch-slider');

    switchContainer.appendChild(checkbox);
    switchContainer.appendChild(slider);

    // Adding elements to the wrapper
    wrapper.appendChild(labelText);
    wrapper.appendChild(switchContainer);

    container.appendChild(wrapper);

    // Replace the original label
    if (this.hasAttribute('id')) {
      //this.removeAttribute('id');
    }

    checkbox.id = (this.getAttribute('id') || generate_unique_dom_id()) + "_checkbox";

    //this.replaceWith(container);
    this.appendChild(container);

    //her we will add a event listener
    const eventOnclick = this.getAttribute('onclick');
    checkbox.addEventListener('change', (e) => {
      const status = this._checkbox ? this._checkbox.checked : false;

      //her we will see if exist the function and run the function with the status of the check
      if (eventOnclick && typeof window[eventOnclick] === 'function') {
        window[eventOnclick](status);
      }
    });

    this._rendered = true; // mark as rendered
  }

  setChecked(value) {
    if (this._checkbox) {
      this._checkbox.checked = value;
    }
  }

  getChecked() {
    return this._checkbox ? this._checkbox.checked : false;
  }
}

//her we will get the information of the status of the switch
function get_status_plus_switch(id) {
  const mySwitch = document.getElementById(id);
  if (!mySwitch) return;

  // her we will see if the component has a shadowRoot
  const shadow = mySwitch.shadowRoot;
  if (!shadow) return;

  const input = shadow.getElementById(id);
  return input.checked ? input.checked : false;
}

function set_status_plus_switch(id, newValue) {
  const mySwitch = document.getElementById(id);
  if (!mySwitch) return;

  if (typeof mySwitch.setChecked === 'function') {
    mySwitch.setChecked(newValue);
  }
}


class PlusHelp extends HTMLElement {
  constructor() {
    super();
    this.currentStep = 0;
  }

  connectedCallback() {
    //first we will get the title of the help 
    const title = this.getAttribute('title') || window.t('info.help'); //if the user not added the title, we will show a text for default
    const t = this.getAttribute('t') || title; //first we will see if the proggramer need translate this text
    const titleTranslate = window.translate_text(t); //translate the title

    const dataKey = this.getAttribute('data') || 'default-help';

    //create a button for help to the user
    const button = document.createElement('button');
    button.setAttribute('type', 'button');
    button.textContent = titleTranslate;
    button.classList.add('plus-help-button');

    //her we will create the pop for show help
    const popup = document.createElement('div');
    popup.classList.add('plus-help-popup', 'plus-help-hidden');

    const textButtonAfter = window.t('info.after');
    const textButtonFormer = window.t('info.former');
    popup.innerHTML = `
        <div class="plus-help-header">
          <span class="plus-help-title">${title}</span>
          <button class="plus-help-close" type="button">X</button>
        </div>
        <div class="plus-help-progress" id="plus-help-progress"></div>
        <div class="plus-help-step-container" id="plus-help-content"></div>
        <div class="plus-help-footer">
          <button class="plus-help-nav" id="plus-help-prev" type="button">← ${textButtonFormer}</button>
          <span id="plus-help-status">Paso 1</span>
          <button class="plus-help-nav" id="plus-help-next" type="button">${textButtonAfter} →</button>
        </div>
      `;

    button.addEventListener('click', () => {
      popup.classList.remove('plus-help-hidden');
      this.loadHelpContent(dataKey);
    });

    popup.querySelector('.plus-help-close').addEventListener('click', () => {
      popup.classList.add('plus-help-hidden');
      this.currentStep = 0;
    });

    this.appendChild(button);
    this.appendChild(popup);
  }

  loadHelpContent(key) {
    this.helpData = window.PLUS_HELP_DATA?.[key]?.steps || [];
    this.totalSteps = this.helpData.length;
    this.renderStep();
  }

  renderStep() {
    const content = this.querySelector('#plus-help-content');
    const progress = this.querySelector('#plus-help-progress');
    const status = this.querySelector('#plus-help-status');
    const prevBtn = this.querySelector('#plus-help-prev');
    const nextBtn = this.querySelector('#plus-help-next');

    const not_exist_information_of_help = t('info.not_exist_information_of_help');
    if (!this.helpData.length) {
      content.innerHTML = `<p>${not_exist_information_of_help}</p>`;
      return;
    }

    const step = this.helpData[this.currentStep];

    // Actualiza contenido
    content.innerHTML = `
        <div class="plus-help-step">
          <h3>${step.title}</h3>
          <p>${step.text}</p>
          ${step.image ? `<img loading="lazy" src="${step.image}" class="loadzy plus-help-img" alt="Paso">` : ''}
          ${step.video ? `<iframe class="plus-help-video" loading="lazy" src="https://www.youtube.com/embed/${step.video}" frameborder="0" allowfullscreen></iframe>` : ''}
        </div>
      `;

    // Actualiza barra de pasos
    progress.innerHTML = this.helpData.map((s, i) => `
        <div class="plus-help-progress-item ${i === this.currentStep ? 'active' : ''} ${i < this.currentStep ? 'done' : ''}">
          ${i + 1}
        </div>
      `).join('');

    // Actualiza estado
    const textStep = t('info.step') || 'Step';
    const textOF = t('info.of') || 'of';
    status.textContent = `${textStep} ${this.currentStep + 1} ${textOF} ${this.totalSteps}`;

    // Botones
    prevBtn.disabled = this.currentStep === 0;
    nextBtn.disabled = this.currentStep === this.totalSteps - 1;

    prevBtn.onclick = () => {
      if (this.currentStep > 0) {
        this.currentStep--;
        this.renderStep();
      }
    };

    nextBtn.onclick = () => {
      if (this.currentStep < this.totalSteps - 1) {
        this.currentStep++;
        this.renderStep();
      }
    };

    if (window.loadzy) loadzy(); // Lazy load
  }
}

class CreateHelp {
  constructor(key) {
    this.key = key;
    this.title = '';
    this.message = '';
    this.image = '';
    this.video = '';
  }

  toStepObject() {
    const step = {
      title: this.title,
      text: this.message,
    };

    if (this.image) step.image = this.image;
    if (this.video) step.video = this.video;

    return step;
  }



  add_step({ title = '', message = '', image = '', video = '' }) {
    //her we will see if exist this help, if not exist, we will to create
    if (!window.PLUS_HELP_DATA[this.key]) {
      window.PLUS_HELP_DATA[this.key] = { steps: [] };
    }

    //save the information 
    this.title = title;
    this.message = message;
    this.image = image;
    this.video = video;

    //save the step of help
    window.PLUS_HELP_DATA[this.key].steps.push(this.toStepObject());
  }

  save_help_data() {
    //her we will see if exist this help, if not exist, we will to create
    if (!window.PLUS_HELP_DATA[this.key]) {
      window.PLUS_HELP_DATA[this.key] = { steps: [] };
    }

    window.PLUS_HELP_DATA[this.key].steps.push(this.toStepObject());
  }

}

class PlusSelectDate extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    const nameStart = this.getAttribute('name-start') || 'fecha_inicio';
    const nameEnd = this.getAttribute('name-end') || 'fecha_fin';

    const labelInfo = this.getAttribute('label') || window.t('btn.range_date');
    const t = this.getAttribute('t') || labelInfo;

    const isRequired = this.hasAttribute('required');
    const requiredMark = isRequired ? '*' : '';
    const labelText = window.translate_text(t) + ' ' + requiredMark;
    const lang = navigator.language || 'es-ES';

    const shadow = this.shadowRoot;

    //her we will get the translate of the select 
    const select_range_date = window.t('btn.select_range_date')
    const today = window.t('range.today');
    const last_7_days = window.t('range.last_7_days');
    const current_month = window.t('range.current_month');
    const previous_month = window.t('range.previous_month');
    const custom = window.t('range.custom');
    const success = window.t('message.success');
    const cancel = window.t('message.cancel');

    shadow.innerHTML = `
      <style>
        .plus-select-date-wrapper {
          font-family: sans-serif;
          position: relative;
          width: 100%;
          max-width: 300px;
          margin-bottom: 16px; 
        }

        .plus-select-date-label {
          font-size: 13px;
          color: #555;
          margin-bottom: 4px;
          display: block;
        }

        .plus-select-date-display {
          display: flex;
          align-items: center;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 6px;
          cursor: pointer;
          background: #fff;
        }

        .plus-select-date-display i {
          margin-right: 8px;
        }

        .plus-select-date-popup {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: #fff;
          border: 1px solid #ccc;
          border-radius: 6px;
          margin-top: 4px;
          z-index: 100;
          display: none;
          flex-direction: column;
          padding: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .plus-select-date-popup.active {
          display: flex;
        }

        .plus-select-date-options > div {
          padding: 6px 10px;
          cursor: pointer;
          border-radius: 4px;
        }

        .plus-select-date-options > div:hover {
          background: #f0f0f0;
        }

        .plus-select-date-custom {
          display: none;
          flex-direction: column;
          gap: 8px;
          margin-top: 8px;
        }

        .plus-select-date-custom.active {
          display: flex;
        }

        .plus-select-date-custom input[type="date"] {
          padding: 6px;
          border: 1px solid #ccc;
          border-radius: 4px;
        }

        .plus-select-date-buttons {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
        }

        .plus-select-date-buttons button {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .btn-accept {
          background: var(--primary);
          color: white;
        }

        .btn-cancel {
          background: #ccc;
        }

        .icon-calendar{
          color: var(--primary);
        }
      </style>
      <link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-regular-rounded/css/uicons-regular-rounded.css'>

      <div class="plus-select-date-wrapper">
        <label class="plus-select-date-label">${labelText}</label>
        <div class="plus-select-date-display">
          <i class="fi icon-calendar fi-rr-calendar"></i>
          <span class="plus-select-date-range">${select_range_date}</span>
          <i class="fi fi-rr-angle-small-right" style="margin-left:auto;"></i>
        </div>
        <div class="plus-select-date-popup">
          <div class="plus-select-date-options">
            <div data-range="today">${today}</div>
            <div data-range="7days">${last_7_days}</div>
            <div data-range="thismonth">${current_month}</div>
            <div data-range="lastmonth">${previous_month}</div>
            <div data-range="custom">${custom}</div>
          </div>

          <div class="plus-select-date-custom">
            <input type="date" class="date-start">
            <input type="date" class="date-end">
            <div class="plus-select-date-buttons">
              <button class="btn-accept" type="button">${success}</button>
              <button class="btn-cancel" type="button">${cancel}</button>
            </div>
          </div>
        </div>

        <input type="hidden" id="${nameStart}" name="${nameStart}">
        <input type="hidden" id="${nameEnd}" name="${nameEnd}">
      </div>
    `;

    const display = shadow.querySelector('.plus-select-date-display');
    const popup = shadow.querySelector('.plus-select-date-popup');
    const options = shadow.querySelectorAll('.plus-select-date-options > div');
    const customDiv = shadow.querySelector('.plus-select-date-custom');
    const dateStart = shadow.querySelector('.date-start');
    const dateEnd = shadow.querySelector('.date-end');
    const btnAccept = shadow.querySelector('.btn-accept');
    const btnCancel = shadow.querySelector('.btn-cancel');
    const rangeSpan = shadow.querySelector('.plus-select-date-range');
    const inputStart = shadow.getElementById(nameStart);
    const inputEnd = shadow.getElementById(nameEnd);

    function formatDate(date) {
      return date.toLocaleDateString(lang, { day: 'numeric', month: 'long', year: 'numeric' });
    }

    function setRange(start, end) {
      rangeSpan.textContent = `${formatDate(start)} - ${formatDate(end)}`;
      inputStart.value = start.toISOString().split('T')[0];
      inputEnd.value = end.toISOString().split('T')[0];
    }

    display.addEventListener('click', () => {
      popup.classList.toggle('active');
    });

    options.forEach(option => {
      option.addEventListener('click', () => {
        const type = option.dataset.range;
        const now = new Date();
        let start, end;

        customDiv.classList.remove('active');

        if (type === 'today') {
          start = end = now;
        } else if (type === '7days') {
          end = now;
          start = new Date();
          start.setDate(end.getDate() - 6);
        } else if (type === 'thismonth') {
          start = new Date(now.getFullYear(), now.getMonth(), 1);
          end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        } else if (type === 'lastmonth') {
          start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
          end = new Date(now.getFullYear(), now.getMonth(), 0);
        } else if (type === 'custom') {
          customDiv.classList.add('active');
          return;
        }

        setRange(start, end);
        popup.classList.remove('active');
      });
    });

    btnAccept.addEventListener('click', () => {
      if (dateStart.value && dateEnd.value) {
        const start = new Date(dateStart.value);
        const end = new Date(dateEnd.value);
        setRange(start, end);
        popup.classList.remove('active');
      }
    });

    btnCancel.addEventListener('click', () => {
      popup.classList.remove('active');
    });

    document.addEventListener('click', (e) => {
      if (!this.contains(e.target) && !shadow.contains(e.target)) {
        popup.classList.remove('active');
      }
    });
  }
}

class PlusTabs extends HTMLElement {
  connectedCallback() {
    if (this._rendered) return;
    this._rendered = true;

    this.classList.add('plus-tabs');

    const tabButtonsContainer = document.createElement('div');
    tabButtonsContainer.className = 'plus-tab-buttons';

    const tabs = Array.from(this.querySelectorAll('plus-tab'));

    tabs.forEach((tab, index) => {
      const tAttr = tab.getAttribute('t') || tab.getAttribute('text') || 'tab';
      const title = window.translate_text(tAttr);

      const button = document.createElement('button');
      button.textContent = title;
      button.type = 'button';
      button.setAttribute('t', tAttr);
      if (index === 0) button.classList.add('active');

      button.addEventListener('click', () => {
        this.querySelectorAll('plus-tab').forEach((t, i) => {
          t.style.display = i === index ? 'block' : 'none';
        });
        tabButtonsContainer.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
      });

      tabButtonsContainer.appendChild(button);
    });

    this.insertBefore(tabButtonsContainer, this.firstChild);

    // Mostrar solo el primer tab al iniciar
    tabs.forEach((tab, index) => {
      tab.style.display = index === 0 ? 'block' : 'none';
    });
  }
}

class PlusTab extends HTMLElement {
  connectedCallback() {
    this.classList.add('plus-tab');
    //this.style.display = 'none';
  }
}


/*
This is a menu of 3 points. When the user do click 
the label show all the options that added the programmer use <plus-action> 
*/
class PlusActions extends HTMLElement {
  constructor() {
    super();
    this.open = false;
  }

  connectedCallback() {
    if (this._rendered) return;
    this._rendered = true;
    this.classList.add('plus-actions');

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'plus-action-button';
    button.innerHTML = '<i class="fi fi-rr-menu-dots-vertical"></i>';

    const menu = document.createElement('div');
    menu.className = 'plus-action-menu';
    menu.style.display = 'none';

    const actions = this.querySelectorAll('plus-action');
    actions.forEach(action => {
      const type = action.getAttribute('type') || null;
      const icon = action.getAttribute('icon') || '';
      const t = action.getAttribute('t') || action.getAttribute('text');
      const text = action.getAttribute('text');
      const onclick = action.getAttribute('onclick');

      //now we will see if the user add a 
      const existCombo = action.hasAttribute('combo')
      const combo = action.getAttribute('combo')
      if (existCombo) {
        const keyBind = document.createElement('key-bind');
        keyBind.setAttribute('combo', combo)
        keyBind.setAttribute('action', onclick)
        this.appendChild(keyBind);
      }

      //save the text to translate
      const textTranslate = window.translate_text(t) + (existCombo ? ' ' + combo : '');

      //her we will see the type 
      let item;
      if (type == 'switch') {
        //her we will to create a id for that the user can edit or get iformation of the switch 
        const id = action.getAttribute('id') || `plus-id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
        const raw = action.getAttribute('checked');
        const checked = get_value_of_label_true_or_false(raw);

        //her we will save all the information that the proggramer added to the label
        item = document.createElement('plus-switch');
        item.setAttribute('id', id)
        item.setAttribute('text', text)
        item.setAttribute('t', t)
        item.setAttribute('name', id)
        item.setAttribute('icon', icon)

        if (checked) {
          item.setAttribute('checked', checked);
        }
      } else {
        item = document.createElement('div');
        item.className = 'plus-action-item';

        //we will see if this button need a pin 
        const thisElementHaveApin = action.hasAttribute('pin');
        const pin = get_value_of_label_true_or_false(action.getAttribute('pin'));

        if (thisElementHaveApin) {
          if (pin) {
            item.innerHTML = `
              <div class="item-row">
                <div class="item-main" onclick="handleMainAction(this)">
                  <i class="${icon}"></i>
                  <span t='${t}'>${textTranslate}</span>
                </div>
                <div class="item-pin">
                  <i class="fi fi-ss-thumbtack"></i>
                </div>
              </div>
            `;
          } else {
            item.innerHTML = `
              <div class="item-row">
                <div class="item-main" onclick="handleMainAction(this)">
                  <i class="${icon}"></i>
                  <span t='${t}'>${textTranslate}</span>
                </div>
                <div class="item-pin">
                  <i class="fi fi-rs-thumbtack"></i>
                </div>
              </div>
            `;
          }
        } else {
          item.innerHTML = `
          <div class="item-row">
            <div class="item-main" onclick="handleMainAction(this)">
              <i class="${icon}"></i>
              <span t='${t}'>${textTranslate}</span>
            </div>
          </div>
          `;
        }
      }




      if (onclick) {
        item.onclick = () => {

          window[onclick]?.();
          this.toggle(false); // opcional: close when do clic the user
        };
      }

      // Assign event to pins without propagating the click to the parent
      const pinIcon = item.querySelector('.item-pin i');
      if (pinIcon) {
        pinIcon.addEventListener('click', (e) => {
          e.stopPropagation(); // This prevents the parent click from being triggered.
          this.handlePin(pinIcon, action, onclick, icon, textTranslate);  // run the function for add the function flash
        });
      }

      menu.appendChild(item);

    });

    //her is the desktop of the shortcuts of the functions
    const quickActions = document.createElement('div');
    quickActions.className = 'plus-quick-actions';
    this.appendChild(quickActions);

    this.appendChild(button);
    this.appendChild(menu);

    button.addEventListener('click', () => this.toggle());
  }

  toggle(forceState = null) {
    const menu = this.querySelector('.plus-action-menu');
    const icon = this.querySelector('.plus-action-button i');

    this.open = forceState !== null ? forceState : !this.open;

    if (this.open) {
      menu.style.display = 'block';

      // Esperar a que el menú tenga tamaño real
      requestAnimationFrame(() => {
        const triggerRect = this.getBoundingClientRect();
        const menuRect = menu.getBoundingClientRect();
        const viewportWidth = window.innerWidth;

        const GAP = 8; //space of segurity

        const spaceRight = viewportWidth - triggerRect.right;
        const spaceLeft = triggerRect.left;

        // Reset previo
        menu.style.left = 'auto';
        menu.style.right = 'auto';

        if (spaceRight >= menuRect.width + GAP) {
          // open to the rigth
          menu.style.left = '100%';
        } else if (spaceLeft >= menuRect.width + GAP) {
          // open to the left
          menu.style.right = '100%';
        } else {
          // 👉 Fallback change with help of the viewport
          menu.style.left = '50%';
          menu.style.transform = 'translateX(-60%)';
        }
      });

      icon.style.transform = 'rotate(90deg)';
    } else {
      menu.style.display = 'none';

      // clear the fallback
      menu.style.transform = '';

      icon.style.transform = 'rotate(0deg)';
    }
  }

  handlePin(pinIcon, action, onclick, icon, textTranslate) {
    const quickActions = this.querySelector('.plus-quick-actions');
    const alreadyPinned = pinIcon.classList.contains('fi-ss-thumbtack');

    if (alreadyPinned) {
      // Remove quick access
      pinIcon.classList.remove('fi-ss-thumbtack');
      pinIcon.classList.add('fi-rs-thumbtack');

      const existing = quickActions.querySelector(`[data-id="${textTranslate}"]`);
      if (existing) quickActions.removeChild(existing);
    } else {
      // Add quick access
      pinIcon.classList.remove('fi-rs-thumbtack');
      pinIcon.classList.add('fi-ss-thumbtack');

      const shortcut = document.createElement('button');
      shortcut.type = 'button';
      shortcut.className = 'plus-quick-action';
      shortcut.setAttribute('data-id', textTranslate);

      if (icon) {
        shortcut.innerHTML = `<i class="${icon}"></i>`;
      } else {
        shortcut.textContent = textTranslate;
      }

      shortcut.addEventListener('click', () => {
        if (onclick) window[onclick]?.();
      });

      quickActions.appendChild(shortcut);
    }
  }
}

class PlusComment extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  async connectedCallback() {
    const shadow = this.shadowRoot;

    // Carga Quill JS y CSS desde un CDN (puedes cambiarlo si es local)
    const quillJS = await this.loadScript('https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js');
    const quillCSS = await this.loadCSS('https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css');

    // Agrega estilos al shadow
    const styleTag = document.createElement('style');
    styleTag.textContent = `
      #editor {
        height: 200px;
      }
      .ql-toolbar.ql-snow {
        border: 1px solid #ccc;
        border-bottom: none;
      }
      .ql-container.ql-snow {
        border: 1px solid #ccc;
      }
    `;
    shadow.appendChild(styleTag);

    // Crea el contenedor del editor
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css">
      <div class="editor">
        <div id="toolbar">
          <button class="ql-bold" type="button"></button>
          <button class="ql-italic" type="button"></button>
          <button class="ql-underline" type="button"></button>
          <button class="ql-strike" type="button"></button>
          <select class="ql-size">
            <option value="small"></option>
            <option selected></option>
            <option value="large"></option>
            <option value="huge"></option>
          </select>
          <button class="ql-list" value="ordered" type="button"></button>
          <button class="ql-list" value="bullet" type="button"></button>
        </div>
        <div id="editor"></div>
      </div>
    `;
    shadow.appendChild(wrapper);

    // Inyecta Quill dentro del shadow DOM usando su propio contexto
    const Quill = window.Quill;
    new Quill(shadow.getElementById('editor'), {
      theme: 'snow',
      modules: {
        toolbar: shadow.getElementById('toolbar')
      }
    });
  }

  // Método para cargar el CSS y devolver la URL para uso interno
  loadCSS(href) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.onload = () => resolve(href);
      link.onerror = () => reject(new Error(`Error cargando CSS: ${href}`));
      this.shadowRoot.appendChild(link);
    });
  }

  // Método para cargar el JS de Quill
  loadScript(src) {
    return new Promise((resolve, reject) => {
      if (window.Quill) return resolve();

      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = () => reject(new Error(`Error cargando JS: ${src}`));
      document.head.appendChild(script);
    });
  }
}

class PlusFilterTable extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.table = null;
    this.open = false;
  }

  connectedCallback() {
    const tableId = this.getAttribute('table-id');
    this.table = document.getElementById(tableId);
    if (!this.table) {
      console.warn(`Table with id "${tableId}" not found.`);
      return;
    }

    const columnElements = this.querySelectorAll('plus-column');
    const columns = Array.from(columnElements).map(col => ({
      index: parseInt(col.getAttribute('index')),
      label: col.getAttribute('t') || col.getAttribute('label'),
      checked: col.hasAttribute('checked')
    }));

    // Botón de filtro
    const button = document.createElement('button');
    button.classList.add('filter-button');
    button.innerHTML = '⋮';
    button.addEventListener('click', () => this.toggleMenu());

    // Contenedor flotante de filtros
    const container = document.createElement('div');
    container.classList.add('table-controls');
    container.style.display = 'none';

    // Input buscador
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = window.t('message.search');
    searchInput.classList.add('filter-search');
    searchInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase();
      container.querySelectorAll('.switch-label').forEach(label => {
        const text = label.textContent.toLowerCase();
        label.style.display = text.includes(term) ? 'flex' : 'none';
      });
    });
    container.appendChild(searchInput);

    columns.forEach(col => {
      const t = col.label;
      const label = document.createElement('label');
      label.setAttribute('t', t);
      label.classList.add('switch-label');

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = col.checked;
      checkbox.dataset.col = col.index;

      const slider = document.createElement('span');
      slider.classList.add('slider');

      label.appendChild(checkbox);
      label.appendChild(slider);

      const text = document.createTextNode(col.label);
      label.appendChild(document.createTextNode(col.label));

      checkbox.addEventListener('change', (e) => {
        const colIndex = parseInt(e.target.dataset.col);
        const checked = e.target.checked;
        Array.from(this.table.rows).forEach(row => {
          if (row.cells[colIndex]) row.cells[colIndex].style.display = checked ? '' : 'none';
        });
      });

      container.appendChild(label);
    });

    this.shadowRoot.appendChild(button);
    this.shadowRoot.appendChild(container);

    const style = document.createElement('style');
    style.textContent = `
      .filter-button {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 20px;
        padding: 4px 8px;
        position: relative;
        z-index: 1001;
      }

      .table-controls {
        position: absolute;
        top: 30px;
        right: 0;
        display: flex;
        flex-direction: column;
        gap: 8px;
        max-height: 250px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: white;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        min-width: 140px;
      }

      .filter-search {
        padding: 4px 2px;
        border: none;
        border-bottom: 1px solid #ccc;
        outline: none;
        font-size: 14px;
        margin-bottom: 6px;
        transition: border-color 0.3s;
      }

      .filter-search:focus {
        border-color: ${colors.color_company};
      }

      .switch-label {
        position: relative;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        cursor: pointer;
        user-select: none;
      }

      .switch-label input {
        opacity: 0;
        width: 0;
        height: 0;
      }

      .slider {
        position: relative;
        width: 36px;
        height: 20px;
        background-color: #ccc;
        border-radius: 20px;
        transition: 0.3s;
        flex-shrink: 0;
      }

      .slider:before {
        content: "";
        position: absolute;
        width: 16px;
        height: 16px;
        left: 2px;
        bottom: 2px;
        background-color: white;
        border-radius: 50%;
        transition: 0.3s;
      }

      input:checked + .slider {
        background-color: ${colors.color_company};
      }

      input:checked + .slider:before {
        transform: translateX(16px);
      }

      .table-controls {
        display: flex;
        flex-direction: column;
        gap: 4px;
        max-height: 250px;
        overflow-y: auto;
        background: white;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        width: max-content;     
        min-width: 150px;       
      }

      /* Scrollbar minimalista */
      .table-controls::-webkit-scrollbar {
        width: 3px;
      }

      .table-controls::-webkit-scrollbar-track {
        background: transparent;
      }

      .table-controls::-webkit-scrollbar-thumb {
        background-color: rgba(0,0,0,0.25);
        border-radius: 3px;
        transition: background 0.3s;
      }

      .table-controls::-webkit-scrollbar-thumb:hover {
        background-color: rgba(0,0,0,0.4);
      }

      @media (max-width: 768px) {
        .table-controls {
          right: 10px;
          top: 40px;
          max-height: 200px;
          min-width: 120px;
          width: 90vw;
          padding: 8px;
          gap: 3px;
        }

        .switch-label {
          font-size: 13px;
        }

        .filter-button {
          font-size: 18px;
          padding: 2px 6px;
        }

        .filter-search {
          font-size: 13px;
        }
      }
    `;
    this.shadowRoot.appendChild(style);
  }

  toggleMenu() {
    const container = this.shadowRoot.querySelector('.table-controls');
    const buttonRect = this.shadowRoot.querySelector('.filter-button').getBoundingClientRect();
    this.open = !this.open;
    container.style.display = this.open ? 'flex' : 'none';
    container.style.position = 'fixed';
    container.style.top = `${buttonRect.bottom + 4}px`;
    container.style.left = `${buttonRect.left}px`;
  }
}

class PlusSearch extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    // Crear contenedor principal
    const container = document.createElement("div");
    container.classList.add("plus-search-container");

    // Contenedor input con icono
    const inputWrapper = document.createElement("div");
    inputWrapper.classList.add("plus-search-input");

    // Icono lupa
    const icon = document.createElement("i");
    icon.className = "fi fi-rs-search";

    // Input
    const idInput = this.getAttribute('input_id') || generate_unique_dom_id();
    const input = document.createElement("input");
    input.type = "search";
    input.placeholder = this.getAttribute("placeholder") || "message.search";
    input.setAttribute('t-placeholder', input.placeholder);
    input.setAttribute('id', idInput);

    inputWrapper.appendChild(icon);
    inputWrapper.appendChild(input);

    // Contenedor de opciones
    const optionsContainer = document.createElement("div");
    optionsContainer.classList.add("plus-search-options");

    // Mover los hijos <search-option>
    const options = this.querySelectorAll("search-option");
    options.forEach(opt => {
      optionsContainer.appendChild(opt.firstElementChild);
    });

    // Limpiar y renderizar
    this.innerHTML = "";
    container.appendChild(inputWrapper);
    container.appendChild(optionsContainer);
    this.appendChild(container);
  }
}

/*----------------DATE------------------------------------- */
function format_date_to_text(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // the month goes from 0 to 11
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

class PlusDate extends HTMLElement {
  constructor() {
    super();
    this.selectedDate = null;
    this.currentDate = new Date();

    //her we will to create a  input hidden outside of the DOM normal 
    const name = this.getAttribute('name') || 'plus-date';
    this.hiddenInput = document.createElement('input');
    this.hiddenInput.type = 'hidden';
    this.hiddenInput.name = name;
    this.appendChild(this.hiddenInput);

    this.mode = 'days'; // 'days' | 'months'

    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    const t = this.getAttribute("t") || this.getAttribute("label") || 'btn.select_range_date'; //her we will see if the user would like translate a text, if no have nathing, we will get the value of the label
    const labelText = window.translate_text(t); //her we will to trsnlate the text if exist a text, else we will to create a value predefine 

    const name = this.getAttribute("name") || "plus-date";
    const valueAttr = this.getAttribute("value");
    if (valueAttr) {
      this.selectedDate = new Date(valueAttr);
      this.currentDate = new Date(valueAttr);
    }

    //update the input that be hidden
    if (this.selectedDate) {
      const formattedValue = this.selectedDate.toISOString().split('T')[0];
      this.hiddenInput.value = formattedValue;
    }


    const style = document.createElement("style");
    style.textContent = `
      .plus-calendar-calendar {
        background-color: white;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-radius: 20px;
        padding: 20px;
        width: 100%;
        z-inex:-50;
      }

      .plus-calendar-calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
      }

      .plus-calendar-calendar-header h2 {
        margin: 0;
        font-size: 1.4rem;
      }

      .plus-calendar-calendar-days {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        text-align: center;
      }

      .plus-calendar-calendar-days .plus-calendar-day {
        padding: 8px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
      }

      .plus-calendar-calendar-days .plus-calendar-day:hover {
        background-color: #eee;
      }

      .plus-calendar-calendar-days .plus-calendar-today {
        background-color: #f4f4f8ff;
        color: black;
      }

      .plus-calendar-calendar-days .plus-calendar-selected {
        background-color: ${colors.color_company};
        color: white;
      }

      .plus-calendar-calendar-days .plus-calendar-empty {
        visibility: hidden;
      }

      .plus-calendar-fake-input {
        width: 100%;
        padding: 8px 4px;
        margin-top: 4px;
        border: none;
        border-bottom: 2px solid #d0d5dd;
        background-color: transparent;
        font-size: 1em;
        color: #1d2939;
        outline: none;
        transition: border-color 0.3s;
        margin: 12px 0;
      }

      .plus-calendar-fake-input:hover,
      .plus-calendar-fake-input:focus {
        border-bottom-color: #2a395b;
      }

      .plus-calendar-calendar-container {
        margin-top: 10px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 999;
        position: absolute;
      }

      .plus-calendar-calendar-header button {
        background-color: transparent;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 5px 10px;
        border-radius: 8px;
        transition: background 0.2s;
      }

      .plus-calendar-calendar-header button:hover {
        background-color: #f0f0f0;
      }

      .plus-calendar-input-label {
        font-size: 0.85em;
        color: #475467;
        margin-bottom: 4px;
        display: block;
      }

      .plus-calendar-input-wrapper {
        position: relative;
        width: max-content;
      }





    .plus-calendar-calendar-days-month{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      text-align: center;
      padding: 10px 0;
    }


    .plus-calendar-month {
      padding: 10px 6px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.95rem;
      color: #333;
      user-select: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      cursor: pointer;
      transition: background-color 0.25s ease;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 40px; /* altura fija para uniformidad */
    }

    .plus-calendar-month:hover {
      background-color: #f4f4f8ff;
      color: #2a395b;
    }

      .btn-restart{
        background-color: #f4f4f8ff;
        color: #2a395b;
        border: none;
        font-size: .9rem;
        cursor: pointer;
        padding: 5px 5px;
        border-radius: 8px;
      }

      .btn-restart:hover{
      cursor:pointer;
      }
    `;


    this.shadowRoot.innerHTML = `
      <div class="plus-calendar-input-wrapper">
        <div class="plus-calendar-fake-input" id="plus-date-display">${this.formatDate(this.selectedDate)}</div>
        <input type="date" id="${name}" name="${name}" style="display:none;" value="${valueAttr || ''}"/>
        <div class="plus-calendar-calendar-container" style="display:none;"></div>
      </div>
    `;


    this.shadowRoot.appendChild(style);

    this.display = this.shadowRoot.querySelector('#plus-date-display');
    this.input = this.shadowRoot.querySelector(`input[name="${name}"]`);
    this.input.type = 'date';
    this.input.id = this.getAttribute("id") || generate_unique_dom_id(); //her we will to create a id 
    this.input.required = this.hasAttribute('required'); //we will see if this input is requerid

    this.calendarContainer = this.shadowRoot.querySelector('.plus-calendar-calendar-container');

    this.display.addEventListener('click', () => {
      this.toggleCalendar();
    });

    //Close calendar if clicked outside
    document.addEventListener('click', (e) => {
      if (!this.contains(e.target)) {
        this.calendarContainer.style.display = 'none';
      }
    });

    this.renderCalendar();
  }

  toggleCalendar() {
    this.calendarContainer.style.display =
      this.calendarContainer.style.display === 'none' ? 'block' : 'none';
    this.renderCalendar();
  }

  formatDate(date) {
    if (!date) return '00/00/0000';
    const lang = window.get_language_of_the_system()
    return date.toLocaleDateString(lang, {
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  }

  renderCalendar() {
    if (this.mode === 'days') {
      this.renderDays();
    } else if (this.mode === 'months') {
      this.renderMonths();
    }

    this.update_input_form();
  }

  create_text_day() {
    return `<div>${window.t('date.sunday')}</div><div>${window.t('date.monday')}</div><div>${window.t('date.tuesday')}</div><div>${window.t('date.wednesday')}</div><div>${window.t('date.thursday')}</div><div>${window.t('date.friday')}</div><div>${window.t('date.saturday')}</div>`;
  }

  renderDays() {
    const month = this.currentDate.getMonth();
    const year = this.currentDate.getFullYear();
    const firstDay = new Date(year, month, 1).getDay();
    const lastDate = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    const selected = this.selectedDate;


    const textToday = window.t('range.today');
    const textDay = this.create_text_day();
    const userLang = window.get_language_of_the_system(); //get the languace of the system of the user

    let html = `
      <div class="plus-calendar-calendar">
        <div class="plus-calendar-calendar-header">
          <button class="plus-calendar-prev-month" type="button">❮</button>
          <span class="plus-calendar-current-month">${this.currentDate.toLocaleDateString(userLang, { month: 'long', year: 'numeric' })}</span>
          <button class="plus-calendar-next-month" type="button">❯</button>
          <button class="plus-calendar-today-btn" type="button">${textToday}</button>
        </div>
        <div class="plus-calendar-calendar-days">
        ${textDay}
    `;

    for (let i = 0; i < firstDay; i++) {
      html += `<div class="plus-calendar-empty"></div>`;
    }

    for (let d = 1; d <= lastDate; d++) {
      const current = new Date(year, month, d);
      const isToday = current.toDateString() === today.toDateString();
      const isSelected = selected && current.toDateString() === selected.toDateString();
      html += `<div class="plus-calendar-day 
        ${isToday ? "plus-calendar-today" : ""} 
        ${isSelected ? "plus-calendar-selected" : ""}" 
        data-date="${current.toISOString()}">${d}</div>`;
    }



    html += `</div>
      <button class="btn-restart" type="button">${window.t('btn.restart')}</button>
    </div>`;
    this.calendarContainer.innerHTML = html;

    // Events of the buttons for change the date
    this.calendarContainer.querySelector('.plus-calendar-prev-month').onclick = () => {
      this.currentDate.setMonth(this.currentDate.getMonth() - 1);
      this.renderCalendar();
    };
    this.calendarContainer.querySelector('.plus-calendar-next-month').onclick = () => {
      this.currentDate.setMonth(this.currentDate.getMonth() + 1);
      this.renderCalendar();
    };
    this.calendarContainer.querySelector('.plus-calendar-today-btn').onclick = () => {
      this.currentDate = new Date();
      this.selectedDate = new Date();
      this.input.value = this.selectedDate.toISOString().split('T')[0];
      this.display.textContent = this.formatDate(this.selectedDate);
      this.renderCalendar();
    };

    this.calendarContainer.querySelector('.plus-calendar-current-month').onclick = () => {
      this.mode = 'months';
      this.renderCalendar();
    };

    this.calendarContainer.querySelectorAll('.plus-calendar-day').forEach(day => {
      day.onclick = () => {
        const selectedISO = day.getAttribute('data-date');
        const newDate = new Date(selectedISO);
        this.selectedDate = newDate;
        this.input.value = selectedISO.split('T')[0];
        this.display.textContent = this.formatDate(newDate);
        this.calendarContainer.style.display = 'none';
        this.renderCalendar();
        this.update_input_form();
      };
    });




    this.calendarContainer.querySelector('.btn-restart').onclick = () => {
      this.selectedDate = null;
      this.input.value = '';
      this.display.textContent = '00/00/0000';//window.t('btn.select_range_date');
      this.calendarContainer.style.display = 'none';
      this.renderCalendar();
      this.update_input_form();
    };


    this.update_input_form();
  }

  get_list_months() {
    return [
      window.t('date.month.january'),
      window.t('date.month.february'),
      window.t('date.month.march'),
      window.t('date.month.april'),
      window.t('date.month.may'),
      window.t('date.month.june'),
      window.t('date.month.july'),
      window.t('date.month.august'),
      window.t('date.month.september'),
      window.t('date.month.october'),
      window.t('date.month.november'),
      window.t('date.month.december')
    ];
  }

  renderMonths() {
    const year = this.currentDate.getFullYear();
    const monthNames = this.get_list_months();
    const textToday = window.t('range.today');

    let html = `
      <div class="plus-calendar-calendar">
        <div class="plus-calendar-calendar-header">
          <button class="plus-calendar-prev-month" type="button">❮</button>
          <span class="plus-calendar-current-month">${year}</span>
          <button class="plus-calendar-next-month" type="button">❯</button>
          <button class="plus-calendar-today-btn" type="button">${textToday}</button>
          <button class="plus-calendar-today-btn" type="button">${textToday}</button>
        </div>
        <div class="plus-calendar-calendar-days-month">
    `;

    for (let m = 0; m < 12; m++) {
      html += `<div class="plus-calendar-month" data-month="${m}" style="cursor: pointer;">${monthNames[m]}</div>`;
    }

    html += `</div></div>`;
    this.calendarContainer.innerHTML = html;

    //Events to browse between years
    this.calendarContainer.querySelector('.plus-calendar-prev-month').onclick = () => {
      this.currentDate.setFullYear(this.currentDate.getFullYear() - 1);
      this.renderCalendar();
    };
    this.calendarContainer.querySelector('.plus-calendar-next-month').onclick = () => {
      this.currentDate.setFullYear(this.currentDate.getFullYear() + 1);
      this.renderCalendar();
    };
    this.calendarContainer.querySelector('.plus-calendar-today-btn').onclick = () => {
      this.currentDate = new Date();
      this.selectedDate = new Date();
      this.input.value = this.selectedDate.toISOString().split('T')[0];
      this.display.textContent = this.formatDate(this.selectedDate);
      this.mode = 'days';
      this.renderCalendar();
    };

    // Select month and return to day mode
    this.calendarContainer.querySelectorAll('.plus-calendar-month').forEach(monthDiv => {
      monthDiv.onclick = () => {
        const month = parseInt(monthDiv.getAttribute('data-month'));
        this.currentDate.setMonth(month);
        this.mode = 'days';
        this.renderCalendar();
      };
    });


    this.update_input_form();
  }

  update_input_form() {
    if (this.selectedDate) {
        //We extract the parts of the LOCAL date
        const year = this.selectedDate.getFullYear();
        const month = String(this.selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(this.selectedDate.getDate()).padStart(2, '0');
        
        //YYYY-MM-DD format based on user view, not UTC
        this.hiddenInput.value = `${year}-${month}-${day}`;
    }
  }
}

function change_plus_date(id, newDate) {
  const plusDate = document.getElementById(id);
  if (!plusDate) return;

  const shadow = plusDate.shadowRoot;
  if (!shadow) return;

  const displayDiv = shadow.querySelector('#plus-date-display');

  // 1️⃣ Actualizar la UI del calendario
  if (displayDiv) {
    displayDiv.textContent = format_date_to_text(newDate); // mostrar fecha
  }

  // 2️⃣ Actualizar el input dentro del shadow DOM (opcional)
  const inputShadow = shadow.querySelector('input[type="date"]');
  if (inputShadow) inputShadow.value = typeof newDate === 'string' ? newDate : newDate.toISOString().split('T')[0];

  // 3️⃣ Actualizar el input hidden que se envía al formulario
  if (plusDate.hiddenInput) {
    plusDate.hiddenInput.value = typeof newDate === 'string' ? newDate : newDate.toISOString().split('T')[0];
  }

  // 4️⃣ Actualizar la propiedad selectedDate del componente
  if (plusDate.selectedDate !== undefined) {
    plusDate.selectedDate = typeof newDate === 'string' ? new Date(newDate) : newDate;
  }

  // 5️⃣ (Opcional) refrescar calendario interno
  if (plusDate.renderCalendar) {
    plusDate.renderCalendar();
  }
}

class PlusTime extends HTMLElement {
  constructor() {
    super();
    this.selectedHour = 12;
    this.selectedMinute = 0;
    this.attachShadow({ mode: "open" });

    //her we will to create a  input hidden outside of the DOM normal 
    const name = this.getAttribute('name') || 'plus-time';
    this.hiddenInput = document.createElement('input');
    this.hiddenInput.type = 'hidden';
    this.hiddenInput.name = name;
    this.appendChild(this.hiddenInput);
  }

  connectedCallback() {
    const name = this.getAttribute("name") || "plus-time";
    const id = this.getAttribute("id") || generate_unique_dom_id(); //her we will to create a id 
    const t = this.getAttribute("t") || this.getAttribute("label") || "Select Time";
    const labelTranslate = window.translate_text(t);
    const valueAttr = this.getAttribute("value") || "";
    const [h, m] = valueAttr.split(":");
    if (h && m) {
      this.selectedHour = parseInt(h);
      this.selectedMinute = parseInt(m);
    }

    const style = document.createElement("style");
    style.textContent = `
      .time-picker-wrapper {
        position: relative;
        width: max-content;
      }

      .time-picker-label {
        font-size: 0.85em;
        color: #475467;
        margin-bottom: 4px;
        display: block;
      }

      .time-picker-display {
        padding: 8px 4px;
        border: none;
        border-bottom: 2px solid #d0d5dd;
        background-color: transparent;
        font-size: 1em;
        color: #1d2939;
        outline: none;
        transition: border-color 0.3s;
        cursor: pointer;
        margin-top: 12px;
      }

      .time-picker-display:hover,
      .time-picker-display:focus {
        border-bottom-color: #2a395b;
      }

      .time-picker-dropdown {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 999;
        padding: 20px;
        display: flex;
        gap: 16px;
        user-select: none;
      }

      .time-scroll {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 1.5rem;
        height: 120px;
        overflow: hidden;
        position: relative;
      }

      .time-scroll div {
        padding: 6px;
        cursor: grab;
        transition: background-color 0.2s;
        text-align: center;
      }

      .time-scroll div:hover,
      .time-scroll div.selected {
        background-color: #f0f0f0;
        border-radius: 6px;
      }

      .arrow {
        font-size: 1.2rem;
        cursor: pointer;
        user-select: none;
      }
    `;

    this.shadowRoot.innerHTML = `
      <div class="time-picker-wrapper">
        <div class="time-picker-display">${this.formatTime()}</div>
        <input type="time" name="${name}" id="${id}" value="${this.formatTime(true)}" style="display:none;"/>
        <div class="time-picker-dropdown">
          <div class="time-scroll" id="hour-scroll">
            ${this.generateOptions(24, this.selectedHour)}
          </div>
          <div class="time-scroll" id="minute-scroll">
            ${this.generateOptions(60, this.selectedMinute)}
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.appendChild(style);

    this.display = this.shadowRoot.querySelector(".time-picker-display");
    this.dropdown = this.shadowRoot.querySelector(".time-picker-dropdown");
    this.input = this.shadowRoot.querySelector("input[type='time']");

    this.display.addEventListener("click", () => {
      const isOpening = 
        this.dropdown.style.display === "none" || !this.dropdown.style.display;
      
      this.dropdown.style.display = isOpening ? "flex" : "none";
      
      if (isOpening) {
        // call to the option for center the hours and the minutes when the user open the input
        this.centerSelectedOption();
      }
    });

    document.addEventListener("click", (e) => {
      if (!this.contains(e.target)) this.dropdown.style.display = "none";
      this.update_input_form();
    });

    this.initInteraction("hour");
    this.initInteraction("minute");
  }

  formatTime(asValue = false) {
    const h = String(this.selectedHour).padStart(2, "0");
    const m = String(this.selectedMinute).padStart(2, "0");
    return asValue ? `${h}:${m}` : `${h}:${m}`;
  }

  generateOptions(limit, selected) {
    let html = "";
    for (let i = 0; i < limit; i++) {
      const padded = String(i).padStart(2, "0");
      html += `<div class="time-option ${i === selected ? "selected" : ""}" data-val="${i}">${padded}</div>`;
    }
    return html;
  }

  initInteraction(type) {
      const scroll = this.shadowRoot.getElementById(`${type}-scroll`);
      const options = scroll.querySelectorAll(".time-option");

      let isDragging = false;
      let startY;
      let startScroll;
      
      // Almacenamos el elemento sobre el que se hizo el último 'touchstart'
      let touchTarget = null; 

      // --- Funciones de Arrastre (Desplazamiento) ---

      const startDrag = (e) => {
          isDragging = true;
          // e.touches[0].clientY para táctil, e.clientY para ratón
          startY = e.touches ? e.touches[0].clientY : e.clientY; 
          startScroll = scroll.scrollTop;
          
          // Almacena el elemento tocado para la selección posterior
          if (e.touches) touchTarget = e.target;
          
          if (e.type === 'touchstart') {
              e.preventDefault(); 
          }
          scroll.style.cursor = 'grabbing';
      };

      const drag = (e) => {
          if (!isDragging) return;
          const currentY = e.touches ? e.touches[0].clientY : e.clientY;
          const delta = startY - currentY;
          scroll.scrollTop = startScroll + delta;

          // Si hay un desplazamiento significativo, cancelamos el target
          if (Math.abs(delta) > 10) { 
              touchTarget = null;
          }

          if (e.type === 'touchmove') {
              e.preventDefault(); 
          }
      };

      const endDrag = () => {
          isDragging = false;
          scroll.style.cursor = 'grab';
      };
      
      // --- Lógica de Selección Unificada ---
      const handleSelection = (opt) => {
          // Lógica de selección:
          options.forEach((o) => o.classList.remove("selected"));
          opt.classList.add("selected");
          const val = parseInt(opt.getAttribute("data-val"));
          if (type === "hour") this.selectedHour = val;
          else this.selectedMinute = val;
          
          // Usar la función de actualización centralizada
          this.update_input_form(); 
      };

      // --- Listeners de Ratón (Desktop) ---
      scroll.addEventListener("mousedown", startDrag);
      document.addEventListener("mousemove", drag); 
      document.addEventListener("mouseup", endDrag);

      // --- Listeners Táctiles (Móvil) ---
      scroll.addEventListener("touchstart", startDrag, { passive: false });
      document.addEventListener("touchmove", drag, { passive: false });
      document.addEventListener("touchend", endDrag); // Finaliza el arrastre
      document.addEventListener("touchcancel", endDrag);

      // --- Listener de Rueda (Scroll) ---
      scroll.addEventListener("wheel", (e) => {
          e.preventDefault();
          scroll.scrollTop += e.deltaY;
      }, { passive: false });

      // --- Listener de Clic/Tap en Opciones (Selección) ---
      options.forEach((opt) => {
        
        // 1. Ratón: Sigue usando 'click'. Solo se dispara si NO hubo arrastre.
        opt.addEventListener("click", (e) => {
          // Evita el click si el elemento fue parte de un arrastre táctil reciente
          if (e.detail === 0 && e.pointerType === "touch") return; 
          handleSelection(opt);
        });
        
        // 2. Táctil: Usamos 'touchend'. Esto se dispara después de un toque (tap).
        opt.addEventListener("touchend", (e) => {
            e.preventDefault();
            //Only select the element if the touch start and finish in is moment (touchTarget)
            if (opt === touchTarget) { 
                handleSelection(opt);
            }
            touchTarget = null; // We reset the target after the selection/attempt
        });
      });
  }

  centerSelectedOption() {
    const hourScroll = this.shadowRoot.getElementById('hour-scroll');
    const minuteScroll = this.shadowRoot.getElementById('minute-scroll');

    // Internal function to center a specific scroll
    const performCentering = (scrollElement) => {
      const selectedOption = scrollElement.querySelector('.selected');
      if (selectedOption) {
        // calculate for center:
        // Top position of element + (Element height / 2) - (Scroll container height / 2)
        const centerPosition = 
          selectedOption.offsetTop + 
          (selectedOption.offsetHeight / 2) - 
          (scrollElement.clientHeight / 2);
        
        // aplicate scroll 
        scrollElement.scrollTop = centerPosition;
      }
    };

    if (hourScroll) performCentering(hourScroll);
    if (minuteScroll) performCentering(minuteScroll);
  }

  scrollCenter(scrollElement, options) {
      const selectedOption = scrollElement.querySelector('.selected');
      if (selectedOption) {
          // Height of an option element (approximately)
          const optionHeight = selectedOption.offsetHeight; 
          // Calculate the position to center: (element position) - (half the scroll height) + (half the element height)
          scrollElement.scrollTop = selectedOption.offsetTop - (scrollElement.clientHeight / 2) + (optionHeight / 2);
      }
  }

  update_input_form() {
    // update the input that is hidden
    if (this.hiddenInput) {
      this.hiddenInput.value = `${String(this.selectedHour).padStart(2, '0')}:${String(this.selectedMinute).padStart(2, '0')}`;
    }

    // also update the input type="time" in the shadow DOM
    if (this.input) {
      this.input.value = `${String(this.selectedHour).padStart(2, '0')}:${String(this.selectedMinute).padStart(2, '0')}`;
    }

    // Update the display
    if (this.display) {
      this.display.textContent = `${String(this.selectedHour).padStart(2, '0')}:${String(this.selectedMinute).padStart(2, '0')}`;
    }
  }

  disable() {
      if (this.display) {
        this.display.style.pointerEvents = "none";
        this.display.style.opacity = "0.5"; 
      }
      if (this.dropdown) {
        this.dropdown.style.display = "none";
      }

      this.selectedHour = 0;
      this.selectedMinute = 0;
      this.update_input_form();
  }

  enable(defaultTime = "07:00") {
    if (this.display) {
      this.display.style.pointerEvents = "auto";
      this.display.style.opacity = "1";
    }
    if (this.input) {
      this.input.disabled = false;
    }
    if (this.hiddenInput) {
      this.hiddenInput.disabled = false;
    }

    if (defaultTime) {
      change_plus_time(this.id, defaultTime);
    }
  }
}

function change_plus_time(id, newTime) {
  const plusTime = document.getElementById(id);
  if (!plusTime) return;

  const shadow = plusTime.shadowRoot;
  if (!shadow) return;

  const [hourStr, minuteStr] = newTime.split(':');
  const hour = parseInt(hourStr, 10);
  const minute = parseInt(minuteStr, 10);

  // Actualizar propiedades internas
  plusTime.selectedHour = hour;
  plusTime.selectedMinute = minute;

  // Actualizar display
  const displayDiv = shadow.querySelector('.time-picker-display');
  if (displayDiv) {
    displayDiv.textContent = `${hourStr.padStart(2, '0')}:${minuteStr.padStart(2, '0')}`;
  }

  // Actualizar input tipo time (si lo necesitas)
  const input = shadow.querySelector('input[type="time"]');
  if (input) {
    input.value = `${hourStr.padStart(2, '0')}:${minuteStr.padStart(2, '0')}`;
  }

  // Actualizar input hidden que se enviará en el formulario
  if (plusTime.hiddenInput) {
    plusTime.hiddenInput.value = `${hourStr.padStart(2, '0')}:${minuteStr.padStart(2, '0')}`;
  }
}

function update_input_date_and_time(id_date, id_time, data_date) {
  //first we will see if exist the data that we need convert
  if (data_date) {
    //convert the object to type Date only if the format initial not is YYYY-MM-DD
    let dateObj;
    if (data_date instanceof Date) {
      //when the data_date is Date, not convert
      dateObj = data_date;
    } else {
      //while that when data_date is string or other type, we will to convert this data in a type date
      dateObj = new Date(data_date);
    }


    // Get only the date in format YYYY-MM-DD
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    const date = new Date(year, dateObj.getMonth(), day);

    // Get only the time in format HH:MM:SS
    const hours = String(dateObj.getHours()).padStart(2, '0');
    const minutes = String(dateObj.getMinutes()).padStart(2, '0');
    const seconds = String(dateObj.getSeconds()).padStart(2, '0');
    const time = `${hours}:${minutes}:${seconds}`;

    window.change_plus_date(id_date, date);
    window.change_plus_time(id_time, time);
  }
}

function get_value_of_label_true_or_false(value) {
  return value === true || value === 'true' || value === '1' || value === 1;
}

class InputColor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });

    const colorInicial = this.getAttribute('value') || '#3b82f6';
    const name = this.getAttribute('name') || '';
    const id = this.getAttribute('id') || generate_unique_dom_id();

    this.value = colorInicial;

    // --- Crear hidden input FUERA del shadow DOM ---
    this.hiddenInput = document.createElement('input');
    this.hiddenInput.type = 'hidden';
    this.hiddenInput.name = name;
    this.hiddenInput.id = id;
    this.hiddenInput.value = colorInicial;
    this.appendChild(this.hiddenInput); // ✅ Light DOM, se envía con form

    // --- Contenedor visual dentro del shadow ---
    const container = document.createElement('div');
    container.innerHTML = `
      <style>
        .input-color-container {
          display: inline-block;
        }
        .color-box {
          width: 42px;
          height: 42px;
          border-radius: 12px;
          border: 1px solid #ccc;
          cursor: pointer;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          transition: all 0.2s ease;
        }
        .color-box:hover {
          box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
      </style>
      <div class="input-color-container">
        <div class="color-box" style="background-color: ${colorInicial}"></div>
      </div>
    `;

    // Label descriptivo
    const label = document.createElement('info-label');
    label.textContent = window.t('input.color');
    label.setAttribute('t', 'input.color');
    label.setAttribute('text', window.t('input.color'));
    this.shadowRoot.appendChild(label);

    this.shadowRoot.appendChild(container);

    // referencias
    this.box = this.shadowRoot.querySelector('.color-box');

    // evento abrir
    this.box.addEventListener('click', (e) => {
      e.stopPropagation();
      if (this.popupEl && document.body.contains(this.popupEl)) {
        this.closePopup();
      } else {
        this.openPopup();
      }
    });
  }

  updateColor(color) {
    this.value = color;
    this.box.style.backgroundColor = color;
    if (this.hiddenInput) this.hiddenInput.value = color; // actualizar Light DOM
    this.dispatchEvent(new CustomEvent('change', { detail: { color } }));
  }
  openPopup() {
    // cerrar si ya está abierto
    if (this.popupEl) {
      this.closePopup();
      return;
    }

    const rect = this.box.getBoundingClientRect();

    // Crear popup fuera del shadow DOM
    this.popupEl = document.createElement('div');
    this.popupEl.classList.add('color-picker-popup-global');
    this.popupEl.innerHTML = `
      <style>
        .color-picker-popup-global {
          position: absolute;
          top: ${rect.bottom + window.scrollY}px;
          left: ${rect.left + window.scrollX}px;
          background: #fff;
          border: 1px solid #e0e0e0;
          border-radius: 16px;
          box-shadow: 0 8px 16px rgba(0,0,0,0.1);
          padding: 16px;
          width: 260px;
          z-index: ${currentPopZIndex + 1};
        }
        .tabs {
          display: flex;
          margin-bottom: 12px;
          background: #f0f0f0;
          border-radius: 12px;
          overflow: hidden;
        }
        .tab-button {
          flex: 1;
          padding: 6px;
          background: transparent;
          border: none;
          cursor: pointer;
          font-size: 14px;
          color: #444;
        }
        .tab-button.active {
          background: #e0e0e0;
          font-weight: 600;
        }
        .tab-content {
          display: none;
        }
        .tab-content.active {
          display: block;
        }
        .quick-colors {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }
        .color-circle {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          cursor: pointer;
          border: 1px solid #ccc;
        }
        .color-circle:hover {
          border-color: #999;
        }
        .color-code-input {
          margin-top: 8px;
          width: 100%;
          padding: 6px 10px;
          border: 1px solid #ccc;
          border-radius: 8px;
          font-size: 13px;
          font-family: monospace;
          color: #333;
        }
        .accept-button {
          margin-top: 12px;
          width: 100%;
          padding: 8px;
          background: ${colors.color_company};
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          cursor: pointer;
        }
      </style>
      <div class="tabs">
        <button class="tab-button active" type="button">${window.t('input.speed')}</button>
        <button class="tab-button" type="button">${window.t('input.personalize')}</button>
      </div>
      <div class="tab-content active">
        <div class="quick-colors">
          ${[
        '#ff3b30', '#ff6b81', '#a55eea', '#8e44ad', '#0050ef',
        '#5ac8fa', '#007aff', '#00ffff', '#20c997', '#006400',
        '#34c759', '#ffff00', '#f1c40f', '#f39c12', '#ffa500',
        '#e67e22', '#8b4513', '#95a5a6', '#000000', '#ffffff'
      ].map(c => `<div class="color-circle" data-color="${c}" style="background:${c}"></div>`).join('')}
        </div>
      </div>
      <div class="tab-content">
        <input type="color" class="custom-color" value="${this.value}" />
        <input type="text" class="color-code-input" value="${this.value}" readonly />
        <button class="accept-button" type="button">${window.t('message.success')}</button>
      </div>
    `;
    document.body.appendChild(this.popupEl);

    // referencias internas
    const tabs = this.popupEl.querySelectorAll('.tab-button');
    const contents = this.popupEl.querySelectorAll('.tab-content');
    const colorInput = this.popupEl.querySelector('.custom-color');
    const acceptButton = this.popupEl.querySelector('.accept-button');

    // tabs
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        contents.forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        contents[i].classList.add('active');
      });
    });

    // quick colors
    this.popupEl.querySelectorAll('.color-circle').forEach(circle => {
      circle.addEventListener('click', () => {
        const color = circle.getAttribute('data-color');
        this.updateColor(color);
        this.closePopup();
      });
    });

    // aceptar color personalizado
    acceptButton.addEventListener('click', () => {
      const color = colorInput.value;
      this.updateColor(color);
      this.closePopup();
    });

    // cerrar al hacer click fuera
    setTimeout(() => {
      const handler = (e) => {
        if (this.popupEl && !this.popupEl.contains(e.target) && e.target !== this.box) {
          this.closePopup();
          document.removeEventListener('click', handler);
        }
      };
      document.addEventListener('click', handler);
    }, 0);
  }

  closePopup() {
    if (this.popupEl && document.body.contains(this.popupEl)) {
      this.popupEl.remove();
      this.popupEl = null;
    }
  }

  get value() {
    return this.getAttribute('value');
  }

  set value(val) {
    this.setAttribute('value', val);
  }

}

class PlusTag extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });

    // label
    const label = this.getAttribute('label') || 'input.tags';
    this.labelInfo = document.createElement('info-label');
    this.labelInfo.setAttribute('label', label);
    this.labelInfo.setAttribute('message', 'tag-message-show');
    this.appendChild(this.labelInfo);

    // atributes of the tag, we will see if need translate the tag
    const name = this.getAttribute('name') || 'plus-tags';
    const t = this.getAttribute('t') || this.getAttribute('t-placeholder') || this.getAttribute('placeholder') || 'input.tags';
    const textPlaceholder = window.translate_text(t);

    // Styles of the label tags
    const style = document.createElement('style');
    style.textContent = `
      .container {
        padding: 8px;
        flex-wrap: wrap;
        background: transparent;
        display: flex;
        gap: 8px;
        padding: 4px 0;
        border-bottom: 2px solid #D0D5DD;
      }

      .tag {
          background-color: #D6E9F8; 
          color: #085DA9;           
          padding: 6px 12px;
          border-radius: 999px;
          font-size: 14px;
          display: flex;
          align-items: center;
          transition: background-color 0.2s ease;
      }

      .tag:hover {
          background-color: #C5DFF1;
      }
          
      .tag button {
        background: none;
        border: none;
        color: inherit;
        font-weight: bold;
        cursor: pointer;
      }

      input[type="text"] {
        border: none;
        outline: none;
        flex: 1;
        min-width: 120px;
        font-size: 14px;
        background: transparent;
      }
    `;

    // estructura shadow
    this.shadowRoot.innerHTML = `
      <div class="container">
        <input type="text" t-placeholder="${t}">
      </div>
    `;
    this.shadowRoot.appendChild(style);

    // input hidden fuera del shadow
    this.hiddenInput = document.createElement('input');
    this.hiddenInput.type = 'hidden';
    this.hiddenInput.name = name;
    this.appendChild(this.hiddenInput);

    // list of all the tags
    this.emails = [];
  }

  connectedCallback() {
    this.input = this.shadowRoot.querySelector('input[type="text"]');
    this.container = this.shadowRoot.querySelector('.container');

    this.input.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        const email = this.input.value.trim();
        if (email && !this.emails.includes(email)) {
          this.addTag(email);
        }
        this.input.value = '';
      }
    });

    this._value = this.getAttribute('value') || []


    // Obtener los tags iniciales desde el atributo `value`
    const valueAttr = this.getAttribute('value');
    let initialTags = [];

    if (valueAttr) {
      try {
        //Trying to parse as JSON
        const parsed = JSON.parse(valueAttr);

        //Verify that it is an array of strings
        if (Array.isArray(parsed)) {
          initialTags = parsed;
        } else {
          console.warn('PlusTag: el atributo value debe ser un array JSON válido');
        }
      } catch (e) {
        console.warn('PlusTag: el atributo value debe ser un JSON válido', e);
      }
    }

    // Render the initial tags
    this.setTags(initialTags);
  }

  /** RENDER OF TAGS */
  /**
   * Renders the list of email tags inside the container.
   * 
   * This function first removes any existing tags to avoid duplicates.
   * Then, it iterates over the current list of emails and creates a 
   * visual "tag" element for each one. 
   * 
   * Each tag consists of:
   *  - The email text.
   *  - A small "×" button to remove the email from the list.
   * 
   * When the "×" button is clicked, the corresponding email is removed 
   * using the `removeTag()` method.
   * 
   * Finally, all tags are inserted into the container, before the 
   * input element, and the hidden input field is updated to contain 
   * the JSON string of the emails array. This makes the data 
   * available for form submissions.
   */
  renderTags() {
    // Remove any existing tags to re-render from scratch
    const existingTags = this.container.querySelectorAll('.tag');
    existingTags.forEach(tag => tag.remove());

    // Create a new tag element for each email
    this.emails.forEach(email => {
      const tag = document.createElement('span');
      tag.className = 'tag';
      tag.innerHTML = `${email} <button type="button">&times;</button>`;

      // Add event listener for removing this tag
      tag.querySelector('button').onclick = () => {
        this.removeTag(email);
      };

      // Insert the tag before the input field
      this.container.insertBefore(tag, this.input);
    });

    // Store all emails as JSON in the hidden input (for form submission)
    this.hiddenInput.value = JSON.stringify(this.emails);
  }

  /** PUBLIC METHODS */
  addTag(value) {
    if (value && !this.emails.includes(value)) {
      this.emails.push(value);
      this.renderTags();
    }
  }

  removeTag(value) {
    this.emails = this.emails.filter(v => v !== value);
    this.renderTags();
  }

  setTags(values) {
    if (Array.isArray(values)) {
      this.emails = values;
      this.renderTags();
    }
  }

  getTags() {
    return this.emails;
  }

  resetTags() {
    this.emails = [];
    this.renderTags();
  }
}

class ShowMore extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    const t = this.getAttribute("t") || this.getAttribute("label") || this.getAttribute("text") || "Show more";
    const textTranslate = window.translate_text(t)
    const onclickFn = this.getAttribute("onclick") || null;
    const wrapper = document.createElement("div");
    const description = this.getAttribute('description') || '';
    const translateDescription = window.translate_text(description);
    wrapper.classList.add("show-more-wrapper");


    wrapper.innerHTML = `
      <style>
        :host {
          display: block;
          margin: 8px 0;
        }
        .show-more-wrapper {
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
          font-weight: 500;
          font-size: 14px;
          color: #131313ff;
          background-color: #fff;
          padding: 16px 12px;
          border-radius: 8px;
          user-select: none;
        }
        .show-more-wrapper:hover {
          background-color: #ebebebff;
        }
        .label {
          flex: 1;
          text-align: left;
        }
        .right-container {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .description {
          font-weight: normal;
          font-size: 13px;
          color: #555;
        }
        .icon {
          font-weight: bold;
        }
      </style>
      <link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-regular-rounded/css/uicons-regular-rounded.css'>
      
      <span class="label" t='${t}'>${textTranslate}</span>
      <div class="right-container">
        ${description ? `<span class="description" t='${description}'>${translateDescription}</span>` : ''}
        <span class="icon"><i class="fi fi-rr-angle-right"></i></span>
      </div>
    `;

    this.shadowRoot.appendChild(wrapper);

    // evento click
    wrapper.addEventListener("click", () => {
      if (onclickFn && typeof window[onclickFn.replace("()", "")] === "function") {
        window[onclickFn.replace("()", "")]();
      }
    });
  }
}

class ImageUploader extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    const maxImages = parseInt(this.getAttribute("max")) || 1;
    const styleType = this.getAttribute("style") || "square";
    const fieldName = this.getAttribute("name") || "image";

    const style = document.createElement("style");
    style.textContent = `
      .uploader-container {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        padding: 20px;
        border-radius: 16px;
        justify-content: flex-start;
        align-items: center;
      }

      .image-box {
        position: relative;
        width: 120px;
        height: 120px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease-in-out;
      }

      .image-box:hover {
        border-color: ${colors.color_company};
        cursor:pointer;
      }

      .image-box img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .image-square img {
        border-radius: 0;
      }
      .image-rounded img {
        border-radius: 12px;
      }
      .image-circle img {
        border-radius: 50%;
      }

      .delete-btn {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: rgba(0,0,0,0.6);
        color: white;
        font-size: 16px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.2s ease-in-out, background 0.2s;
      }

      .image-box:hover .delete-btn {
        opacity: 1;
      }

      .delete-btn:hover {
        background: rgba(220,38,38,0.9); /* rojo elegante */
      }

      .add-button {
        width: 120px;
        height: 120px;
        border: 2px dashed #9ca3af;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        background: #f3f4f6;
        transition: all 0.3s ease-in-out;
      }

      .add-button:hover {
        background: #e5e7eb;
        border-color: ${colors.color_company};
      }

      .add-button:hover span {
        color: ${colors.color_company};
      }

      .add-button span {
        font-size: 2rem;
        color: #6b7280;
      }

      input[type="file"] {
        display: none;
      }
    `;


    const container = document.createElement("div");
    container.classList.add("uploader-container");

    const inputFile = document.createElement("input");
    inputFile.type = "file";
    inputFile.accept = "image/*";
    inputFile.multiple = maxImages > 1;

    const addButton = document.createElement("div");
    addButton.classList.add("add-button");
    addButton.innerHTML = `<span>＋</span>`;

    const images = [];

    // 📌 función para agregar imágenes nuevas desde FileReader

    const addImage = (file) => {
      if (images.length >= maxImages) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        const box = document.createElement("div");
        box.classList.add("image-box", `image-${styleType}`);

        const img = document.createElement("img");
        img.src = e.target.result;
        img.alt = "Uploaded Image";

        // 🔹 Crear input oculto en el DOM principal (fuera del shadowRoot)
        const form = this.closest('form');
        let hiddenInput = null;
        if (form) {
          hiddenInput = document.createElement("input");
          hiddenInput.type = "hidden";
          hiddenInput.name = maxImages === 1 ? fieldName : `${fieldName}_${images.length + 1}`;
          hiddenInput.value = e.target.result; // base64 de la imagen
          form.appendChild(hiddenInput);
        }

        const deleteBtn = document.createElement("div");
        deleteBtn.classList.add("delete-btn");
        deleteBtn.textContent = "✖";

        deleteBtn.addEventListener("click", () => {
          container.removeChild(box);
          images.splice(images.indexOf(file), 1);
          if (hiddenInput) hiddenInput.remove();
          if (images.length < maxImages) addButton.style.display = "flex";
        });

        box.appendChild(img);
        box.appendChild(deleteBtn);
        container.insertBefore(box, addButton);
        images.push(file);

        if (images.length >= maxImages) addButton.style.display = "none";
      };

      reader.readAsDataURL(file);
    };

    // 📌 función para agregar imágenes desde URL (preexistentes)
    const addImageFromUrl = (url, index) => {
      if (images.length >= maxImages) return;

      const img = new Image();
      img.onload = () => {
        // La imagen existe y cargó correctamente
        createImageBox(url, img, index);
      };

      img.src = url;

      img.onerror = () => {
        // La imagen no existe → crea solo el marco vacío
        createImageBox(null, null, index);
      };


    };

    // 📌 función general para crear el box
    const createImageBox = (src, file, index) => {
      const box = document.createElement("div");
      box.classList.add("image-box", `image-${styleType}`);

      const img = document.createElement("img");
      img.src = src;
      img.alt = "Uploaded Image";

      // 🔹 input oculto en el form
      const form = this.closest("form");
      let hiddenInput = null;
      if (form) {
        hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = maxImages === 1 ? fieldName : `${fieldName}_${index}`;
        hiddenInput.value = src;
        form.appendChild(hiddenInput);
      }

      const deleteBtn = document.createElement("div");
      deleteBtn.classList.add("delete-btn");
      deleteBtn.textContent = "✖";

      deleteBtn.addEventListener("click", () => {
        container.removeChild(box);
        if (hiddenInput) hiddenInput.remove();
        images.splice(images.indexOf(file), 1);
        if (images.length < maxImages) addButton.style.display = "flex";
      });

      box.appendChild(img);
      box.appendChild(deleteBtn);
      container.insertBefore(box, addButton);
      images.push(file || src);

      if (images.length >= maxImages) addButton.style.display = "none";
    };

    addButton.addEventListener("click", () => inputFile.click());
    inputFile.addEventListener("change", (e) => {
      if (e.target.files.length > 0) addImage(e.target.files[0]);
    });

    container.appendChild(addButton);
    this.shadowRoot.append(style, container, inputFile);

    // 📌 cargar imágenes iniciales desde atributos value-1, value-2...
    for (let i = 1; i <= maxImages; i++) {
      const url = this.getAttribute(`value-${i}`);
      if (url) {
        addImageFromUrl(url, i);
      }
    }
  }
}

class PlusPriority extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._value = 0;
    this._max = 3;
    this._allowNone = false;
    this._hiddenInput = null;
  }

  connectedCallback() {
    this._max = parseInt(this.getAttribute("max")) || 3;
    this._value = parseInt(this.getAttribute("value")) || 0;
    this._allowNone = this.hasAttribute("allow-none");
    const isEditable = !this.hasAttribute("notIsEditable");
    const name = this.getAttribute("name") || "priority";
    const id = this.getAttribute("id") || window.generate_unique_dom_id();

    // ===== styles =====
    const style = document.createElement("style");
    style.textContent = `
      .stars {
        display: flex;
        gap: 6px;
        cursor: pointer;
        user-select: none;
      }
      .star {
        font-size: 28px;
        color: #d1d5db;
        transition: transform 0.2s ease, color 0.3s ease;
      }
      .star.filled {
        color: #fbbf24;
        text-shadow: 0px 2px 6px rgba(0,0,0,0.15);
      }
      .star:hover {
        transform: scale(1.2);
      }
    `;

    // ===== hidden input only once in the light DOM =====
    if (!this._hiddenInput) {
      this._hiddenInput = document.createElement("input");
      this._hiddenInput.type = "hidden";
      if (name) this._hiddenInput.name = name;
      if (id) this._hiddenInput.id = id;
      this._hiddenInput.value = this._value;
      this.appendChild(this._hiddenInput); // light DOM (para enviar en formularios)
    }

    // ===== render stars =====
    const wrapper = document.createElement("div");
    wrapper.classList.add("stars");

    const renderStars = () => {
      wrapper.innerHTML = "";
      for (let i = 1; i <= this._max; i++) {
        const star = document.createElement("span");
        star.classList.add("star");
        star.innerHTML = "★";
        if (i <= this._value) {
          star.classList.add("filled");
        }

        if (isEditable) {
          star.addEventListener("click", () => {
            if (this._allowNone && i === this._value) {
              this._value = 0;
            } else {
              this._value = i;
            }
            this._hiddenInput.value = this._value;
            this.setAttribute("value", this._value);
            this.dispatchEvent(new CustomEvent("change", { detail: { value: this._value } }));
            renderStars(); // refresh the starts
          });
        } else {
          star.style.cursor = "default";
        }

        wrapper.appendChild(star);
      }
    };

    renderStars();

    // ===== clear shadow before re-rendering=====
    this.shadowRoot.innerHTML = "";
    this.shadowRoot.append(style, wrapper);
  }

  setValue(val) {
    const newValue = parseInt(val);
    if (!isNaN(newValue) && newValue >= 0 && newValue <= this._max) {
      this._value = newValue;
      this._hiddenInput.value = this._value;
      this.setAttribute("value", this._value);
      this.shadowRoot.querySelector(".stars").innerHTML = "";
      this.connectedCallback(); // volver a renderizar
    }
  }

  getValue() {
    return this._value;
  }
}

class PlusSwitchColumn extends HTMLElement {
  connectedCallback() {
    // Evitar duplicar wrapper si ya existe
    if (this.querySelector(".switch-wrapper")) return;

    const wrapper = document.createElement("div");
    wrapper.classList.add("switch-wrapper");

    // Col1 y Col2 envuelven lo que ya existe
    const slot1 = this.querySelector('[slot="col1"]');
    const slot2 = this.querySelector('[slot="col2"]');

    const col1 = document.createElement("div");
    col1.classList.add("col1");
    if (slot1) col1.appendChild(slot1);

    const col2 = document.createElement("div");
    col2.classList.add("col2");
    if (slot2) col2.appendChild(slot2);

    wrapper.appendChild(col1);
    wrapper.appendChild(col2);

    // Reemplazar contenido solo una vez
    this.innerHTML = "";
    this.appendChild(wrapper);

    // Insertar estilos globales una sola vez
    if (!document.getElementById("plus-switch-column-styles")) {
      const style = document.createElement("style");
      style.id = "plus-switch-column-styles";
      style.textContent = `
        plus-switch-column {
          display: block;
          width: 100%;
        }

        .switch-wrapper {
          position: relative;
          width: 100%;
        }

        .switch-wrapper .col1,
        .switch-wrapper .col2 {
          padding: 10px;
          box-sizing: border-box;
        }

        /* --- MÓVIL: col2 oculta y deslizable --- */
        @media (max-width: 768px) {
          .switch-wrapper .col1 {
            width: 100%;
          }
          .switch-wrapper .col2 {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            overflow-y: auto;
            background-color: #F6F5F8;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 9999;
          }
          .switch-wrapper .col2.active {
            transform: translateX(0);
          }
        }

        /* --- DESKTOP: columnas lado a lado --- */
        @media (min-width: 769px) {
          .switch-wrapper {
            display: flex;
          }
          .switch-wrapper .col1,
          .switch-wrapper .col2 {
            width: 50%;
            position: relative;
            height: auto;
            transform: none !important;
          }
        }
      `;
      document.head.appendChild(style);
    }

    this.col2 = col2;
  }
}

class ListButton extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          position: relative;
          display: inline-block;
          font-family: system-ui, sans-serif;
        }

        .main-btn {
          background-color: #2d8659;
          display: inline-block;
          padding: 10px 18px;
          font-size: 0.95rem;
          border: none;
          border-radius: var(--radius);
          cursor: pointer;
          transition: background 0.3s;
          color: white;
          margin-right: 0.5rem;
        }

        .main-btn:hover {
          background-color: #24704a;
        }

        .menu {
          position: absolute;
          top: 58px;
          left: 0;
          display: none;
          flex-direction: column;
          background: #ffffff;
          border-radius: 10px;
          box-shadow: 0 4px 10px rgba(0,0,0,0.15);
          padding: 6px;
          min-width: 180px;
          max-width: 200px;
          animation: fadeIn 0.2s ease;
          z-index: 10;
        }

        :host([open]) .menu {
          display: flex;
        }

        :host([flip]) .menu {
          left: auto;
          right: 0;
        }

        ::slotted(button) {
          all: unset;
          display: block;
          padding: 10px 12px;
          font-size: 14px;
          color: #333;
          cursor: pointer;
          border-radius: 6px;
          transition: background 0.2s ease, color 0.2s ease;
        }

        ::slotted(button:hover) {
          background: #f2f2f2;
          color: #111;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-5px); }
          to { opacity: 1; transform: translateY(0); }
        }
      </style>

      <button class="main-btn" title="Más opciones">+</button>
      <div class="menu">
        <slot></slot>
      </div>
    `;
  }

  connectedCallback() {
    const mainBtn = this.shadowRoot.querySelector(".main-btn");
    const menu = this.shadowRoot.querySelector(".menu");

    mainBtn.addEventListener("click", (e) => {
      e.stopPropagation();

      // Abrimos el menú
      this.toggleAttribute("open");

      // Calculamos si debemos voltear el menú
      const rect = menu.getBoundingClientRect();
      const viewportWidth = window.innerWidth;

      if (rect.right > viewportWidth) {
        this.setAttribute("flip", "");
      } else {
        this.removeAttribute("flip");
      }
    });

    // Close when clicking outside
    document.addEventListener("click", this._outsideHandler = (e) => {
      const path = e.composedPath();
      if (!path.includes(this)) this.removeAttribute("open");
    });

    // Close when choosing an option
    const slot = this.shadowRoot.querySelector("slot");
    slot.addEventListener("click", (e) => {
      if (e.target.nodeName === "BUTTON") this.removeAttribute("open");
    });
  }

  disconnectedCallback() {
    document.removeEventListener("click", this._outsideHandler);
  }
}

// Registrar componente
customElements.define("plus-switch-column", PlusSwitchColumn);

// Función para abrir/cerrar col2 en móviles
function toggle_switch_column(id, open = true) {
  const element = document.getElementById(id);
  if (!element || !element.col2) return;

  const isMobile = window.innerWidth <= 768;
  if (!isMobile) return; // Solo aplica en móviles

  if (open) {
    element.col2.classList.add("active");
  } else {
    element.col2.classList.remove("active");
  }
}

class PlusAccordion extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._isOpen = this.hasAttribute('open');
    }

    connectedCallback() {
        const baseStatic = window.STATIC_URLS ? window.STATIC_URLS.pathStatic : '/static/';
        const iconsPath = `${baseStatic}css/icons/uicons-regular-rounded.css`;
        this.render(iconsPath);
    }

    render(iconsPath) {
        const title = this.getAttribute('label') || 'Opciones';
        const t = this.getAttribute('t') || title;
        const translatedTitle = window.translate_text(t);

        this.shadowRoot.innerHTML = `
        <style>
            @import url('${iconsPath}');

            :host {
                display: block;
                margin-bottom: 12px;
                font-family: sans-serif;
            }

            .accordion-container {
                background: #fff;
                border-radius: 12px;
                overflow: hidden;
            }

            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 20px;
                cursor: pointer;
            }

            .icon {
                display: flex;
                align-items: center;
                transition: transform 0.4s ease;
                transform: ${this._isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
                color: #666B7F;
                font-size: 1.2rem;
            }

            .accordion-wrapper {
                display: grid;
                grid-template-rows: 0fr;
                transition: grid-template-rows 0.4s ease;
            }

            .accordion-wrapper.is-open {
                grid-template-rows: 1fr;
            }

            .content-overflow { overflow: hidden; }
            .content-padding { padding: 0 20px 20px 20px; }
            .title{
              font-size: .9rem;
            }
        </style>

        <div class="accordion-container">
            <div class="header" id="header">
                <span class="title" t="${t}">${translatedTitle}</span>
                <div class="icon">
                    <i class="fi fi-rr-angle-small-down"></i>
                </div>
            </div>

            <div class="accordion-wrapper ${this._isOpen ? 'is-open' : ''}">
                <div class="content-overflow">
                    <div class="content-padding">
                        <slot></slot>
                    </div>
                </div>
            </div>
        </div>
        `;

        this.shadowRoot.getElementById('header').addEventListener('click', () => this.toggle());
    }

    toggle() {
        this._isOpen = !this._isOpen;
        const wrapper = this.shadowRoot.querySelector('.accordion-wrapper');
        const icon = this.shadowRoot.querySelector('.icon');
        
        wrapper.classList.toggle('is-open', this._isOpen);
        icon.style.transform = this._isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
    }
}
/**----------------------------------LABELS OF EXTENSIONS AND PLUGINS----------------------**/
class PlusExtension extends HTMLElement {
    connectedCallback() {
        /**
         * CONDITIONAL RENDERING
         * ---------------------
         * Checks whether the extension should be rendered or not.
         * The condition is received as a string expression via the `if-condition` attribute.
         * 
         * Example:
         * <plus-extension if-condition="user.isAdmin">
         * 
         * ⚠️ WARNING:
         * Using eval() can be dangerous if the input is not controlled.
         * This assumes the condition comes from trusted code.
         */
        const condition = this.getAttribute('if-condition');
        if (condition && !eval(condition)) { 
            this.remove(); 
            return; 
        }

        /**
         * TARGET RESOLUTION
         * -----------------
         * Determines the DOM element where the extension will be injected.
         * Priority:
         * 1. CSS selector via `target` attribute
         * 2. Element ID via `extension_id`
         */
        const target = document.querySelector(
            this.getAttribute('target') || `#${this.getAttribute('extension_id')}`
        );

        /**
         * INSERTION STRATEGY
         * ------------------
         * Defines how the extension content will be inserted relative to the target.
         * Defaults to 'inside' (appendChild).
         */
        const position = this.getAttribute('position') || 'inside';
        
        /**
         * FUNCTION INTERCEPTION (PLUGIN HOOK)
         * -----------------------------------
         * Allows this extension to intercept a global function call.
         * 
         * - wrap_function: name of the global function to override
         * - before: name of a validation function executed before the original function
         * 
         * This is useful for:
         * - Permission checks
         * - Business rules
         * - Blocking actions dynamically
         */
        const functionToWrap = this.getAttribute('wrap_function');
        const validationFnName = this.getAttribute('before');

        if (functionToWrap && validationFnName) {
            this.wrapGlobalFunction(functionToWrap, validationFnName);
        }

        /**
         * If the target element exists, apply the extension content.
         */
        if (target) {
            this.applyExtension(target, position);
        }
    }

    wrapGlobalFunction(originalName, validationName) {
        /**
         * FUNCTION WRAPPING LOGIC
         * ----------------------
         * Stores a reference to the original global function
         * and replaces it with a guarded version.
         * 
         * Example:
         * - originalName: "submitForm"
         * - validationName: "canSubmitForm"
         */
        const originalFn = window[originalName];
        
        if (typeof originalFn === 'function') {
            /**
             * Replace the original function with a proxy function
             * that runs validation before execution.
             */
            window[originalName] = (...args) => {
                const validationFn = window[validationName];
                
                /**
                 * If validation function exists:
                 * - Execute it
                 * - Only call the original function if it returns true
                 */
                if (typeof validationFn === 'function') {
                    if (validationFn()) {
                        return originalFn(...args);
                    } else {
                        console.warn(
                            `Validation "${validationName}" failed. Blocking "${originalName}".`
                        );
                    }
                } else {
                    /**
                     * Fail-safe behavior:
                     * If the validation function does not exist,
                     * execute the original function to avoid breaking the app.
                     */
                    return originalFn(...args);
                }
            };
        }
    }

    applyExtension(target, position) {
        /**
         * CONTENT EXTRACTION
         * ------------------
         * Moves all child nodes of this custom element
         * into a DocumentFragment for efficient DOM insertion.
         */
        const fragment = document.createDocumentFragment();
        while (this.firstChild) {
            fragment.appendChild(this.firstChild);
        }

        /**
         * INSERTION STRATEGIES
         * --------------------
         * Defines how the fragment will be inserted relative to the target element.
         */
        const strategy = {
            'replace': () => target.replaceWith(fragment),
            'before': () => target.parentNode.insertBefore(fragment, target),
            'after': () => target.parentNode.insertBefore(fragment, target.nextSibling),
            'prepend': () => target.insertBefore(fragment, target.firstChild),
            'inside': () => target.appendChild(fragment)
        };

        /**
         * Execute the selected insertion strategy.
         * Defaults to 'inside' if the position is invalid or missing.
         */
        (strategy[position] || strategy['inside'])();

        /**
         * POST-APPLICATION STATE
         * ----------------------
         * The extension element itself remains in the DOM
         * but is hidden to avoid visual duplication.
         * 
         * Metadata attributes are added for debugging or auditing.
         */
        this.style.display = 'none'; 
        this.setAttribute('status', 'applied');
        this.setAttribute('applied-at', new Date().toISOString());    
    }
}

class PlusMove extends HTMLElement {
    connectedCallback() {
        /**
         * SOURCE ELEMENT
         * --------------
         * CSS selector that identifies the element to be moved.
         * Example:
         * <plus-move source="#saveButton" target="#toolbar" />
         */
        const sourceSelector = this.getAttribute('source');

        /**
         * TARGET ELEMENT
         * --------------
         * CSS selector that identifies the destination element.
         * The source element will be moved relative to this element.
         */
        const targetSelector = this.getAttribute('target');

        /**
         * INSERTION POSITION
         * ------------------
         * Defines how the source element will be inserted relative to the target.
         * Possible values:
         * - before   → before the target element
         * - after    → after the target element
         * - prepend  → as the first child of the target
         * - inside   → as the last child of the target (default)
         */
        const position = this.getAttribute('position') || 'inside';

        const sourceEl = document.querySelector(sourceSelector);
        const targetEl = document.querySelector(targetSelector);

        /**
         * VALIDATION
         * ----------
         * Ensures both source and target elements exist before attempting the move.
         */
        if (sourceEl && targetEl) {
            this.moveElement(sourceEl, targetEl, position);
        } else {
            console.warn(
                `PlusMove: Source (${sourceSelector}) or target (${targetSelector}) element not found.`
            );
        }

        /**
         * OPTIONAL MUTATIONS
         * ------------------
         * Allows the extension to modify the moved element
         * after relocation.
         */

        // Replace the element's entire class list
        if (this.getAttribute('set_class')) {
            sourceEl.className = this.getAttribute('set_class');
        }

        // Replace the element's text content
        if (this.getAttribute('set_text')) {
            sourceEl.innerText = this.getAttribute('set_text');
        }

        /**
         * SELF-DESTRUCTION
         * ----------------
         * The <plus-move> element removes itself after execution
         * to keep the DOM clean and avoid unnecessary nodes.
         */
        this.remove();
    }

    moveElement(source, target, position) {
        /**
         * MOVE STRATEGIES
         * ---------------
         * Handles different DOM insertion behaviors based on position.
         */
        switch (position) {
            case 'before':
                target.parentNode.insertBefore(source, target);
                break;

            case 'after':
                target.parentNode.insertBefore(source, target.nextSibling);
                break;

            case 'prepend':
                target.insertBefore(source, target.firstChild);
                break;

            case 'inside':
            default:
                target.appendChild(source);
                break;
        }
    }
}

class PlusPatch extends HTMLElement {
    connectedCallback() {
        /**
         * TARGET & PATCH DEFINITION
         * -------------------------
         * - target: CSS selector of the element to be patched
         * - set-attribute: list of attribute mutations to apply
         *
         * Example:
         * <plus-patch
         *   target="#email"
         *   set-attribute="required:true; placeholder:Enter your email; class:is-required"
         * />
         */
        const selector = this.getAttribute('target');
        const attrString = this.getAttribute('set-attribute');

        /**
         * If no target or patch definition is provided,
         * there is nothing to apply.
         */
        if (!selector || !attrString) return;

        const targetEl = document.querySelector(selector);

        if (targetEl) {
            this.applyPatch(targetEl, attrString);
        } else {
            /**
             * RENDER DELAY RETRY
             * ------------------
             * Some elements may not yet exist in the DOM
             * (e.g. dynamically rendered views or async components).
             *
             * A short retry window is used to apply the patch
             * once the element becomes available.
             */
            setTimeout(() => {
                const retryTarget = document.querySelector(selector);
                if (retryTarget) {
                    this.applyPatch(retryTarget, attrString);
                }
            }, 50);
        }

        /**
         * SELF-CLEANUP
         * ------------
         * The <plus-patch> element removes itself after execution
         * to avoid polluting the DOM with control-only nodes.
         */
        this.remove();
    }

    applyPatch(element, attrString) {
        /**
         * ATTRIBUTE PATCH PARSING
         * -----------------------
         * The attribute string is split into attribute:value pairs.
         *
         * Format:
         * "required:true; class:btn primary; placeholder:Your name"
         */
        const pairs = attrString.split(';');

        pairs.forEach(pair => {
            if (!pair.trim()) return;

            /**
             * Split only on the first ":" to allow values
             * that may contain colons themselves.
             */
            const [attrName, ...valueParts] = pair.split(':');
            const name = attrName.trim();
            const value = valueParts.join(':').trim();

            /**
             * CLASS HANDLING
             * --------------
             * Classes are additive and do not override
             * existing class names.
             */
            if (name === 'class') {
                element.classList.add(...value.split(' '));
            }
            /**
             * BOOLEAN ATTRIBUTES
             * ------------------
             * Handles attributes like:
             * - required
             * - disabled
             * - checked
             */
            else if (value === 'true' || value === '') {
                element.setAttribute(name, '');
            }
            /**
             * BOOLEAN REMOVAL
             * ----------------
             * Explicitly removes the attribute when set to false.
             */
            else if (value === 'false') {
                element.removeAttribute(name);
            }
            /**
             * STANDARD ATTRIBUTES
             * -------------------
             * Applies normal attributes such as:
             * - placeholder
             * - name
             * - value
             * - aria-*
             */
            else {
                element.setAttribute(name, value);
            }
        });
    }
}

const ExtensionEngine = {
    init() {
        /**
         * MUTATION OBSERVER
         * -----------------
         * Watches the DOM for newly added nodes in order to detect
         * extensions that are injected dynamically.
         *
         * This is essential for:
         * - AJAX-loaded content
         * - Modals
         * - Lazy-rendered views
         * - SPA-like navigation
         */
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    /**
                     * Only process element nodes whose tag name
                     * starts with "PLUS-" (custom extension elements).
                     */
                    if (node.nodeType === 1 && node.tagName.startsWith('PLUS-')) {
                        this.processExtension(node);
                    }
                });
            });
        });

        /**
         * Start observing the entire document body
         * for child additions at any depth.
         */
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        /**
         * INITIAL PASS
         * ------------
         * Process extensions that already exist in the DOM
         * at initialization time.
         */
        this.processAll();
    },

    processAll() {
        /**
         * EXTENSION COLLECTION
         * --------------------
         * Collects all known extension types supported
         * by the engine.
         */
        const extensions = Array.from(
            document.querySelectorAll('plus-extension, plus-move, plus-patch')
        );

        /**
         * PRIORITY SORTING
         * ----------------
         * Extensions can define an optional `priority` attribute.
         * Lower values are executed first.
         *
         * This allows deterministic execution order
         * when multiple extensions affect the same area.
         */
        extensions.sort(
            (a, b) =>
                (a.getAttribute('priority') || 0) -
                (b.getAttribute('priority') || 0)
        );

        /**
         * Execute each extension in order.
         */
        extensions.forEach(ext => this.processExtension(ext));
    },

    processExtension(ext) {
        /**
         * EXTENSION EXECUTION
         * -------------------
         * Manually triggers the extension logic.
         *
         * This design allows:
         * - Explicit lifecycle control
         * - Compatibility with dynamically injected elements
         * - Decoupling from native Custom Element lifecycle
         */
        if (typeof ext.execute === 'function') {
            ext.execute();
        }
    }
};
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
    currentPopZIndex += 1;
    overlay.style.zIndex = currentPopZIndex;
    overlay.style.display = 'flex';

    currentPopZIndex += 1;

    //now update the z index of the menu of the apps
    const appMenu = document.getElementById('appMenu');
    let currentZIndex = window.getComputedStyle(appMenu).getPropertyValue('z-index');

    //we will see if have a z-index, if have we will aument 1 to his value
    if (!isNaN(currentZIndex)) {
      let newZIndex = currentZIndex + 1;
      appMenu.style.zIndex = newZIndex;
    } else {
      //if not have a z-index, we will to create a z-index
      appMenu.style.zIndex = 1000;
    }
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

  overlay.style.zIndex = currentPopZIndex;
  overlay.style.zIndex += 1;

  pop.style.zIndex = currentPopZIndex + 2;
  pop.style.zIndex = currentPopZIndex + 3;
  pop.classList.remove('sub-menu-app-pop-info', 'sub-menu-app-pop-alert', 'sub-menu-app-pop-question', 'sub-menu-app-pop-normal', 'sub-menu-app-pop-error');
  pop.classList.add('sub-menu-app-pop-' + type);

  //icon for type
  /*
    success==green
    info, question==blue
    alert==yellow
    error==red
  */
  if (type === 'info') iconEl.innerHTML = '<i class="fi fi-sr-info"></i>';
  else if (type === 'success') iconEl.innerHTML = '<i class="fi fi-sr-check-circle"></i>';
  else if (type === 'alert') iconEl.innerHTML = '<i class="fi fi-sr-exclamation"></i>';
  else if (type === 'question') iconEl.innerHTML = '<i class="fi fi-sr-interrogation"></i>';
  else if (type === 'error') iconEl.innerHTML = '<i class="fi fi-ss-times-hexagon"></i>';
  else iconEl.innerHTML = '';

  //now we will see if the title is a text or have a structur of translate
  //if have a struct now we will to get his information and his text
  //-> show_alert('success', ['Hello ${name}, you have ${count} messages', { name: 'Edward', count: 3 }], ['Hello ${}, you have ${} messages', ['Edward', 3 ]])
  let titleStruct=get_text_and_keys(title);
  let descriptionStruct=get_text_and_keys(description)

  //update the text that show the alert pop
  titleEl.textContent = window.translate_text(titleStruct.text, titleStruct.keys);
  descEl.textContent = window.translate_text(descriptionStruct.text, descriptionStruct.keys);
  buttonsEl.innerHTML = '';

  //get the text of the buttons with the language that have the web. This is for update the text of all the button 
  const btnTextSuccess = window.t('message.success'); //buttonsEl.getAttribute('btnTextSuccess');
  const btnTextCancel = window.t('message.cancel'); //buttonsEl.getAttribute('btnTextCancel');
  const btnTextReadMost = window.t('info.read_most'); //buttonsEl.getAttribute('btnTextReadMost');

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

  //now we will see if the title is a text or have a structur of translate
  //if have a struct now we will to get his information and his text
  let messageStruct=get_text_and_keys(message);

  const alert = document.createElement('div');
  alert.style.zIndex = currentPopZIndex + 1;
  alert.className = `notification-alert ${type}`;
  alert.innerHTML = `
        <div class="icon">${icons[type] || icons['info']}</div>
        <div class="message">${window.translate_text(messageStruct.text, messageStruct.keys)}</div>
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

function on_visible(elementId, callback, runOnce = true) {
  //get the element that the user would like see if exist in the screen
    const element = document.getElementById(elementId);
    if (!element) {
      console.warn(`Element with id "${elementId}" not exist in the screen.`);
      return;
    }


    //here we will to prepare the observer for that we know when the element show in the screen
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                //run the function
                callback();

                // only if need run one time
                if (runOnce) {
                    observer.disconnect();
                }
            }
        });
    });

    observer.observe(element);
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

  if (!customElements.get("plus-switch")) {
    customElements.define("plus-switch", PlusSwitch);
  }

  if (!customElements.get("plus-help")) {
    customElements.define('plus-help', PlusHelp);
  }

  if (!customElements.get("plus-select-date")) {
    customElements.define('plus-select-date', PlusSelectDate);
  }

  if (!customElements.get("plus-tabs")) {
    customElements.define('plus-tabs', PlusTabs);
  }

  if (!customElements.get("plus-tab")) {
    customElements.define('plus-tab', PlusTab);
  }

  if (!customElements.get("plus-actions")) {
    customElements.define('plus-actions', PlusActions);
  }

  if (!customElements.get("plus-action")) {
    customElements.define('plus-action', class extends HTMLElement { });
  }

  if (!customElements.get("search-bar")) {
    customElements.define('search-bar', SearchBar);
  }

  if (!customElements.get("plus-date")) {
    customElements.define('plus-date', PlusDate);
  }

  if (!customElements.get("plus-time")) {
    customElements.define("plus-time", PlusTime);
  }

  if (!customElements.get("input-color")) {
    customElements.define("input-color", InputColor);
  }

  if (!customElements.get("plus-tags")) {
    customElements.define('plus-tags', PlusTag);
  }

  if (!customElements.get("plus-comment")) {
    customElements.define('plus-comment', PlusComment);
  }

  if (!customElements.get("edit-quantity")) {
    customElements.define('edit-quantity', EditQuantity);
  }

  if (!customElements.get("plus-filter-table")) {
    customElements.define('plus-filter-table', PlusFilterTable);
  }

  if (!customElements.get("plus-country")) {
    customElements.define('plus-country', PlusCountry);
  }

  if (!customElements.get("show-more")) {
    customElements.define("show-more", ShowMore);
  }

  if (!customElements.get("image-uploader")) {
    customElements.define("image-uploader", ImageUploader);
  }

  if (!customElements.get("plus-priority")) {
    customElements.define("plus-priority", PlusPriority);
  }

  if (!customElements.get("plus-title")) {
    customElements.define("plus-title", PlusTitle);
  }

  if (!customElements.get("plus-switch-column")) {
    customElements.define('plus-switch-column', PlusSwitchColumn);
  }

  if (!customElements.get("plus-search")) {
    customElements.define('plus-search', PlusSearch);
  }

  if(!customElements.get("list-button")){
    customElements.define('list-button', ListButton);
  }

  if(!customElements.get("plus-panel")){
    customElements.define('plus-panel', PlusPanel);
  }

  if(!customElements.get("plus-quantity")){
    customElements.define('plus-quantity', PlusQuantity);
  }

  /*EXTENSIONS AND PLUGINS*/
  if(!customElements.get("plus-extension")){
    customElements.define('plus-extension', PlusExtension);
  }

  if(!customElements.get("plus-move")){
    customElements.define('plus-move', PlusMove);
  }

  if(!customElements.get("plus-patch")){
    customElements.define('plus-patch', PlusPatch);
  }

  if(!customElements.get("plus-accordion")){
    customElements.define('plus-accordion', PlusAccordion);
  }
  
}

/**---------------------------------TAB----------------------------- */
function openTab(evt, tabId) {
  // Oculta todo el contenido de las pestañas
  const tabContents = document.querySelectorAll('.tab-content');
  tabContents.forEach(content => content.classList.remove('active'));

  // Quita la clase 'active' de todos los botones
  const tabButtons = document.querySelectorAll('.tab-buttons button');
  tabButtons.forEach(button => button.classList.remove('active'));

  // Muestra la pestaña seleccionada
  const selectedTab = document.getElementById(tabId);
  if (selectedTab) {
    selectedTab.classList.add('active');
  }

  // Marca el botón presionado como activo
  evt.currentTarget.classList.add('active');
}








/**---------------------------------SHOW MESSAGE POP PERSONALITY----------------------------- */
function open_my_pop(id) {
  const popElement = document.getElementById(id);
  if (popElement) {
    popElement.style.display = 'flex';
  }
}

function close_my_pop(id) {
  const popElement = document.getElementById(id);
  if (popElement) popElement.style.display = 'none';
}
