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

# Installer les dépendances Python requises par les modules eazynova
RUN pip3 install --no-cache-dir \
    numpy \
    pandas \
    xlrd \
    openpyxl \
    python-dateutil

# Copier les modules personnalisés (eazynova*)
COPY ./addons /mnt/extra-addons

# Copier le nouveau script de démarrage
COPY ./start-odoo.sh /start-odoo.sh

# Rendre le script exécutable et donner les permissions
RUN chmod +x /start-odoo.sh \
    && chown -R odoo:odoo /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo \
    && chown -R odoo:odoo /etc/odoo

# Exposer le port Odoo
EXPOSE 8069

# Lancer le script
CMD ["/start-odoo.sh"]
