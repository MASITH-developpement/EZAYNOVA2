/**
 * Applique dynamiquement les couleurs d'intervention depuis la config Odoo
 */
odoo.define("intervention.color_dynamic", function (require) {
    "use strict"
    var ajax = require("web.ajax")
    var core = require("web.core")

    // Récupère les couleurs depuis les paramètres système Odoo
    Promise.all([
        ajax.jsonRpc("/web/dataset/call_kw", "call", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["intervention.color_primary"],
            kwargs: {},
        }),
        ajax.jsonRpc("/web/dataset/call_kw", "call", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["intervention.color_primary_light"],
            kwargs: {},
        }),
        ajax.jsonRpc("/web/dataset/call_kw", "call", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["intervention.color_primary_dark"],
            kwargs: {},
        }),
        ajax.jsonRpc("/web/dataset/call_kw", "call", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["intervention.color_secondary"],
            kwargs: {},
        }),
        ajax.jsonRpc("/web/dataset/call_kw", "call", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["intervention.color_accent"],
            kwargs: {},
        }),
    ])
        .then(function (colors) {
            var primary = colors[0] || "#0277bd"
            var primaryLight = colors[1] || "#29b6f6"
            var primaryDark = colors[2] || "#01579b"
            var secondary = colors[3] || "#4caf50"
            var accent = colors[4] || "#ff9800"

            // Valider les couleurs (format hexadécimal)
            var hexRegex = /^#[0-9A-Fa-f]{6}$/
            if (!hexRegex.test(primary)) primary = "#0277bd"
            if (!hexRegex.test(primaryLight)) primaryLight = "#29b6f6"
            if (!hexRegex.test(primaryDark)) primaryDark = "#01579b"
            if (!hexRegex.test(secondary)) secondary = "#4caf50"
            if (!hexRegex.test(accent)) accent = "#ff9800"

            // Appliquer les variables CSS
            var root = document.documentElement
            root.style.setProperty("--intervention-primary", primary)
            root.style.setProperty("--intervention-primary-light", primaryLight)
            root.style.setProperty("--intervention-primary-dark", primaryDark)
            root.style.setProperty("--intervention-secondary", secondary)
            root.style.setProperty("--intervention-accent", accent)
            root.style.setProperty("--intervention-success", secondary)
            root.style.setProperty("--intervention-info", primary)

            // Calculer les couleurs de fond avec opacité
            root.style.setProperty("--intervention-bg-light", primary + "08")
            root.style.setProperty("--intervention-bg-medium", primary + "20")
            root.style.setProperty("--intervention-bg-dark", primary + "40")
            root.style.setProperty("--intervention-shadow", primary + "26")

            // Alias pour compatibilité
            root.style.setProperty("--plomberie-primary", primary)
            root.style.setProperty("--plomberie-primary-light", primaryLight)
            root.style.setProperty("--plomberie-primary-dark", primaryDark)
            root.style.setProperty("--plomberie-secondary", secondary)
            root.style.setProperty("--plomberie-success", secondary)
            root.style.setProperty("--plomberie-info", primary)
            root.style.setProperty("--plomberie-bg-light", primary + "08")
            root.style.setProperty("--plomberie-bg-medium", primary + "20")
            root.style.setProperty("--plomberie-bg-dark", primary + "40")
            root.style.setProperty("--plomberie-shadow", primary + "26")

            console.log("🎨 Couleurs Intervention appliquées:", {
                primary: primary,
                primaryLight: primaryLight,
                primaryDark: primaryDark,
                secondary: secondary,
                accent: accent,
            })
        })
        .catch(function (error) {
            console.error(
                "Erreur lors du chargement des couleurs Intervention:",
                error
            )
        })
})
