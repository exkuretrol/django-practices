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
        var total = tr.find("input[field=total-quantity]").first();
        var prod = tr.find("input[field=prod-quantity]").first();

        var prod_quantity = parseInt(prod.val());
        var order_quantity = parseInt($(this).val());
        total.val(order_quantity + prod_quantity);
        tr.find("input[type=checkbox]").first().prop("checked", true);
    });

    $("input[field=btn-place-order]").on("click", function () {
        var trs = $("table input[type=checkbox]:checked").parent().parent();
        console.log(trs);
    });
});
