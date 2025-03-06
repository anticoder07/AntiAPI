// Validator object
function Validator(options) {
    let selectorRules = {};

    function getParent(element, selector) {
        while (element.parentElement) {
            if (element.parentElement.matches(selector)) {
                return element.parentElement;
            }
            element = element.parentElement;
        }
    }

    function validate(inputElement, element) {
        let rules = selectorRules[element.selector];
        let errorMessage;

        for (let i = 0; i < rules.length; ++i) {
            switch (inputElement.type) {
                case "radio":
                case "checkbox":
                    errorMessage = rules[i](
                        formElement.querySelector(element.selector + ":checked")
                    );
                    break;
                default:
                    errorMessage = rules[i](inputElement.value);
            }
            if (errorMessage) break;
        }

        let formMessage = getParent(
            inputElement,
            options.formGroupSelector
        ).querySelector(".form-message");

        if (errorMessage) {
            formMessage.innerText = errorMessage;
            getParent(inputElement, options.formGroupSelector).classList.add(
                "invalid"
            );
        } else {
            formMessage.innerText = "";
            getParent(inputElement, options.formGroupSelector).classList.remove(
                "invalid"
            );
        }
        return errorMessage;
    }

    let formElement = document.querySelector(options.form);
    if (formElement) {
        formElement.onsubmit = function (e) {
            e.preventDefault();

            let isFormValid = true;

            options.rules.forEach(function (element) {
                let inputElement = formElement.querySelector(element.selector);
                if (validate(inputElement, element)) isFormValid = false;
            });

            if (isFormValid) {
                if (typeof options.onSubmit === "function") {
                    let enableInputs = formElement.querySelectorAll(
                        "[name]:not([disabled])"
                    );

                    let formValues = Array.from(enableInputs).reduce(function (
                            values,
                            input
                        ) {
                            switch (input.type) {
                                case "checkbox":
                                    if (!input.matches(":checked")) {
                                        values[input.name] = "";
                                        return values;
                                    }
                                    if (!Array.isArray(values[input.name])) {
                                        values[input.name] = [];
                                    }
                                    values[input.name].push(input.value);
                                    break;
                                case "file":
                                    values[input.name] = input.files;
                                    break;
                                default:
                                    values[input.name] = input.value;
                            }
                            return values;
                        },
                        {});

                    options.onSubmit(formValues);
                } else {
                    formElement.submit();
                }
            }
        };

        options.rules.forEach(function (element) {
            if (Array.isArray(selectorRules[element.selector])) {
                selectorRules[element.selector].push(element.test);
            } else {
                selectorRules[element.selector] = [element.test];
            }

            let inputElements = formElement.querySelectorAll(element.selector);

            Array.from(inputElements).forEach(function (inputElement) {
                if (inputElement) {
                    inputElement.onblur = function () {
                        validate(inputElement, element);
                    };

                    inputElement.oninput = function () {
                        let formMessage = getParent(
                            inputElement,
                            options.formGroupSelector
                        ).querySelector(".form-message");
                        formMessage.innerText = "";
                        getParent(inputElement, options.formGroupSelector).classList.remove(
                            "invalid"
                        );
                    };
                }
            });
        });
    }
}

// Define rules
Validator.isRequired = function (selector, message) {
    // This is to check if a field is required
    return {
        selector: selector,
        test: function (value) {
            return value ? undefined : message || "Please fill out this field";
        },
    };
};

Validator.isEmail = function (selector, message) {
    // This is to check if the field is in email format
    return {
        selector: selector,
        test: function (value) {
            var regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
            return regex.test(value)
                ? undefined
                : message || "This field must be an email address";
        },
    };
};

Validator.rangeLength = function (selecter, min, max, message) {
    return {
        selector: selecter,
        test: function (value) {
            return min <= value.length && max >= value.length
                ? undefined
                : message ||
                "Password length must be between " + min + " and " + max + " characters";
        },
    };
};

Validator.isConfirmed = function (selector, objectConfirm, message) {
    return {
        selector: selector,
        test: function (value) {
            return value === objectConfirm()
                ? undefined
                : message || "The confirmation password does not match";
        },
    };
};
