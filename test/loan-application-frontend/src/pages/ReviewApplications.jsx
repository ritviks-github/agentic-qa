import { useState } from "react";
import StatusBadge from "../components/StatusBadge";
import { initialApplications } from "../data/loanData";

function ReviewApplications() {
  const [applications, setApplications] =
    useState(initialApplications);

  const updateStatus = (id, status) => {
    setApplications((items) =>
      items.map((item) =>
        item.id === id
          ? { ...item, status }
          : item
      )
    );
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Review Applications</h1>
          <p>
            Review submitted applications and make
            approval decisions.
          </p>
        </div>
      </div>

      <section className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Application</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Eligibility</th>
                <th>Status</th>
                <th>Decision</th>
              </tr>
            </thead>

            <tbody>
              {applications.map((application) => (
                <tr key={application.id}>
                  <td>
                    <strong>{application.id}</strong>
                  </td>

                  <td>{application.name}</td>

                  <td>
                    ₹
                    {application.loanAmount.toLocaleString(
                      "en-IN"
                    )}
                  </td>

                  <td>{application.eligibility}</td>

                  <td>
                    <StatusBadge
                      status={application.status}
                    />
                  </td>

                  <td>
                    <div className="decision-buttons">
                      <button
                        className="small-button success-button"
                        onClick={() =>
                          updateStatus(
                            application.id,
                            "APPROVED"
                          )
                        }
                      >
                        Approve
                      </button>

                      <button
                        className="small-button danger-button"
                        onClick={() =>
                          updateStatus(
                            application.id,
                            "REJECTED"
                          )
                        }
                      >
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export default ReviewApplications;