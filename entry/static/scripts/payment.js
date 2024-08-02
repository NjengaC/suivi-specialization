// Create a Stripe client
var stripe = Stripe('pk_live_838dd40463bf4548983e057d966ff390e86145e4');

// Create an instance of Elements
var elements = stripe.elements();

// Create an instance of the card Element
var card = elements.create('card');

// Add an instance of the card Element into the `card-element` div
card.mount('#card-element');

// Handle real-time validation errors from the card Element
card.on('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
});

// Handle form submission
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
    event.preventDefault();

    stripe.createToken(card).then(function(result) {
        if (result.error) {
            // Inform the user if there was an error
            var errorElement = document.getElementById('card-errors');
            errorElement.textContent = result.error.message;
        } else {
            // Send the token to your server for payment verification
            var token = result.token;
            verifyPayment(token);
        }
    });
});

// Function to send token to server for payment verification and email notification
function verifyPayment(token) {
    // Prepare data to send to server
    var formData = new FormData();
    formData.append('stripeToken', token.id);

    // Send data to server using fetch API
    fetch('/verify_payment', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok');
    })
    .then(data => {
        // Handle success response from server
        console.log('Payment verification successful:', data);
        // Optionally, redirect to a success page
        window.location.href = '/payment_success';
    })
    .catch(error => {
        // Handle error
        console.error('Error verifying payment:', error);
        // Display an error message to the user
        var errorElement = document.getElementById('card-errors');
        errorElement.textContent = 'Error verifying payment. Please try again.';
    });
}
