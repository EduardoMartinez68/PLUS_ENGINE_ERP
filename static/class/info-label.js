
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

    const keyLabelText = this.getAttribute("label") || "";
    const keyMessage = this.getAttribute("message") || "";

    const labelText = typeof translate_text === "function" ? translate_text(keyLabelText) : keyLabelText;
    const message = typeof translate_text === "function" ? translate_text(keyMessage) : keyMessage;

    const label = document.createElement("label");
    label.classList.add("info-label-generated");

    const span = document.createElement("span");
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
