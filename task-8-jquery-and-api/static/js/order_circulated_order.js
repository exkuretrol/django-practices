$(function () {
    $("select[name=mfr_id]").on("change", function () {
        var selected_option_index = $(this).prop("selectedIndex") + 1;
        var url = new URL(window.location.href);
        var params = url.searchParams;
        params.set("mfr_page", selected_option_index);
        url.search = params.toString();
        window.location.href = url.toString();
    });

    $("table tr input[field=order-quantity]").on("change", function () {
        var tr = $(this).parent().parent();
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

        var sum_of_box_quantity_field = $("input[field=co_order_box_quantity]");
        var sum_of_order_cost_price_field = $(
            "input[field=co_order_cost_price]"
        );

        var sum_of_box_quantity = $("input[field=order-box-quantity]")
            .map(function () {
                return parseFloat($(this).val());
            })
            .get()
            .reduce(function (acc, curr) {
                return acc + curr;
            });
        var sum_of_order_cost_price = $("input[field=order-cost-price]")
            .map(function () {
                return parseFloat($(this).val());
            })
            .get()
            .reduce(function (acc, curr) {
                return acc + curr;
            });

        sum_of_box_quantity_field.val(sum_of_box_quantity);
        sum_of_order_cost_price_field.val(sum_of_order_cost_price);

        tr.find("input[type=checkbox]").first().prop("checked", true);
    });

    $("input[field=btn-place-order]").on("click", function () {
        var trs = $("table input[type=checkbox]:checked").parent().parent();
        console.log(trs);
    });
});
