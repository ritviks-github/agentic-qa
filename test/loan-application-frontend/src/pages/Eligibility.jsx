import { useParams } from "react-router-dom";
import Icon from "../components/Icon";
import { initialApplications } from "../data/loanData";

function Eligibility() {
  const { id } = useParams();

  const application =
    initialApplications.find(
      (item) => item.id === id
    ) || initialApplications[0];

  const availableIncome =
    application.monthlyIncome -
    application.existingEmi;

  const eligibleAmount = Math.max(
    0,
    availableIncome * 40
  );

  const eligible =
    application.loanAmount <= eligibleAmount;

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="breadcrumb">
            Application / {id}
          </div>

          <h1>Eligibility Assessment</h1>

          <p>
            Automated assessment of the customer's
            loan eligibility.
          </p>
        </div>
      </div>

      <section className="eligibility-card">
        <div
          className={`eligibility-icon ${
            eligible ? "success" : "danger"
          }`}
        >
          <Icon
            name={eligible ? "checkCircle" : "xCircle"}
            size={28}
          />
        </div>

        <div>
          <span>Eligibility Decision</span>

          <h2 className={eligible ? "success-text" : "danger-text"}>
            {eligible ? "ELIGIBLE" : "NOT ELIGIBLE"}
          </h2>

          <p>
            {eligible
              ? "The requested loan amount is within the customer's estimated eligibility."
              : "The requested loan amount exceeds the customer's estimated eligibility."}
          </p>
        </div>
      </section>

      <div className="stats-grid eligibility-stats">
        <div className="stat-card">
          <div>
            <span className="stat-label">
              Monthly Income
            </span>

            <strong className="stat-value">
              ₹
              {application.monthlyIncome.toLocaleString(
                "en-IN"
              )}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div>
            <span className="stat-label">
              Existing EMI
            </span>

            <strong className="stat-value">
              ₹
              {application.existingEmi.toLocaleString(
                "en-IN"
              )}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div>
            <span className="stat-label">
              Available Income
            </span>

            <strong className="stat-value">
              ₹{availableIncome.toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div>
            <span className="stat-label">
              Estimated Eligible Amount
            </span>

            <strong className="stat-value">
              ₹{eligibleAmount.toLocaleString("en-IN")}
            </strong>
          </div>
        </div>
      </div>
    </>
  );
}

export default Eligibility;