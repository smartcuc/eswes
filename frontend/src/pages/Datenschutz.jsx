/*
# src/pages/Datenschutz.jsx
*/

import Modal from "../components/Modal";

export default function Datenschutz({ onClose }) {
    return (
        <Modal title="Datenschutz" onClose={onClose}>

            <h1 className="text-2xl font-semibold mb-6">
                Datenschutzerklärung
            </h1>

            <p className="mb-4">
                Diese Anwendung verarbeitet Daten zur Darstellung von Energieflüssen.
            </p>

            <p className="mb-4">
                Personenbezogene Daten werden nur im notwendigen Umfang verarbeitet.
            </p>

            <p className="mb-4">
                Verantwortlich: smartEvo UG
            </p>


        </Modal>

    );
}