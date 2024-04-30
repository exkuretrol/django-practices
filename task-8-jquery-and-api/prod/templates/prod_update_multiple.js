$(function () {
    let timeout;
    let excel_table = $("#id_excel_table");
    let output = $("#output");
    let btn_update = $("#btn_update");
    let tbl_json = [];
    excel_table.on("keyup", (_) => {
        clearTimeout(timeout);
        timeout = setTimeout(function () {
            let table_str = excel_table.val();
            if (!form_validation(table_str)) {
                output.empty().append("table is not valid");
            } else {
                tbl_json = generate_table(table_str);

                $("#id_prod_no").val(
                    extract_product_no_to_list(tbl_json).join(",")
                );
                btn_update.removeAttr("disabled").removeClass("disabled");
            }
        }, 800);
    });

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
     * Validates the form based on the provided table string.
     *
     * @param {string} table_str - The table string to validate.
     */
    function generate_table(table_str) {
        // TODO: remove empty rows
        let rows = table_str.split("\n");
        let table = [];
        for (let row_num in rows) {
            let row = remove_extra_tabs(rows[row_num]);
            let cells = row.split("\t");
            let obj = {};
            for (let cell_num in cells) {
                let cell = cells[cell_num];
                let header = get_header(cell_num);
                if (row_num !== "0") {
                    obj[header] = cell;
                }
            }
            if (row_num !== "0") {
                table.push(obj);
            }
        }
        return table;
    }

    /**
     *
     * @param {[Object]} table_json
     */
    function extract_product_no_to_list(table_json) {
        return table_json.map((prod) => {
            return prod.prod_no;
        });
    }

    /**
     * Get the header based on the cell number.
     *
     * @param {number} cell_num - The cell number.
     * @returns {string} - The header corresponding to the cell number.
     */
    function get_header(cell_num) {
        const headers = ["prod_no", "prod_quantity"];
        return headers[cell_num] || "";
    }
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
     *
     * @param {[Object]} obj_list
     */
    function update_prods(obj_list) {
        $.ajax({
            url: "{% url 'api:update_products' %}",
            method: "put",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json",
            },
            data: JSON.stringify(obj_list),
            success: (_) => {
                $("#btn_query").trigger("click");
            },
        });
    }

    btn_update.on("click", (e) => {
        e.preventDefault();
        update_prods(tbl_json);
    });
});
