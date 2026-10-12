import { Link, useParams } from "react-router-dom";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { initialApplications } from "../data/loanData";

function ApplicationDetails() {
  const { id } = useParams();

  const application =
    initialApplications.find(
      (item) => item.id === id
    ) || initialApplications[0];

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="breadcrumb">
            Applications / {application.id}
          </div>

          <h1>{application.id}</h1>

          <p>
            Application details and processing information.
          </p>
        </div>

        <StatusBadge status={application.status} />
      </div>

      <div className="details-grid">
        <section className="card">
          <h3 className="card-title">
            Customer Information
          </h3>

          <div className="details-list">
            <div>
              <span>Full Name</span>
              <strong>{application.name}</strong>
            </div>

            <div>
              <span>Email</span>
              <strong>{application.email}</strong>
            </div>

            <div>
              <span>Mobile</span>
              <strong>{application.phone}</strong>
            </div>

            <div>
              <span>Date of Birth</span>
              <strong>{application.dob}</strong>
            </div>

            <div>
              <span>PAN</span>
              <strong>{application.pan}</strong>
            </div>
          </div>
        </section>

        <section className="card">
          <h3 className="card-title">
            Loan Information
          </h3>

          <div className="details-list">
            <div>
              <span>Loan Type</span>
              <strong>{application.loanType}</strong>
            </div>

            <div>
              <span>Requested Amount</span>
              <strong>
                ₹
                {application.loanAmount.toLocaleString(
                  "en-IN"
                )}
              </strong>
            </div>

            <div>
              <span>Tenure</span>
              <strong>{application.tenure} months</strong>
            </div>

            <div>
              <span>Eligibility</span>
              <strong className="success-text">
                {application.eligibility}
              </strong>
            </div>

            <div>
              <span>Created</span>
              <strong>{application.createdAt}</strong>
            </div>
          </div>
        </section>

        <section className="card">
          <h3 className="card-title">
            Financial Information
          </h3>

          <div className="details-list">
            <div>
              <span>Employment</span>
              <strong>{application.employment}</strong>
            </div>

            <div>
              <span>Monthly Income</span>
              <strong>
                ₹
                {application.monthlyIncome.toLocaleString(
                  "en-IN"
                )}
              </strong>
            </div>

            <div>
              <span>Existing EMI</span>
              <strong>
                ₹
                {application.existingEmi.toLocaleString(
                  "en-IN"
                )}
              </strong>
            </div>

            <div>
              <span>Available Income</span>
              <strong>
                ₹
                {(
                  application.monthlyIncome -
                  application.existingEmi
                ).toLocaleString("en-IN")}
              </strong>
            </div>
          </div>
        </section>

        <section className="card">
          <h3 className="card-title">
            Application Actions
          </h3>

          <div className="action-list">
            <Link
              to={`/applications/${application.id}/documents`}
              className="action-card"
            >
              <div className="action-icon">
                <Icon name="file" size={17} />
              </div>

              <div>
                <strong>Documents</strong>
                <span>
                  View and verify documents
                </span>
              </div>

              <Icon name="chevronRight" size={16} />
            </Link>

            <Link
              to={`/applications/${application.id}/eligibility`}
              className="action-card"
            >
              <div className="action-icon">
                <Icon name="calculator" size={17} />
              </div>

              <div>
                <strong>Eligibility</strong>
                <span>
                  View eligibility assessment
                </span>
              </div>

              <Icon name="chevronRight" size={16} />
            </Link>
          </div>
        </section>
      </div>
    </>
  );
}

export default ApplicationDetails;