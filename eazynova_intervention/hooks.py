from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    View = env['ir.ui.view']
    Act = env['ir.actions.act_window']
    Imd = env['ir.model.data']

    calendar_view = View.search([
        ('model', '=', 'intervention.intervention'),
        ('type', '=', 'calendar')
    ], limit=1)

    if not calendar_view:
        arch = (
            '<calendar string="Planning Interventions" '
            'date_start="date_prevue" '
            'date_stop="date_calendar_stop" '
            'date_delay="duree_prevue" '
            'mode="week" '
            'color="technicien_principal_id">'
            '<field name="numero"/>'
            '<field name="type_intervention"/>'
            '<field name="donneur_ordre_id"/>'
            '<field name="client_final_id"/>'
            '<field name="technicien_principal_id"/>'
            '</calendar>'
        )
        calendar_view = View.create({
            'name': 'intervention.intervention.view.calendar',
            'type': 'calendar',
            'model': 'intervention.intervention',
            'arch_db': arch,
            'active': True,
            'priority': 16,
        })
        Imd.create({
            'module': 'eazynova_intervention',
            'name': 'intervention_intervention_view_calendar',
            'model': 'ir.ui.view',
            'res_id': calendar_view.id,
            'noupdate': False,
        })

    try:
        action = env.ref('eazynova_intervention.action_intervention')
        action.write({'view_mode': 'calendar,list,form'})
        if calendar_view:
            action.write({'view_id': calendar_view.id})
    except Exception:
        pass

