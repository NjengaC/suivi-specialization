document.addEventListener('DOMContentLoaded', function () {
    const formFields = document.querySelectorAll('.send_form input, .send_form select, .send_form textarea');
    const steps = document.querySelectorAll('.step');

    formFields.forEach(function (field) {
        field.addEventListener('input', function () {
            updateSteps();
        });
    });

    function updateSteps() {
        let isFormCompleted = true;

        formFields.forEach(function (field) {
            if (field.value.trim() === '') {
                isFormCompleted = false;
            }
        });

        if (isFormCompleted) {
            steps.forEach(function (step) {
                step.classList.add('completed');
            });
        }
    }
});
