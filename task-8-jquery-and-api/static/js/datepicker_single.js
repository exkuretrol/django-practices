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
});
