import { useState } from "react";
import { useParams } from "react-router-dom";
import Icon from "../components/Icon";

function Documents() {
  const { id } = useParams();

  const [documents, setDocuments] = useState([
    {
      name: "PAN Card",
      type: "Identity Proof",
      status: "VERIFIED",
    },
    {
      name: "Salary Slip",
      type: "Income Proof",
      status: "PENDING",
    },
    {
      name: "Address Proof",
      type: "Address",
      status: "VERIFIED",
    },
  ]);

  const updateStatus = (index, status) => {
    setDocuments((items) =>
      items.map((item, itemIndex) =>
        itemIndex === index
          ? { ...item, status }
          : item
      )
    );
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="breadcrumb">
            Application / {id}
          </div>

          <h1>Documents</h1>

          <p>
            Verify documents submitted for this application.
          </p>
        </div>
      </div>

      <section className="card">
        <div className="card-heading">
          <div>
            <h3>Required Documents</h3>
            <p>
              Review and verify each submitted document.
            </p>
          </div>
        </div>

        <div className="documents-table">
          {documents.map((document, index) => (
            <div
              className="document-item"
              key={document.name}
            >
              <div className="document-main">
                <div className="document-icon">
                  <Icon name="file" size={18} />
                </div>

                <div>
                  <strong>{document.name}</strong>
                  <span>{document.type}</span>
                </div>
              </div>

              <span
                className={`document-status ${document.status.toLowerCase()}`}
              >
                {document.status}
              </span>

              <div className="document-actions">
                <button
                  className="small-button success-button"
                  onClick={() =>
                    updateStatus(index, "VERIFIED")
                  }
                >
                  Verify
                </button>

                <button
                  className="small-button danger-button"
                  onClick={() =>
                    updateStatus(index, "REJECTED")
                  }
                >
                  Reject
                </button>

                <button
                  className="small-button neutral-button"
                  onClick={() =>
                    updateStatus(
                      index,
                      "REQUIRES_REUPLOAD"
                    )
                  }
                >
                  Re-upload
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

export default Documents;