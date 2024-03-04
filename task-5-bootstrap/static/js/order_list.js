$(function () {
    /**
     * hide the inputs and convert to datepicker
     * @param {string} input_id
     */
    function convert_to_datepicker(input_id) {
        let input_0 = $("#" + input_id + "_0");
        let input_1 = $("#" + input_id + "_1");
        input_0.attr("type", "hidden");
        input_1.attr("type", "hidden");
        let parent = input_0.parent();
        parent
            .contents()
            .filter(function () {
                return this.nodeType === 3;
            })
            .remove();

        parent.append(`<input type='text' id='id_${input_id}_datepicker'/>`);
        let date_datepicker = $(`#id_${input_id}_datepicker`).addClass(
            input_0.attr("class")
        );
        if (input_id !== "id_od_except_arrival_date") {
            if (input_0.val() === "") {
                let currentDate = new Date();
                currentDate.setDate(currentDate.getDate() - 7);
                input_0.val(currentDate.toISOString().split("T")[0]);
            }
            if (input_1.val() === "") {
                let currentDate = new Date();
                input_1.val(currentDate.toISOString().split("T")[0]);
            }
        }
        date_datepicker.daterangepicker(
            {
                startDate: input_0.val() !== "" ? input_0.val() : new Date(),
                endDate: input_1.val() !== "" ? input_1.val() : new Date(),
                opens: "left",
                locale: {
                    format: "YYYY-MM-DD",
                    cancelLabel: "清空",
                    applyLabel: "確定",
                },
                // autoApply: true,
                autoUpdateInput: input_0.val() !== "" ? true : false,
            },
            function (start, end, label) {
                input_0.val(start.format("YYYY-MM-DD"));
                input_1.val(end.format("YYYY-MM-DD"));
            }
        );
        date_datepicker.on("apply.daterangepicker", function (ev, picker) {
            $(this).val(
                picker.startDate.format("YYYY-MM-DD") +
                    " - " +
                    picker.endDate.format("YYYY-MM-DD")
            );
        });
        date_datepicker.on("cancel.daterangepicker", function (ev, picker) {
            picker.element.val("");
            input_0.val("");
            input_1.val("");
        });
    }
    convert_to_datepicker("id_od_date");
    convert_to_datepicker("id_od_except_arrival_date");
});

/**
 * clear the filter form
 */
function clearFilter() {
    let form = $("#order-filter-form");
    form.find("input:not([type='submit']):not([type='button'])").val("");
}
