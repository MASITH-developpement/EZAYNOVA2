/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

// Calculateur de prix
publicWidget.registry.EazynovaPriceCalculator = publicWidget.Widget.extend({
    selector: '#nb_users_calc, #nb_users, #plan_id',
    events: {
        'change #nb_users_calc': '_onNbUsersChange',
        'input #nb_users_calc': '_onNbUsersChange',
        'change #nb_users': '_onFormNbUsersChange',
        'input #nb_users': '_onFormNbUsersChange',
        'change #plan_id': '_onPlanChange',
    },

    start: function () {
        this._updatePrice();
        return this._super.apply(this, arguments);
    },

    _onNbUsersChange: function (ev) {
        this._updatePrice();
    },

    _onFormNbUsersChange: function (ev) {
        this._updateFormPrice();
    },

    _onPlanChange: function (ev) {
        this._updateFormPrice();
    },

    _updatePrice: function () {
        const nbUsers = parseInt($('#nb_users_calc').val()) || 5;
        const basePrice = 250;
        const includedUsers = 5;
        const extraUserPrice = 20;
        const setupFee = 1800;

        const extraUsers = Math.max(0, nbUsers - includedUsers);
        const extraPrice = extraUsers * extraUserPrice;
        const totalMonthly = basePrice + extraPrice;

        // Mise à jour de l'affichage
        $('#calculated_price .display-4').text(totalMonthly + ' €');
        $('#price_details').html(`
            <p class="mb-1">Prix de base (${includedUsers} utilisateurs) : ${basePrice} €/mois</p>
            <p class="mb-1">Utilisateurs supplémentaires : ${extraUsers} × ${extraUserPrice} € = ${extraPrice} €/mois</p>
            <p class="mb-1 fw-bold">Total mensuel : ${totalMonthly} €/mois HT</p>
            <p class="mb-0 text-warning">+ Configuration : ${setupFee} € HT (une fois)</p>
        `);
    },

    _updateFormPrice: function () {
        const planSelect = $('#plan_id');
        const nbUsersInput = $('#nb_users');

        if (!planSelect.length || !nbUsersInput.length) return;

        const selectedOption = planSelect.find('option:selected');
        const basePrice = parseFloat(selectedOption.data('monthly-price')) || 250;
        const includedUsers = parseInt(selectedOption.data('included-users')) || 5;
        const extraUserPrice = parseFloat(selectedOption.data('extra-user-price')) || 20;
        const setupFee = parseFloat(selectedOption.data('setup-fee')) || 1800;
        const nbUsers = parseInt(nbUsersInput.val()) || 5;

        const extraUsers = Math.max(0, nbUsers - includedUsers);
        const extraPrice = extraUsers * extraUserPrice;
        const totalMonthly = basePrice + extraPrice;

        // Mise à jour du récapitulatif
        $('#base_price').text(basePrice.toFixed(0) + ' €');
        $('#extra_users_count').text(extraUsers);
        $('#extra_price').text(extraPrice.toFixed(0) + ' €');
        $('#total_monthly').text(totalMonthly.toFixed(0) + ' €');
        $('#setup_fee').text(setupFee.toFixed(0) + ' €');

        // Afficher/masquer la ligne des utilisateurs supplémentaires
        if (extraUsers > 0) {
            $('#extra_users_line').show();
        } else {
            $('#extra_users_line').hide();
        }
    },
});

// Validation du formulaire d'inscription
publicWidget.registry.EazynovaSignupForm = publicWidget.Widget.extend({
    selector: 'form[action="/saas/signup/submit"]',
    events: {
        'submit': '_onSubmit',
    },

    _onSubmit: function (ev) {
        const form = ev.currentTarget;

        if (!form.checkValidity()) {
            ev.preventDefault();
            ev.stopPropagation();
            form.classList.add('was-validated');
            return false;
        }

        // Vérifier les conditions
        const termsCheckbox = form.querySelector('#terms');
        if (termsCheckbox && !termsCheckbox.checked) {
            ev.preventDefault();
            alert('Veuillez accepter les conditions générales d\'utilisation.');
            return false;
        }

        // Afficher un loader
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Création en cours...';
        }

        return true;
    },
});

// Animation au scroll
publicWidget.registry.EazynovaScrollAnimation = publicWidget.Widget.extend({
    selector: '.card, .feature-icon',

    start: function () {
        this._animateOnScroll();
        $(window).on('scroll', this._animateOnScroll.bind(this));
        return this._super.apply(this, arguments);
    },

    _animateOnScroll: function () {
        const windowHeight = $(window).height();
        const scrollTop = $(window).scrollTop();

        this.$el.each(function () {
            const elementTop = $(this).offset().top;
            if (elementTop < scrollTop + windowHeight - 100) {
                $(this).addClass('fade-in');
            }
        });
    },
});

export default {
    EazynovaPriceCalculator: publicWidget.registry.EazynovaPriceCalculator,
    EazynovaSignupForm: publicWidget.registry.EazynovaSignupForm,
    EazynovaScrollAnimation: publicWidget.registry.EazynovaScrollAnimation,
};
