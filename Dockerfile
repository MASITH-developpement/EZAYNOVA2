FROM odoo:19.0

# Définir l'utilisateur root pour l'installation
USER root

# Mettre à jour et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Créer les répertoires nécessaires
RUN mkdir -p /mnt/extra-addons \
    && mkdir -p /var/lib/odoo \
    && mkdir -p /etc/odoo

# Copier le fichier de configuration
COPY ./odoo.conf /etc/odoo/odoo.conf

# Donner les permissions appropriées
RUN chown -R odoo:odoo /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo \
    && chown -R odoo:odoo /etc/odoo

# Revenir à l'utilisateur odoo
USER odoo

# Exposer le port Odoo
EXPOSE 8069

# Définir les variables d'environnement par défaut
ENV ODOO_RC=/etc/odoo/odoo.conf

# Commande de démarrage
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
