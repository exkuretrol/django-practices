let prod_cate_cols = [].map
    .call(
        document.querySelectorAll(
            "table[table-name='prod_cate'] tbody tr:first-child td"
        ),
        (el) => el.getAttribute("col")
    )
    .filter((el) => el != null);
let tables = [
    {
        table_name: "prod_mfr",
        cols: ["prod_nums", "mfr_main_nums", "mfr_sub_nums"],
    },
    { table_name: "prod_cate", cols: prod_cate_cols },
];

let prod_cate_data = JSON.parse(
    document.getElementById("prod_cate_data").textContent
);

tables.map((table) => {
    let cols = table.cols;
    cols.map((col, i) => {
        let els = document.querySelectorAll(`td[col='${col}']`);

        const width = 120;
        const height = 20;
        const formatter = d3.format(".1%");
        const total = parseInt(
            d3
                .select(
                    document.querySelector(
                        `table[table-name='${
                            table.table_name
                        }'] tfoot td:nth-child(${i + 2})`
                    )
                )
                .text()
                .trim()
        );
        const x = d3.scaleLinear().domain([0, total]).range([0, width]);

        for (let dom_el of els) {
            let el = d3.select(dom_el);
            let num = parseInt(el.text().trim());
            let svg = d3
                .create("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewbox", [-width / 2, -height / 2, width, height]);
            let g = svg.append("g").attr("fill", "steelblue");
            g.append("rect").attr("width", x(num)).attr("height", height);
            let text = g
                .append("text")
                .text(formatter(num / total))
                .attr("y", height - 3)
                .attr("x", x(num) + 5)
                .attr("fill", "blue");
            svg.on("mouseover", (event, d) => {
                text.transition()
                    .duration("300")
                    .text(num)
                    .style("left", 80 + "px");
            }).on("mouseout", (d, i) => {
                text.transition()
                    .duration("300")
                    .text(formatter(num / total));
            });

            dom_el.innerHTML = "";
            dom_el.appendChild(svg.node());
        }
    });
});
