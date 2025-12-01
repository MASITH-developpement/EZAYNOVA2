from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Ensure actions exist
    Act = env['ir.actions.act_window']
    Imd = env['ir.model.data']

    def ensure_action(xmlid, vals):
        try:
            Imd.get_object_reference('eazynova_trust', xmlid)
            return
        except Exception:
            pass
        act = Act.create(vals)
        Imd.create({
            'module': 'eazynova_trust',
            'name': xmlid,
            'model': 'ir.actions.act_window',
            'res_id': act.id,
            'noupdate': False,
        })

    ensure_action('action_review_request', {
        'name': "Demandes d'Avis",
        'res_model': 'eazynova.review.request',
        'view_mode': 'tree,form',
    })

    ensure_action('action_customer_review', {
        'name': 'Avis Clients',
        'res_model': 'eazynova.customer.review',
        'view_mode': 'tree,form',
    })

    # Trust config action
    ensure_action('action_trust_config', {
        'name': 'Configuration Avis Clients',
        'res_model': 'eazynova.trust.config',
        'view_mode': 'form',
    })

