console.log("Keywords.js loaded");
document.addEventListener("DOMContentLoaded", function () {
    const keywordsButtons = document.querySelectorAll(".keyword-button");
    keywordsButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const kw = this.value;
            const form = document.getElementById("search-sort-form");
            const hidden = document.createElement("input");
            hidden.type = "hidden";
            hidden.name = "keywords";
            hidden.value = kw;
            form.appendChild(hidden);
            form.submit();
        });
    });
});
