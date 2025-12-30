// ============================
// OPTION SELECTION LOGIC
// ============================

document.querySelectorAll(".option-group").forEach(group => {
    const options = group.querySelectorAll(".option");

    options.forEach(option => {
        option.addEventListener("click", () => {

            // remove active from all options in this group
            options.forEach(opt => opt.classList.remove("active"));

            // add active to clicked option
            option.classList.add("active");

            // update hidden input value
            const inputName = group.dataset.name;
            const hiddenInput = document.querySelector(
                `input[name="${inputName}"]`
            );

            if (hiddenInput) {
                hiddenInput.value = option.dataset.value;
            }
        });
    });
});

// ============================
// TAB SWITCHING
// ============================

const tabs = document.querySelectorAll(".tab");
const tabContents = document.querySelectorAll(".tab-content");

tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tabContents.forEach(c => c.classList.remove("active"));

        tab.classList.add("active");
        document
            .getElementById(tab.dataset.tab)
            .classList.add("active");
    });
});

// ============================
// OPTION SELECTION
// ============================

document.querySelectorAll(".option-group").forEach(group => {
    const options = group.querySelectorAll(".option");

    options.forEach(option => {
        option.addEventListener("click", () => {
            options.forEach(o => o.classList.remove("active"));
            option.classList.add("active");

            const inputName = group.dataset.name;
            const hiddenInput = document.querySelector(
                `input[name="${inputName}"]`
            );

            if (hiddenInput) {
                hiddenInput.value = option.dataset.value;
            }
        });
    });
});

