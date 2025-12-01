/** @odoo-module **/

/**
 * Gestion de l'authentification par reconnaissance faciale
 */
(function() {
    'use strict';

    // Variables globales
    let stream = null;
    let video = null;
    let canvas = null;
    let isCapturing = false;

    // Éléments DOM
    let btnStartCamera = null;
    let btnIdentify = null;
    let btnRetry = null;
    let statusElement = null;
    let infoMessage = null;
    let errorMessage = null;
    let successMessage = null;

    /**
     * Initialisation au chargement de la page
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Récupérer les éléments DOM
        video = document.getElementById('facial_video');
        canvas = document.getElementById('facial_canvas');
        btnStartCamera = document.getElementById('btn_start_camera');
        btnIdentify = document.getElementById('btn_identify');
        btnRetry = document.getElementById('btn_retry');
        statusElement = document.getElementById('facial_status');
        infoMessage = document.getElementById('facial_info_message');
        errorMessage = document.getElementById('facial_error_message');
        successMessage = document.getElementById('facial_success_message');

        // Vérifier que les éléments existent
        if (!video || !canvas) {
            console.error('Éléments vidéo/canvas non trouvés');
            return;
        }

        // Attacher les événements
        if (btnStartCamera) {
            btnStartCamera.addEventListener('click', startCamera);
        }

        if (btnIdentify) {
            btnIdentify.addEventListener('click', identifyAndLogin);
        }

        if (btnRetry) {
            btnRetry.addEventListener('click', resetCapture);
        }

        // Démarrer automatiquement la caméra après un court délai
        setTimeout(function() {
            if (btnStartCamera && btnStartCamera.style.display !== 'none') {
                startCamera();
            }
        }, 500);
    });

    /**
     * Démarre la caméra
     */
    async function startCamera() {
        try {
            showStatus('Démarrage de la caméra...', 'info');

            // Demander l'accès à la webcam
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            };

            stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
            video.play();

            // Attendre que la vidéo soit prête
            video.addEventListener('loadeddata', function() {
                showStatus('Caméra active - Positionnez votre visage', 'success');

                // Afficher le bouton d'identification
                if (btnStartCamera) btnStartCamera.style.display = 'none';
                if (btnIdentify) btnIdentify.style.display = 'inline-block';

                hideMessages();
            });

        } catch (err) {
            console.error('Erreur d\'accès à la webcam:', err);
            showError('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
            showStatus('Erreur caméra', 'error');
        }
    }

    /**
     * Arrête la caméra
     */
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }

        if (video) {
            video.srcObject = null;
        }
    }

    /**
     * Capture une photo depuis la webcam
     */
    function capturePhoto() {
        if (!video || !canvas) {
            return null;
        }

        // Configurer le canvas avec les dimensions de la vidéo
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Dessiner l'image de la vidéo sur le canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convertir en base64
        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        const base64Data = imageData.split(',')[1];

        return base64Data;
    }

    /**
     * Identifie l'utilisateur et le connecte
     */
    async function identifyAndLogin() {
        if (isCapturing) {
            return;
        }

        try {
            isCapturing = true;
            showStatus('Capture en cours...', 'info');

            // Désactiver le bouton
            if (btnIdentify) {
                btnIdentify.disabled = true;
            }

            // Capturer la photo
            const photoData = capturePhoto();
            if (!photoData) {
                throw new Error('Échec de la capture photo');
            }

            showStatus('Identification en cours...', 'info');

            // Appeler l'API d'authentification
            const response = await fetch('/web/facial_auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        photo_data: photoData
                    },
                    id: new Date().getTime()
                })
            });

            const data = await response.json();
            const result = data.result;

            if (result.success) {
                // Authentification réussie
                const userName = result.user_name;
                const confidence = result.confidence.toFixed(1);

                showSuccess(`Bienvenue ${userName}! (confiance: ${confidence}%)`);
                showStatus('Connexion réussie!', 'success');

                // Arrêter la caméra
                stopCamera();

                // Cacher les boutons
                if (btnIdentify) btnIdentify.style.display = 'none';

                // Rediriger vers l'application
                setTimeout(function() {
                    window.location.href = result.redirect || '/web';
                }, 1500);

            } else {
                // Échec de l'authentification
                showError(result.error || 'Identification échouée. Réessayez.');
                showStatus('Identification échouée', 'error');

                // Afficher le bouton réessayer
                if (btnIdentify) btnIdentify.style.display = 'none';
                if (btnRetry) btnRetry.style.display = 'inline-block';
            }

        } catch (error) {
            console.error('Erreur lors de l\'identification:', error);
            showError('Erreur lors de l\'identification: ' + error.message);
            showStatus('Erreur', 'error');

            // Afficher le bouton réessayer
            if (btnIdentify) btnIdentify.style.display = 'none';
            if (btnRetry) btnRetry.style.display = 'inline-block';

        } finally {
            isCapturing = false;
            if (btnIdentify) {
                btnIdentify.disabled = false;
            }
        }
    }

    /**
     * Réinitialise la capture pour un nouvel essai
     */
    function resetCapture() {
        hideMessages();
        showStatus('Prêt pour une nouvelle capture', 'info');

        if (btnRetry) btnRetry.style.display = 'none';
        if (btnIdentify) btnIdentify.style.display = 'inline-block';
    }

    /**
     * Affiche un message de statut
     */
    function showStatus(message, type) {
        if (!statusElement) return;

        statusElement.innerHTML = message;
        statusElement.className = 'o_facial_status';

        if (type === 'success') {
            statusElement.classList.add('o_facial_status_success');
        } else if (type === 'error') {
            statusElement.classList.add('o_facial_status_error');
        } else {
            statusElement.classList.add('o_facial_status_info');
        }
    }

    /**
     * Affiche un message d'information
     */
    function showInfo(message) {
        hideMessages();
        if (infoMessage) {
            document.getElementById('facial_info_text').textContent = message;
            infoMessage.style.display = 'block';
        }
    }

    /**
     * Affiche un message d'erreur
     */
    function showError(message) {
        hideMessages();
        if (errorMessage) {
            document.getElementById('facial_error_text').textContent = message;
            errorMessage.style.display = 'block';
        }
    }

    /**
     * Affiche un message de succès
     */
    function showSuccess(message) {
        hideMessages();
        if (successMessage) {
            document.getElementById('facial_success_text').textContent = message;
            successMessage.style.display = 'block';
        }
    }

    /**
     * Cache tous les messages
     */
    function hideMessages() {
        if (infoMessage) infoMessage.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';
        if (successMessage) successMessage.style.display = 'none';
    }

    // Nettoyer lors de la fermeture de la page
    window.addEventListener('beforeunload', function() {
        stopCamera();
    });

})();

console.log('EAZYNOVA Facial Authentication loaded');
