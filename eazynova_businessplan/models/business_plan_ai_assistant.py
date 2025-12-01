# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json


class BusinessPlanAIAssistant(models.Model):
    _name = 'business.plan.ai.assistant'
    _description = 'Assistant IA pour Business Plan'
    _order = 'create_date desc'

    business_plan_id = fields.Many2one('business.plan', string='Business Plan', required=True, ondelete='cascade')
    analysis_type = fields.Selection([
        ('global', 'Analyse globale'),
        ('financial', 'Analyse financière'),
        ('market', 'Analyse de marché'),
        ('strategy', 'Analyse stratégie'),
        ('coherence', 'Vérification cohérence'),
        ('suggestions', 'Suggestions d\'amélioration'),
    ], string='Type d\'analyse', required=True)

    result = fields.Text(string='Résultat de l\'analyse')
    suggestions = fields.Text(string='Suggestions')
    issues = fields.Text(string='Problèmes détectés')
    score = fields.Integer(string='Score qualité (/100)', compute='_compute_score', store=True)

    @api.depends('result', 'suggestions', 'issues')
    def _compute_score(self):
        for assistant in self:
            # Score basique basé sur la complétude
            plan = assistant.business_plan_id
            score = 0

            # Section résumé (10 points)
            if plan.executive_summary:
                score += 10

            # Section projet (10 points)
            if plan.project_description:
                score += 10

            # Produits/services (10 points)
            if plan.products_services and plan.value_proposition:
                score += 10

            # Marché (15 points)
            if plan.target_market:
                score += 5
            if plan.competitors:
                score += 5
            if plan.competitive_advantage:
                score += 5

            # Stratégie (15 points)
            if plan.marketing_strategy:
                score += 5
            if plan.sales_strategy:
                score += 5
            if plan.customer_acquisition:
                score += 5

            # Équipe (10 points)
            if plan.team_structure:
                score += 10

            # Finances (20 points)
            if plan.revenue_year1 and plan.costs_year1:
                score += 10
            if plan.revenue_year2 or plan.revenue_year3:
                score += 5
            if plan.initial_investment and plan.own_contribution:
                score += 5

            # Risques (10 points)
            if plan.risks and plan.mitigation_plan:
                score += 10

            assistant.score = score

    def analyze_business_plan(self):
        """Analyse complète du business plan"""
        self.ensure_one()
        plan = self.business_plan_id

        analysis = []
        suggestions_list = []
        issues_list = []

        # 1. ANALYSE DE COMPLÉTUDE
        analysis.append("=== ANALYSE DE COMPLÉTUDE ===\n")

        missing_sections = []
        if not plan.executive_summary:
            missing_sections.append("- Résumé exécutif")
        if not plan.project_description:
            missing_sections.append("- Description du projet")
        if not plan.products_services:
            missing_sections.append("- Produits et services")
        if not plan.target_market:
            missing_sections.append("- Marché cible")
        if not plan.marketing_strategy:
            missing_sections.append("- Stratégie marketing")
        if not plan.team_structure:
            missing_sections.append("- Structure de l'équipe")
        if not plan.revenue_year1:
            missing_sections.append("- Prévisions financières")

        if missing_sections:
            issues_list.append("SECTIONS MANQUANTES:\n" + "\n".join(missing_sections))
            analysis.append("⚠️ {} section(s) à compléter\n".format(len(missing_sections)))
        else:
            analysis.append("✅ Toutes les sections principales sont remplies\n")

        # 2. ANALYSE FINANCIÈRE
        analysis.append("\n=== ANALYSE FINANCIÈRE ===\n")

        if plan.revenue_year1 and plan.costs_year1:
            margin_year1 = ((plan.profit_year1 / plan.revenue_year1) * 100) if plan.revenue_year1 else 0
            analysis.append(f"Marge Année 1: {margin_year1:.1f}%\n")

            if margin_year1 < 0:
                issues_list.append("⚠️ PERTE prévue en Année 1")
                suggestions_list.append("Revoir vos charges ou augmenter vos prix pour atteindre la rentabilité")
            elif margin_year1 < 10:
                suggestions_list.append("Marge faible (< 10%). Cherchez des moyens d'optimiser vos coûts")
            else:
                analysis.append("✅ Marge saine\n")

            # Vérifier la cohérence des prévisions
            if plan.revenue_year2:
                growth_rate = ((plan.revenue_year2 - plan.revenue_year1) / plan.revenue_year1 * 100)
                analysis.append(f"Croissance Année 1→2: {growth_rate:.1f}%\n")

                if growth_rate > 100:
                    issues_list.append("⚠️ Croissance >100% entre année 1 et 2 - Soyez réaliste!")
                elif growth_rate < 0:
                    issues_list.append("⚠️ Baisse de CA prévue - Justifiez cette prévision")
        else:
            issues_list.append("Prévisions financières manquantes")

        # 3. COHÉRENCE FINANCEMENT
        if plan.initial_investment and plan.own_contribution:
            if plan.funding_needed > 0:
                analysis.append(f"\n💰 Besoin de financement: {plan.funding_needed:,.0f} {plan.currency_id.symbol}\n")
                if not plan.funding_sources:
                    issues_list.append("Besoin de financement détecté mais sources non précisées")
                    suggestions_list.append("Détaillez vos sources de financement (prêt, aides, investisseurs...)")
            else:
                analysis.append("✅ Projet autofinancé\n")

        # 4. ANALYSE DE MARCHÉ
        analysis.append("\n=== ANALYSE STRATÉGIQUE ===\n")

        if plan.target_market and len(plan.target_market) < 100:
            suggestions_list.append("Développez davantage votre analyse de marché (taille, tendances, segmentation)")

        if plan.competitors and len(plan.competitors) < 50:
            suggestions_list.append("Analysez plus en détail vos concurrents (au moins 3-4 concurrents)")

        if not plan.competitive_advantage:
            issues_list.append("Avantage concurrentiel non défini - CRITIQUE!")
            suggestions_list.append("Identifiez clairement ce qui vous différencie de la concurrence")

        # 5. COHÉRENCE GLOBALE
        analysis.append("\n=== COHÉRENCE GLOBALE ===\n")

        # Vérifier que l'équipe est cohérente avec l'activité
        if plan.team_size == 1 and plan.revenue_year1 > 500000:
            suggestions_list.append("CA élevé pour une personne seule - Prévoyez des recrutements")

        # Vérifier que les dates sont cohérentes
        if plan.date_start and plan.date_end:
            duration_days = (plan.date_end - plan.date_start).days
            if duration_days > 1095:  # 3 ans
                suggestions_list.append("Période très longue (>3 ans) - Précisez des jalons intermédiaires")

        # 6. RECOMMANDATIONS GÉNÉRALES
        analysis.append("\n=== RECOMMANDATIONS ===\n")

        if self.score < 50:
            suggestions_list.append("⚠️ Business plan incomplet. Complétez toutes les sections avant validation")
        elif self.score < 70:
            suggestions_list.append("Business plan correct mais améliorable. Développez les sections faibles")
        elif self.score < 90:
            suggestions_list.append("Bon business plan. Quelques détails à affiner")
        else:
            analysis.append("✅ Excellent business plan, très complet!\n")

        # Mise à jour des résultats
        self.result = "".join(analysis)
        self.suggestions = "\n\n".join(suggestions_list) if suggestions_list else "Aucune suggestion - Bon travail!"
        self.issues = "\n\n".join(issues_list) if issues_list else "Aucun problème détecté"

        return {
            'score': self.score,
            'result': self.result,
            'suggestions': self.suggestions,
            'issues': self.issues,
        }

    def suggest_improvements_for_section(self, section):
        """Suggère des améliorations pour une section spécifique"""
        self.ensure_one()
        plan = self.business_plan_id

        suggestions = {
            'executive_summary': """
CONSEILS POUR LE RÉSUMÉ EXÉCUTIF:
- Commencez par votre objectif principal
- Présentez votre marché en 1-2 phrases
- Indiquez votre avantage concurrentiel unique
- Donnez vos principaux chiffres (CA cible, investissement)
- Terminez par votre vision à 3 ans
- Restez concis: 150-200 mots maximum

EXEMPLE:
"Notre entreprise vise à créer la première plateforme de livraison de repas bio à Lyon.
Le marché du bio croît de 15%/an avec une clientèle urbaine CSP+ prête à payer pour la qualité.
Notre différence: partenariats exclusifs avec 20 producteurs locaux dans un rayon de 30km.
Objectif: 500k€ de CA la première année avec 80k€ d'investissement initial.
Vision: Devenir la référence locale et s'étendre à 3 villes en 3 ans."
            """,

            'market': """
CONSEILS POUR L'ANALYSE DE MARCHÉ:
1. MARCHÉ CIBLE:
   - Qui sont vos clients ? (âge, CSP, localisation, comportements)
   - Combien sont-ils ? (taille du marché)
   - Le marché croît-il ? (tendances, % de croissance)
   - Segmentez votre marché (B2B/B2C, segments)

2. CONCURRENCE:
   - Listez 3-5 concurrents directs
   - Pour chacun: forces, faiblesses, positionnement, prix
   - Identifiez les leaders du marché
   - Parts de marché si disponibles

3. VOTRE POSITIONNEMENT:
   - Qu'est-ce qui vous rend unique ?
   - Pourquoi les clients vous choisiront ?
   - Quelle est votre niche ?
            """,

            'financial': """
CONSEILS POUR LES PRÉVISIONS FINANCIÈRES:
1. REVENUS:
   - Soyez RÉALISTE (plutôt pessimiste qu'optimiste)
   - Basez-vous sur: prix × volume prévu
   - Année 1: démarrage progressif
   - Année 2: croissance 20-50%
   - Année 3: croissance 10-30%

2. CHARGES:
   - Listez TOUTES les charges (fixes et variables)
   - Charges fixes: loyer, salaires, assurances...
   - Charges variables: matières, sous-traitance...
   - Prévoyez une marge de sécurité (+10-15%)

3. COHÉRENCE:
   - Marge nette minimum: 5-10%
   - Vérifiez: prix de vente > coût de revient
   - Point mort à atteindre en 12-18 mois
            """,

            'strategy': """
CONSEILS POUR LA STRATÉGIE COMMERCIALE:
1. MARKETING:
   - Canaux: digital (SEO, réseaux sociaux, pub online) + physique (flyers, affichage...)
   - Budget: 5-10% du CA prévu
   - Actions concrètes: planning des 6 premiers mois
   - Mesure: KPIs à suivre

2. VENTE:
   - Circuit de distribution (direct, partenaires, e-commerce...)
   - Politique de prix (premium, compétitif, low-cost)
   - Arguments de vente principaux
   - Process de vente (du prospect au client)

3. ACQUISITION:
   - Offre de lancement
   - Programme de parrainage
   - Partenariats stratégiques
   - Objectif: X clients les 3 premiers mois
            """,
        }

        return suggestions.get(section, "Section non reconnue")

    def check_financial_coherence(self):
        """Vérifie la cohérence des données financières"""
        self.ensure_one()
        plan = self.business_plan_id

        checks = []

        # Vérification 1: Marges
        if plan.revenue_year1 and plan.costs_year1:
            if plan.profit_year1 < 0:
                checks.append("❌ Perte en année 1 - Ajustez vos prévisions")
            else:
                margin_pct = (plan.profit_year1 / plan.revenue_year1) * 100
                if margin_pct < 5:
                    checks.append(f"⚠️ Marge faible ({margin_pct:.1f}%) - Optimisez vos coûts")
                else:
                    checks.append(f"✅ Marge correcte ({margin_pct:.1f}%)")

        # Vérification 2: Croissance cohérente
        if plan.revenue_year1 and plan.revenue_year2:
            growth = ((plan.revenue_year2 - plan.revenue_year1) / plan.revenue_year1) * 100
            if growth > 200:
                checks.append(f"⚠️ Croissance irréaliste année 1→2 ({growth:.0f}%)")
            elif growth < 0:
                checks.append(f"⚠️ Baisse de CA prévue ({growth:.0f}%) - Justifiez")
            else:
                checks.append(f"✅ Croissance cohérente année 1→2 ({growth:.0f}%)")

        # Vérification 3: Financement
        if plan.initial_investment:
            if plan.own_contribution == 0:
                checks.append("⚠️ Aucun apport personnel - Difficile d'obtenir un financement")
            elif plan.own_contribution < (plan.initial_investment * 0.2):
                checks.append("⚠️ Apport personnel < 20% - Augmentez votre apport si possible")
            else:
                pct = (plan.own_contribution / plan.initial_investment) * 100
                checks.append(f"✅ Apport personnel correct ({pct:.0f}%)")

        # Vérification 4: Ratio investissement/CA
        if plan.initial_investment and plan.revenue_year1:
            ratio = plan.initial_investment / plan.revenue_year1
            if ratio > 2:
                checks.append(f"⚠️ Investissement très élevé par rapport au CA (×{ratio:.1f})")

        return "\n".join(checks)

    def generate_smart_suggestions(self):
        """Génère des suggestions intelligentes basées sur l'analyse"""
        self.ensure_one()
        plan = self.business_plan_id

        suggestions = []

        # Suggestions basées sur le secteur (à améliorer avec vraie IA)
        if plan.legal_form == 'individual':
            suggestions.append("💡 En entreprise individuelle, pensez à l'EIRL pour protéger votre patrimoine")

        # Suggestions financières
        if plan.revenue_year1:
            if plan.revenue_year1 < 50000:
                suggestions.append("💡 Avec ce CA, pensez au régime micro-entreprise pour simplifier la gestion")
            elif plan.revenue_year1 > 500000:
                suggestions.append("💡 CA important: pensez à recruter dès l'année 2 pour soutenir la croissance")

        # Suggestions d'équipe
        if plan.team_size == 1 and plan.revenue_year1 > 200000:
            suggestions.append("💡 Seul avec ce CA: prévoyez un plan de recrutement ou de sous-traitance")

        # Suggestions marketing
        if not plan.marketing_strategy:
            suggestions.append("💡 Une stratégie marketing solide est cruciale - Ne négligez pas cette section!")

        # Suggestions de financement
        if plan.funding_needed > 50000 and not plan.funding_sources:
            suggestions.append("💡 Pour >50k€, explorez: prêt bancaire, BPI France, business angels, crowdfunding")

        return "\n\n".join(suggestions)
