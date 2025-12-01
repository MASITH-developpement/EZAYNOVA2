/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Composant OWL pour la capture faciale via webcam
 */
export class FacialCaptureWidget extends Component {
    static template = "eazynova.FacialCaptureWidget";
    static props = {
        onCapture: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({
            streaming: false,
            hasPhoto: false,
            error: null,
        });

        this.videoRef = useRef("video");
        this.canvasRef = useRef("canvas");
        this.stream = null;

        onWillUnmount(() => {
            this.stopCamera();
        });
    }

    /**
     * Démarre la caméra
     */
    async startCamera() {
        try {
            // Demander l'accès à la webcam
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: "user",
                },
                audio: false,
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);

            const video = this.videoRef.el;
            if (video) {
                video.srcObject = this.stream;
                video.play();

                this.state.streaming = true;
                this.state.error = null;
            }
        } catch (err) {
            console.error("Erreur d'accès à la webcam:", err);
            this.state.error = "Impossible d'accéder à la caméra. Vérifiez les permissions.";
        }
    }

    /**
     * Arrête la caméra
     */
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach((track) => track.stop());
            this.stream = null;
        }

        const video = this.videoRef.el;
        if (video) {
            video.srcObject = null;
        }

        this.state.streaming = false;
    }

    /**
     * Capture une photo depuis la webcam
     */
    capturePhoto() {
        const video = this.videoRef.el;
        const canvas = this.canvasRef.el;

        if (!video || !canvas) {
            return;
        }

        const context = canvas.getContext("2d");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Dessiner l'image du video sur le canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convertir en base64
        const imageData = canvas.toDataURL("image/jpeg", 0.9);
        const base64Data = imageData.split(",")[1];

        this.state.hasPhoto = true;

        // Appeler le callback avec les données de l'image
        if (this.props.onCapture) {
            this.props.onCapture(base64Data);
        }

        // Arrêter la caméra après la capture
        this.stopCamera();

        return base64Data;
    }

    /**
     * Réinitialise pour une nouvelle capture
     */
    resetCapture() {
        this.state.hasPhoto = false;
        const canvas = this.canvasRef.el;
        if (canvas) {
            const context = canvas.getContext("2d");
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
    }
}

/**
 * Service de reconnaissance faciale
 */
export class FacialRecognitionService {
    constructor(env, services) {
        this.env = env;
        this.orm = services.orm;
        this.notification = services.notification;
    }

    /**
     * Enregistre un visage
     */
    async registerFace(userId, photoData) {
        try {
            const result = await this.orm.call(
                "eazynova.facial.service",
                "register_face",
                [photoData, userId]
            );

            if (result.success) {
                this.notification.add("Enregistrement facial réussi !", {
                    type: "success",
                });
            } else {
                this.notification.add(result.error || "Erreur lors de l'enregistrement", {
                    type: "danger",
                });
            }

            return result;
        } catch (error) {
            console.error("Erreur lors de l'enregistrement facial:", error);
            this.notification.add("Erreur lors de l'enregistrement facial", {
                type: "danger",
            });
            throw error;
        }
    }

    /**
     * Vérifie un visage
     */
    async verifyFace(photoData, storedEncoding, tolerance = 0.6) {
        try {
            const result = await this.orm.call(
                "eazynova.facial.service",
                "verify_face",
                [photoData, storedEncoding, tolerance]
            );

            return result;
        } catch (error) {
            console.error("Erreur lors de la vérification faciale:", error);
            this.notification.add("Erreur lors de la vérification faciale", {
                type: "danger",
            });
            throw error;
        }
    }

    /**
     * Identifie un utilisateur à partir d'une photo
     */
    async identifyUser(photoData, tolerance = 0.6) {
        try {
            const result = await this.orm.call(
                "eazynova.facial.service",
                "identify_user",
                [photoData, tolerance]
            );

            if (result.success && result.user_id) {
                this.notification.add(
                    `Utilisateur identifié: ${result.user_name} (${result.confidence.toFixed(1)}%)`,
                    { type: "success" }
                );
            } else {
                this.notification.add("Aucun utilisateur correspondant trouvé", {
                    type: "warning",
                });
            }

            return result;
        } catch (error) {
            console.error("Erreur lors de l'identification faciale:", error);
            this.notification.add("Erreur lors de l'identification faciale", {
                type: "danger",
            });
            throw error;
        }
    }

    /**
     * Vérifie la disponibilité des bibliothèques
     */
    async checkLibraryAvailability() {
        try {
            const result = await this.orm.call(
                "eazynova.facial.service",
                "check_library_availability",
                []
            );

            return result;
        } catch (error) {
            console.error("Erreur lors de la vérification des bibliothèques:", error);
            return { available: false, error: error.message };
        }
    }
}

// Enregistrer le service
export const facialRecognitionService = {
    dependencies: ["orm", "notification"],
    start(env, services) {
        return new FacialRecognitionService(env, services);
    },
};

registry.category("services").add("facialRecognition", facialRecognitionService);

console.log("EAZYNOVA Facial Recognition loaded");
