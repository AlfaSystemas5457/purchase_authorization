{
    "name": "Autorización de compras",
    "version": "1.0",
    "description": "Agrega un botón para pedir la autorizacion en el modulo de compras.",
    "summary": "Agrega un botón para pedir la autorizacion en el modulo de compras.",
    "author": "DGV",
    "license": "LGPL-3",
    "category": "Purchase",
    "depends": ["purchase", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/purchase_order_views.xml",
        "views/res_partner_view.xml",
        "wizards/reject_wizard.xml",
    ],
    "auto_install": False,
    "application": False,
}
