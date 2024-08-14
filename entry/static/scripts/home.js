document.addEventListener('DOMContentLoaded', function() {
  // Get the greeting element
  const greetingElement = document.querySelector('.greeting-message');

  // Get the current hour
  const currentHour = new Date().getHours();

  // Define the greeting messages
  let greetingMessage = '';
  if (currentHour < 12) {
    greetingMessage = 'Good Morning! {{ current_user.name}}';
  } else if (currentHour < 18) {
    greetingMessage = 'Good Afternoon! {{ current_user.name}}';
  } else {
    greetingMessage = 'Good Evening! {{ current_user.name}}';
  }
  const h1Element = document.createElement('h1');
  h1Element.textContent = greetingMessage;

  greetingElement.innerHTML = '';
  greetingElement.appendChild(h1Element);
});

// Wait for the DOM to be fully loaded before executing the code
document.addEventListener("DOMContentLoaded", function() {
    // Get references to the elements you want to add click event listeners to
    const deliveryCard = document.querySelector(".delivery");
    const secureCard = document.querySelector(".secure");

    // Get references to the policy content sections
    const timelyDeliverySection = document.getElementById("timelyDelivery");
    const secureParcelHandlingSection = document.getElementById("secureParcelHandling");
    const policySection = document.getElementById("policySection");

    // Add click event listeners to the cards
    deliveryCard.addEventListener("click", function() {
        // Hide the other policy content section
        secureParcelHandlingSection.style.display = "none";
        // Display the timely delivery policy content section
        timelyDeliverySection.style.display = "block";
        // Show the policy section
        policySection.style.display = "block";
    });

    secureCard.addEventListener("click", function() {
        // Hide the other policy content section
        timelyDeliverySection.style.display = "none";
        // Display the secure parcel handling policy content section
        secureParcelHandlingSection.style.display = "block";
        // Show the policy section
        policySection.style.display = "block";
    });

    // Get reference to the close policy button
    const closePolicyBtn = document.getElementById("closePolicyBtn");

    // Add click event listener to close the policy section when close button is clicked
    closePolicyBtn.addEventListener("click", function() {
        // Hide the policy section
        policySection.style.display = "none";
    });
});
