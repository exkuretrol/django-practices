$(function () {
    $("#ajax-button").on("click", function () {
        $.ajax({
            url: '{% url "ajax_get_category" %}',
            success: (data) => {
                $("#ajax-response").text(data.message);
            },
        });
    });
    let query = $("#query");

    query.on("keyup", (_) => {console.log(_)});

    function search_by_conditions(conditions) {
        $.ajax({
            url: '{% url "ajax_get_prods %}',
            success: () => {},
        });
    }
});
