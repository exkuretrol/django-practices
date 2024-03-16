$(function () {
    $("input[type='text'].dateinput").each(function (_, e) {
        $(e).daterangepicker({
            autoApply: true,
            singleDatePicker: true,
            startDate: new Date($(e).val()),
            endDate: new Date($(e).val()),
            locale: { format: "YYYY-MM-DD" },
        });
    });

    $(".btn-delete").each(function (_, e) {
        $(e).on("click", function (event) {
            event.preventDefault();
            let prefix = "#" + $(this).attr("prefix") + "-TOTAL_FORMS";
            $(prefix).val(parseInt($(prefix).val()) - 1);
            $(this).parent().find(".delete-checkbox").prop("checked", true);
            $(this).parent().addClass("d-none");
        });
    });
});
