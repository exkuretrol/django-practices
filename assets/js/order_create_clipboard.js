$(function () {
    let clipboard_text = null;
    document.getElementById("generate").addEventListener("click", function () {
        // TODO: add some validation
        navigator.clipboard
            .readText()
            .then((text) => {
                let input_clipboard = $("#id_clipboard");
                input_clipboard.val(text);
                input_clipboard
                    .parent()
                    .find("input[type='submit']")
                    .trigger("submit");
            })
            .catch((err) => {
                console.error("Failed to read clipboard contents: ", err);
            });
    });
});
