document.addEventListener('DOMContentLoaded', function() {

    // ============================================================
    // MAIN PAGE LOGIC (Catalog Filters, Sort, Tags)
    // ============================================================

    const homePageContent = document.querySelector('.main-content-grid');
    if (homePageContent) {
        // 1. Sort Buttons
        const sortButtons = document.querySelectorAll('.sort-options .sort-button');
        sortButtons.forEach(button => {
            button.addEventListener('click', function() {
                sortButtons.forEach(btn => btn.classList.remove('active-sort'));
                this.classList.add('active-sort');
            });
        });

        // 2. Keywords/Tags + Checkboxes
        const keywordsList = document.querySelector('.keywords-list');
        const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');

        if (keywordsList && checkboxes.length > 0) {

            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const keyword = this.dataset.keyword;
                    if (this.checked) {
                        if (!document.querySelector(`.keyword-tag[data-keyword="${keyword}"]`)) {
                            const newTag = document.createElement('span');
                            newTag.className = 'keyword-tag';
                            newTag.dataset.keyword = keyword;
                            newTag.innerHTML = `${keyword} <i class="fa-solid fa-xmark remove-keyword-icon"></i>`;
                            keywordsList.appendChild(newTag);
                        }
                    } else {
                        const tagToRemove = document.querySelector(`.keyword-tag[data-keyword="${keyword}"]`);
                        if (tagToRemove) tagToRemove.remove();
                    }
                });
            });

            keywordsList.addEventListener('click', function(event) {
                const keywordIcon = event.target.closest('.remove-keyword-icon');
                if (keywordIcon) {
                    const keywordTag = keywordIcon.closest('.keyword-tag');
                    const keywordText = keywordTag.dataset.keyword;
                    const checkbox = document.querySelector(`.checkbox-container input[data-keyword="${keywordText}"]`);
                    if (checkbox) checkbox.checked = false;
                    keywordTag.remove();
                }
            });
        }
    }


    // ============================================================
    // PRODUCT DETAIL PAGE LOGIC
    // ============================================================

    const productPageContent = document.querySelector('.page-product');
    if (productPageContent) {

        // Accordion
        const accordionTitle = document.querySelector('.accordion-title');
        if (accordionTitle) {
            accordionTitle.addEventListener('click', function() {
                this.closest('.accordion-item').classList.toggle('active');
            });
        }

        // --- AUTO SCROLL TO REVIEW FORM (?review=1) ---
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("review") === "1") {
            const reviewForm = document.querySelector(".add-review-form");
            if (reviewForm) {
                reviewForm.scrollIntoView({ behavior: "smooth", block: "center" });
                reviewForm.style.transition = "box-shadow 0.3s ease";
                reviewForm.style.boxShadow = "0 0 12px 4px rgba(255, 140, 0, 0.6)";
                setTimeout(() => reviewForm.style.boxShadow = "none", 2000);
            }
        }

        // Cart Counter Preview (if used)
        const cartControls = document.querySelector('.cart-controls');
        if (cartControls) {
            const addToCartBtn = cartControls.querySelector('#add-to-cart-btn');
            const quantityCounter = cartControls.querySelector('#quantity-counter');

            if (addToCartBtn && quantityCounter) {
                const decreaseBtn = quantityCounter.querySelector('[data-action="decrease"]');
                const increaseBtn = quantityCounter.querySelector('[data-action="increase"]');
                const quantityValueSpan = quantityCounter.querySelector('.quantity-value');

                let quantity = 0;

                function updateView() {
                    if (quantity === 0) {
                        addToCartBtn.classList.remove('is-hidden');
                        quantityCounter.classList.add('is-hidden');
                    } else {
                        addToCartBtn.classList.add('is-hidden');
                        quantityCounter.classList.remove('is-hidden');
                        quantityValueSpan.textContent = `${quantity} in cart`;
                    }
                }

                addToCartBtn.addEventListener('click', () => { quantity = 1; updateView(); });
                decreaseBtn.addEventListener('click', () => { if (quantity > 0) quantity--; updateView(); });
                increaseBtn.addEventListener('click', () => { quantity++; updateView(); });

                updateView();
            }
        }
    }


    // ============================================================
    // CART PAGE LOGIC (front-only visual adjustments)
    // ============================================================

    const cartPageContent = document.querySelector('.cart-page-wrapper');
    if (cartPageContent) {

        const cartTotalPriceElem = document.getElementById('cart-total-price');

        function updateCartTotal() {
            let total = 0;
            document.querySelectorAll('.cart-item').forEach(item => {
                const priceText = item.querySelector('[data-item-total-price]').textContent;
                if (priceText) total += parseFloat(priceText.replace('$', ''));
            });
            if (cartTotalPriceElem) {
                cartTotalPriceElem.textContent = `$${total.toFixed(2)}`;
            }
        }

        const cartItemsList = document.getElementById('cart-items-list');
        if (cartItemsList) {
            cartItemsList.addEventListener('click', function(event) {
                const cartItem = event.target.closest('.cart-item');
                if (!cartItem) return;

                const quantityElem = cartItem.querySelector('.quantity-value-cart');
                const itemTotalElem = cartItem.querySelector('[data-item-total-price]');
                const basePrice = parseFloat(cartItem.dataset.price);
                let quantity = parseInt(quantityElem.textContent);

                if (event.target.closest('[data-action="increase"]')) {
                    quantity++;
                } else if (event.target.closest('[data-action="decrease"]')) {
                    quantity = quantity > 1 ? quantity - 1 : 0;
                }

                if (event.target.closest('[data-action="remove"]') || quantity === 0) {
                    cartItem.remove();
                } else {
                    quantityElem.textContent = quantity;
                    itemTotalElem.textContent = `$${(basePrice * quantity).toFixed(2)}`;
                }

                updateCartTotal();
            });
        }

        updateCartTotal();
    }


    // ============================================================
    // ACCOUNT PAGE (tabs + image preview)
    // ============================================================

    const accountAdminWrapper = document.querySelector('.account-page-wrapper, .admin-page-wrapper');
    if (accountAdminWrapper) {

        const accountTabs = document.querySelectorAll('.account-tab');
        const tabPanes = document.querySelectorAll('.tab-pane');

        if (accountTabs.length > 0) {
            accountTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    accountTabs.forEach(i => i.classList.remove('active'));
                    tabPanes.forEach(p => p.classList.remove('active'));

                    this.classList.add('active');
                    const targetPane = document.querySelector(this.dataset.tabTarget);
                    if (targetPane) targetPane.classList.add('active');
                });
            });
        }

        // Upload image preview (if used)
        const uploadButton = document.getElementById('upload-image-btn');
        const fileInput = document.getElementById('image-upload-input');

        if (uploadButton && fileInput) {
            uploadButton.addEventListener('click', () => fileInput.click());

            fileInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    const placeholder = document.querySelector('.image-upload-placeholder');

                    reader.onload = function(e) {
                        placeholder.innerHTML = '';
                        placeholder.style.backgroundImage = `url('${e.target.result}')`;
                        placeholder.style.backgroundSize = 'cover';
                        placeholder.style.backgroundPosition = 'center';
                    };

                    reader.readAsDataURL(file);
                }
            });
        }
    }

});
