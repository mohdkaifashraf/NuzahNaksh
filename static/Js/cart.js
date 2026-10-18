document.addEventListener("DOMContentLoaded", function () {
    const quantityInput = document.getElementById("quantity");
    const decreaseBtn = document.getElementById("decrease-qty");
    const increaseBtn = document.getElementById("increase-qty");

    if (quantityInput && decreaseBtn && increaseBtn) {
        const minVal = parseInt(quantityInput.getAttribute("min")) || 1;
        const maxVal = parseInt(quantityInput.getAttribute("max")) || 999;

        decreaseBtn.addEventListener("click", function () {
            let currentVal = parseInt(quantityInput.value) || 1;
            if (currentVal > minVal) {
                quantityInput.value = currentVal - 1;
            }
        });

        increaseBtn.addEventListener("click", function () {
            let currentVal = parseInt(quantityInput.value) || 1;
            if (currentVal < maxVal) {
                quantityInput.value = currentVal + 1;
            }
        });
    }
});
