const payButton = document.getElementById("pay-button");

if (payButton) {
    const options = {
        key: payButton.dataset.keyId,
        amount: payButton.dataset.amount,
        currency: "INR",
        name: "NuzahNaksh",
        description: `Payment for Order ${payButton.dataset.orderNumber}`,
        order_id: payButton.dataset.orderId,

        handler: function (response) {
            const form = document.getElementById("verification-form");

            form.elements["razorpay_payment_id"].value =
                response.razorpay_payment_id;

            form.elements["razorpay_order_id"].value =
                response.razorpay_order_id;

            form.elements["razorpay_signature"].value =
                response.razorpay_signature;

            form.submit();
        },

        theme: {
            color: "#b86670"
        }
    };

    const razorpayCheckout = new Razorpay(options);

    payButton.addEventListener("click", function () {
        razorpayCheckout.open();
    });

    razorpayCheckout.on("payment.failed", function () {
        alert("Payment failed. Your order has not been confirmed.");
    });
}