document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll(".quantity-counter");

    counters.forEach(counter => {
        const input = counter.querySelector(".quantity-value");
        const btnIncrease = counter.querySelector('[data-action="increase"]');
        const btnDecrease = counter.querySelector('[data-action="decrease"]');

        if (!input || !btnIncrease || !btnDecrease) return;

        const min = parseInt(input.min) || 1;
        const max = parseInt(input.max) || 9999; // fallback на случай отсутствия max

        // ---- УВЕЛИЧЕНИЕ ----
        btnIncrease.addEventListener("click", () => {
            let value = parseInt(input.value);

            if (value < max) {
                input.value = value + 1;
            }
        });

        // ---- УМЕНЬШЕНИЕ ----
        btnDecrease.addEventListener("click", () => {
            let value = parseInt(input.value);

            if (value > min) {
                input.value = value - 1;
            }
        });

        // ---- КОРРЕКЦИЯ РУЧНОГО ВВОДА ----
        input.addEventListener("input", () => {
            let value = parseInt(input.value);

            if (isNaN(value) || value < min) {
                input.value = min;
            } else if (value > max) {
                input.value = max;
            }
        });
    });
});
