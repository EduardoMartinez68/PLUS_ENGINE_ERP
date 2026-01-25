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
