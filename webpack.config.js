"use strict";
const path = require("path");
const webpack = require("webpack");
const autoprefixer = require("autoprefixer");
const bundletracker = require("webpack-bundle-tracker");

module.exports = {
    mode: "development",
    entry: "./assets/js/index.js",
    output: {
        filename: "[name]-[contenthash].js",
        path: path.resolve(__dirname, "assets", "webpack_bundles"),
        publicPath: "auto",
    },
    devServer: {
        static: path.resolve(__dirname, "demo", "static"),
        port: 8001,
        hot: true,
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
        }),
        new bundletracker({ path: __dirname, filename: "webpack-stats.json" }),
    ],
    module: {
        rules: [
            {
                test: /\.(woff|woff2|eot|ttf|otf)$/i,
                type: "asset/resource",
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.scss$/,
                use: [
                    {
                        loader: "style-loader",
                    },
                    {
                        loader: "css-loader",
                    },
                    {
                        loader: "postcss-loader",
                        options: {
                            postcssOptions: {
                                plugins: [autoprefixer],
                            },
                        },
                    },
                    {
                        loader: "sass-loader",
                    },
                ],
            },
            // {
            //     test: /\.(png|svg|jpg|jpeg|gif)$/i,
            //     type: "asset/resource",
            // },
        ],
    },
};
