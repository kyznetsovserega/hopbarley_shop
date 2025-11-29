document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll(".quantity-counter");

    counters.forEach(counter => {
        const input = counter.querySelector(".quantity-value");
        if (!input) return;

        counter.addEventListener("click", (e) => {
            const btn = e.target.closest("button");
            if (!btn) return;

            const action = btn.dataset.action;
            let value = parseInt(input.value, 10);

            if (action === "increase" && value < 10) {
                input.value = value + 1;
            }

            if (action === "decrease" && value > 1) {
                input.value = value - 1;
            }
        });
    });
});
