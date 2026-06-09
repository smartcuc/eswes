/*
#
*/

import Modal from "../components/Modal";

export default function Impressum({ onClose }) {
    return (
        <Modal title="Impressum" onClose={onClose}>


            <p className="mb-4">
                smartEvo UG<br />
                Zeisigweg 17<br />
                50389 Wesseling<br />
                Deutschland
            </p>

            <p className="mb-4">
                Geschäftsführer: Rüdiger Könen
            </p>

            <p className="mb-4">
                E-Mail: info@smartevo.de
            </p>

            <p className="mb-4">
                Website: www.smartevo.de
            </p>

        </Modal>
    );
}
