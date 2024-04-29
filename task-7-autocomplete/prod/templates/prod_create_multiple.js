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
            for (i = 0; i < cells.length; i++) {
                let cell = cells[i];
                let header = get_header(i);
                if (row_num !== "0") {
                    if (i === 0 || i === 4 || i === 6 || i === 7 || i === 8)
                        cell = parseInt(cell);
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
            "prod_img",
            "prod_quantity",
            "prod_cate_no",
            "prod_sales_status",
            "prod_quality_assurance_status",
            "prod_mfr_id",
        ];
        return headers[cell_num] || "";
    }

    function create_prods(json) {
        $.ajax({
            url: "{% url 'api:create_product' %}",
            method: "post",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json",
            },
            data: JSON.stringify(json),
            success: (_) => {
                output.text(_["message"]);
            },
        });
    }
});
