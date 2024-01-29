$(function () {
    let timeout;
    let excel_table = $("#id_excel_table");
    let output = $("#output");
    let btn_create = $("#btn_create");
    let tbl_json = [];
    excel_table.on("keyup", (_) => {
        clearTimeout(timeout);
        timeout = setTimeout(function () {
            let table_str = excel_table.val();
            if (!form_validation(table_str)) {
                output.empty().append("table is not valid");
            } else {
                tbl_json = generate_table(table_str);
                btn_create.removeAttr("disabled").removeClass("disabled");
            }
        }, 800);
    });

    btn_create.on("click", (e) => {
        e.preventDefault();
        create_prods(tbl_json);
    });

    /**
     *
     *
     * @param {string} table_str
     * @return {string}
     */
    function remove_extra_tabs(table_str) {
        return table_str.replace(new RegExp("\t\t", "g"), "\t");
    }
    /**
     * Validates the form based on the provided table string.
     *
     * @param {string} table_str - The table string to validate.
     */
    function generate_table(table_str) {
        // TODO: remove empty rows
        let rows = table_str.split("\n");
        let table = [];
        let htmlTable = $("<table>");
        for (let row_num in rows) {
            let row = remove_extra_tabs(rows[row_num]);
            let cells = row.split("\t");
            let obj = {};
            let htmlTr = $("<tr>");
            for (let cell_num in cells) {
                let cell = cells[cell_num];
                let header = get_header(cell_num);
                if (row_num !== "0") {
                    obj[header] = cell;
                }
                let htmlTd = $("<td>");
                htmlTd.text(cell);
                htmlTr.append(htmlTd);
            }
            htmlTable.append(htmlTr);
            if (row_num !== "0") {
                table.push(obj);
            }
        }
        output.empty().append(htmlTable);
        return table;
    }

    /**
     *
     * @param {string} table_str
     * @returns {bool}
     */
    function form_validation(table_str) {
        if (!table_str.includes("\t")) return false;
        return true;
    }

    /**
     * Get the header based on the cell number.
     *
     * @param {number} cell_num - The cell number.
     * @returns {string} - The header corresponding to the cell number.
     */
    function get_header(cell_num) {
        const headers = [
            "prod_no",
            "prod_name",
            "prod_desc",
            "prod_type",
            "prod_img",
            "prod_quantity",
            "prod_status",
        ];
        return headers[cell_num] || "";
    }

    function create_prods(json) {
        $.ajax({
            url: "{% url 'ajax_post_prods' %}",
            method: "post",
            headers: { "X-CSRFToken": "{{ csrf_token }}" },
            data: { prods: JSON.stringify(json) },
            success: (_) => {
                output.text(_["message"])
            },
        });
    }
});
