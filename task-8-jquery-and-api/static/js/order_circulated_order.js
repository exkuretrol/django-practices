const data = document.currentScript.dataset;
$(function () {
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
    });

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
        order_box_quantity_field.val(box_quantity);

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

    function constructOrder(action) {
        var order_products = [];
        var target_tr = $("table input[type=checkbox]:checked")
            .parent()
            .parent();
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

    function handle_error(err) {
        var errors = err.responseJSON.errors;
        for (let error of errors) {
            var target_tr = $(`tr[data-id=${error.obj}]`);
            var target_input = target_tr.find("input[field=order-quantity]");
            var feedback = target_input.next();
            if (feedback.length > 0 && feedback.children().length > 0) {
                feedback.children().append(`<li>${error.message}</li>`);
            } else {
                target_input.after(
                    `<div class='invalid-feedback'><ul><li>${error.message}</li></ul></div>`
                );
            }
            target_input.removeClass("is-valid").addClass("is-invalid");
        }
        if (errors.length > 0) {
            $("input[type=checkbox]:checked")
                .parent()
                .parent()
                .find("input[field=order-quantity]")
                .first()
                .trigger("focus");
        }
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
                $("input[field=order-quantity]").removeClass("is-invalid");
                $("input[field=order-quantity]").removeClass("is-valid");
                $(".invalid-feedback").children().remove();
                $("input[type=checkbox]:checked")
                    .parent()
                    .parent()
                    .find("input[field=order-quantity]")
                    .addClass("is-valid");
            },
            success: function (data) {
                var alert_div = $("div[role=alert]");
                alert_div.removeClass("alert-danger");
                alert_div.addClass("alert-success");
                alert_div.text(data.message);
            },
            error: function (err) {
                handle_error(err);
            },
        });
    });

    $("input[field=btn-place-order]").on("click", () => {
        var order_obj = constructOrder("place");
        var alert_div = $("div[role=alert]");
        $.ajax({
            type: "POST",
            url: data.createOrderUrl,
            data: JSON.stringify(order_obj),
            dataTyle: "json",
            contentType: "application/json",
            beforeSend: function () {
                alert_div.removeClass("alert-danger");
                alert_div.removeClass("alert-success");
                alert_div.text("");
            },
            success: function (data) {
                alert_div.addClass("alert-success");
                alert_div.text(data.message);
            },
            error: function (err) {
                handle_error(err);
            },
        });
    });
});
