FROM odoo:19.0

# Version: Fix postgres user security issue
# Définir l'utilisateur root pour l'installation
USER root

# Mettre à jour et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Créer les répertoires nécessaires
RUN mkdir -p /mnt/extra-addons \
    && mkdir -p /var/lib/odoo \
    && mkdir -p /etc/odoo

# Copier le script d'entrée et le fichier de configuration template
COPY ./entrypoint.sh /entrypoint.sh
COPY ./odoo.conf /etc/odoo/odoo.conf.template

# Rendre le script exécutable et donner les permissions appropriées
RUN chmod +x /entrypoint.sh \
    && chown -R odoo:odoo /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo \
    && chown -R odoo:odoo /etc/odoo

# Exposer le port Odoo
EXPOSE 8069

# Définir les variables d'environnement par défaut
ENV ODOO_RC=/etc/odoo/odoo.conf

# Utiliser le script d'entrée
ENTRYPOINT ["/entrypoint.sh"]

# Arguments par défaut (peuvent être overridés)
CMD []
