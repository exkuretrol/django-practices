$(function () {
    document.getElementById("generate").addEventListener("click", function () {
        navigator.clipboard
            .read()
            .then((text) => {
                console.log("Pasted content: ", text);
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
