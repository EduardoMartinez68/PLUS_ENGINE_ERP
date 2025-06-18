const steps = document.querySelectorAll(".status-step");
const hiddenInput = document.getElementById("statusValue");

steps.forEach((step, index) => {
    step.addEventListener("click", () => {
        steps.forEach((s, i) => {
            s.classList.remove("completed", "active");
            if (i < index) s.classList.add("completed");
            if (i === index) s.classList.add("active");
        });
        hiddenInput.value = step.textContent.trim();
    });
});