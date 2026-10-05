$(function () {
    $("form[data-validate]").on("submit", function (event) {
        const form = this;
        let firstInvalidField = null;

        $(form).find(":input[required]").each(function () {
            const isEmpty = !String($(this).val() || "").trim();
            this.setCustomValidity(isEmpty ? "Please fill out this field." : "");
            if (isEmpty && firstInvalidField === null) {
                firstInvalidField = this;
            }
        });

        if (firstInvalidField) {
            event.preventDefault();
            firstInvalidField.reportValidity();
        }
    });

    $(":input[required]").on("input change", function () {
        this.setCustomValidity("");
    });
});
