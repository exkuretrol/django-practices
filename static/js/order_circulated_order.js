const data = document.currentScript.dataset;
$(function () {
    function alert_div_set(status, content = null) {
        var alert_div = $("div[role=alert]");

        alert_div.removeClass("alert-success").removeClass("alert-danger");
        if (status == "hidden") {
            alert_div.addClass("d-none");
            return;
        }
        alert_div.removeClass("d-none");
        alert_div.empty();
        if (status == "success") {
            alert_div.addClass("alert-success");
        }
        if (status == "error") {
            alert_div.addClass("alert-danger");
        }
        var list = $("<ul>");
        if (typeof content == "object") {
            for (let message of content) {
                list.append(`<li>${message}</li>`);
            }
            alert_div.append(list);
        } else {
            alert_div.text(content);
        }
    }

    function product_feedbacks_set(status) {
        if (status == "show") {
            $("table th:first").removeClass("d-none");
            $("table tr").find("td:first").removeClass("d-none");
        }
        if (status == "hidden") {
            $("table th:first").addClass("d-none");
            $("table tr").find("td:first").addClass("d-none");
        }
    }

    $("select[name=mfr_id]").on("change", function () {
        var selected_option_index = $(this).prop("selectedIndex") + 1;
        var url = new URL(window.location.href);
        var params = url.searchParams;
        params.set("mfr_page", selected_option_index);
        url.search = params.toString();
        window.location.href = url.toString();
    });

    $("table tr input[type=checkbox]").on("change", () => {
        updateTotalQuantity();
        var checklist_obj = construct_checklist();
        $.ajax({
            type: "POST",
            url: data.updateChecklistUrl,
            data: JSON.stringify(checklist_obj),
            dataTyle: "json",
            contentType: "application/json",
        });
    });

    function construct_checklist() {
        var checklist = [];
        var unchecklist = [];
        $("table tr input[type=checkbox]").each(function () {
            var prod_no = parseInt($(this).parent().parent().attr("data-id"));
            if ($(this).prop("checked")) checklist.push(prod_no);
            else unchecklist.push(prod_no);
        });
        return {
            mfr_full_id: data.manufacturerId,
            checklist: checklist,
            unchecklist: unchecklist,
        };
    }

    $("table tr input[field=order-quantity]").on("change", function () {
        // TODO: when change order box quantity, update order quantity
        var tr = $(this).parent().parent();
        tr.find("input[type=checkbox]").first().prop("checked", true);

        var total_quantity_field = tr
            .find("input[field=total-quantity]")
            .first();
        var prod_quantity_field = tr.find("input[field=prod-quantity]").first();
        var order_cost_price_field = tr
            .find("input[field=order-cost-price]")
            .first();
        var order_box_quantity_field = tr
            .find("input[field=order-box-quantity]")
            .first();
        var outer_quantity_field = parseInt(
            tr.find("input[field=outer-quantity]").first().val()
        );
        var inner_quantity_field = parseInt(
            tr.find("input[field=inner-quantity]").first().val()
        );
        var prod_cost_price_field = parseFloat(
            tr.find("input[field=prod-cost-price]").first().val()
        );

        var prod_quantity = parseInt(prod_quantity_field.val());
        var order_quantity = parseInt($(this).val());

        var cost_price = prod_cost_price_field * order_quantity;
        order_cost_price_field.val(cost_price);

        var box_quantity =
            order_quantity / (outer_quantity_field * inner_quantity_field);
        order_box_quantity_field.val(box_quantity.toFixed(2));

        total_quantity_field.val(order_quantity + prod_quantity);
        updateTotalQuantity();
    });

    function updateTotalQuantity() {
        var sum_of_box_quantity_field = $("input[field=co_order_box_quantity]");
        var sum_of_order_cost_price_field = $(
            "input[field=co_order_cost_price]"
        );
        var target_tr = $("input[field=order-box-quantity]")
            .parent()
            .parent()
            .filter((idx, el) => {
                return (
                    $(el).find("input[type=checkbox]").prop("checked") == true
                );
            });
        var box_quantity_arr = target_tr
            .find("input[field=order-box-quantity]")
            .map(function () {
                return parseFloat($(this).val());
            })
            .get();

        var sum_of_box_quantity =
            box_quantity_arr.length == 0
                ? 0
                : box_quantity_arr.reduce(function (acc, curr) {
                      return acc + curr;
                  });

        var order_cost_price_arr = target_tr
            .find("input[field=order-cost-price]")
            .map(function () {
                return parseFloat($(this).val());
            })
            .get();

        var sum_of_order_cost_price =
            order_cost_price_arr.length == 0
                ? 0
                : order_cost_price_arr.reduce(function (acc, curr) {
                      return acc + curr;
                  });

        sum_of_box_quantity_field.val(sum_of_box_quantity);
        sum_of_order_cost_price_field.val(sum_of_order_cost_price);
    }

    function get_checked_products() {
        return $("table input[type=checkbox]:checked").parent().parent();
    }

    function constructOrder(action) {
        var order_products = [];
        var target_tr = get_checked_products();
        if (target_tr.length == 0) {
            alert_div_set("error", "請選擇至少一個產品！");
            return { action: action, products: order_products };
        }
        target_tr.each(function () {
            var order_quantity = parseInt(
                $(this).find("input[field=order-quantity]").val()
            );
            var product_no = parseInt($(this).attr("data-id"));
            order_products.push({
                prod_no: product_no,
                prod_quantity: order_quantity,
            });
        });
        return { action: action, products: order_products };
    }

    function handle_order_error(err) {
        if (err.status == 400) {
            var errors = err.responseJSON.errors;
            global_errors = [];
            for (let error of errors) {
                if (
                    error.obj_type == "Manufacturer" ||
                    error.obj_type == "ProdCategory"
                ) {
                    global_errors.push(error.message);
                    continue;
                }
                product_feedbacks_set("show");
                var target_tr = $(`tr[data-id=${error.obj}]`);
                var invalid_input = target_tr.find(
                    "input[field=order-quantity]"
                );
                var feedback = target_tr.find("div[field=feedback]");
                feedback.addClass("alert alert-danger");
                if (feedback.children().length > 0) {
                    feedback.children().append(`<li>${error.message}</li>`);
                } else {
                    feedback.append(`<ul><li>${error.message}</li></ul>`);
                }
                invalid_input.removeClass("is-valid").addClass("is-invalid");
            }
            if (errors.length > 0) {
                get_checked_products()
                    .find("input[field=order-quantity]")
                    .first()
                    .trigger("focus");
            }
            if (global_errors.length > 0) {
                alert_div_set("error", global_errors);
            }
        } else {
            alert_div_set("error", "伺服器錯誤，請稍後再試！");
        }
    }

    function reset_feedbacks() {
        $("div[field=feedback]").children().remove();
        alert_div_set("hidden");
        $("input[field=order-quantity]").removeClass("is-invalid");
        $("input[field=order-quantity]").removeClass("is-valid");
        product_feedbacks_set("hidden");
    }

    $("input[field=btn-validation]").on("click", () => {
        var order_obj = constructOrder("validation");
        if (order_obj.products == 0) return;
        $.ajax({
            type: "POST",
            url: data.createOrderUrl,
            data: JSON.stringify(order_obj),
            dataTyle: "json",
            contentType: "application/json",
            beforeSend: function () {
                reset_feedbacks();
                get_checked_products()
                    .find("input[field=order-quantity]")
                    .addClass("is-valid");
            },
            success: function (data) {
                alert_div_set("success", data.message);
            },
            error: function (err) {
                handle_order_error(err);
            },
        });
    });

    $("input[field=btn-place-order]").on("click", () => {
        var order_obj = constructOrder("create");
        $.ajax({
            type: "POST",
            url: data.createOrderUrl,
            data: JSON.stringify(order_obj),
            dataTyle: "json",
            contentType: "application/json",
            beforeSend: function () {
                reset_feedbacks();
            },
            success: function (data) {
                alert_div_set("success", data.message);
            },
            error: function (err) {
                handle_order_error(err);
            },
        });
    });
});
