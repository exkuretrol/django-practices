$(function () {
    $("select[name=mfr_id]").on("change", function () {
        var selected_option_index = $(this).prop("selectedIndex") + 1;
        var url = new URL(window.location.href);
        var params = url.searchParams;
        params.set("page", selected_option_index);
        url.search = params.toString();
        window.location.href = url.toString();
    });
});
