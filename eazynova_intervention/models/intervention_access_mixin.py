# -*- coding: utf-8 -*-

from odoo import models


class InterventionAccessMixin(models.AbstractModel):
    """Mixin pour contrôle d'accès interventions par utilisateur"""
    
    _name = 'intervention.access.mixin'
    _description = 'Mixin pour contrôle d\'accès interventions par utilisateur'

    def check_intervention_access(self, operation, section=None):
        """
        Vérifie les droits d'accès de l'utilisateur
        
        Args:
            operation (str): Type d'opération ('read', 'write', 'create', 'unlink')
            section (str, optional): Section spécifique ('rapport', 'photo', 'heure')
        
        Returns:
            bool: True si l'utilisateur a les droits, False sinon
        """
        user = self.env.user
        
        # Droits globaux intervention
        if section is None:
            if operation == 'read' and not user.intervention_access_read:
                return False
            if operation == 'write' and not user.intervention_access_write:
                return False
            if operation == 'create' and not user.intervention_access_create:
                return False
            if operation == 'unlink' and not user.intervention_access_unlink:
                return False
        
        # Droits section rapport
        elif section == 'rapport':
            if operation == 'create' and not user.report_access_create:
                return False
            if operation == 'write' and not user.report_access_write:
                return False
            if operation == 'unlink' and not user.report_access_unlink:
                return False
        
        # Droits section photo
        elif section == 'photo':
            if operation == 'create' and not user.photo_access_create:
                return False
            if operation == 'write' and not user.photo_access_write:
                return False
            if operation == 'unlink' and not user.photo_access_unlink:
                return False
        
        # Droits section heure
        elif section == 'heure':
            if operation == 'create' and not user.hour_access_create:
                return False
            if operation == 'write' and not user.hour_access_write:
                return False
            if operation == 'unlink' and not user.hour_access_unlink:
                return False
        
        return True