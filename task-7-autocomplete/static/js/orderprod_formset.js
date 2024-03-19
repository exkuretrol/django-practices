$(function () {
    $(".btn-delete").each(function (_, e) {
        $(e).on("click", function (event) {
            event.preventDefault();
            let prefix = "#" + $(this).attr("prefix") + "-TOTAL_FORMS";
            $(prefix).val(parseInt($(prefix).val()) - 1);
            $(this).parent().find(".delete-checkbox").prop("checked", true);
            $(this).parent().addClass("d-none");
        });
    });

    $(".input-group").each(function () {
        $(this)
            .children()
            .filter(":not(.d-none):not(span):not([type='hidden'])")
            .last()
            .attr(
                "style",
                "border-top-right-radius: var(--bs-border-radius); border-bottom-right-radius: var(--bs-border-radius);"
            );
    });
});
