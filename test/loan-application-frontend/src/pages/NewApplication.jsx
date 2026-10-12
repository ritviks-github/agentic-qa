import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../components/Icon";
import Stepper from "../components/Stepper";

function NewApplication() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);

  const [form, setForm] = useState({
    name: "",
    dob: "",
    phone: "",
    email: "",
    pan: "",
    employment: "",
    income: "",
    emi: "",
    loanType: "Personal Loan",
    amount: "",
    tenure: "36",
  });

  const update = (field, value) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const next = () => {
    if (step < 5) {
      setStep((value) => value + 1);
    } else {
      navigate("/applications/LN-2026-1004");
    }
  };

  const previous = () => {
    if (step > 1) {
      setStep((value) => value - 1);
    }
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>New Loan Application</h1>
          <p>
            Create and submit a new customer loan application.
          </p>
        </div>
      </div>

      <section className="card application-form">
        <Stepper currentStep={step} />

        {step === 1 && (
          <div className="form-section">
            <h3>Personal Information</h3>
            <p className="section-description">
              Enter the customer's basic personal details.
            </p>

            <div className="form-grid">
              <div className="field">
                <label>Full Name *</label>
                <input
                  value={form.name}
                  onChange={(e) =>
                    update("name", e.target.value)
                  }
                  placeholder="Enter full name"
                />
              </div>

              <div className="field">
                <label>Date of Birth *</label>
                <input
                  type="date"
                  value={form.dob}
                  onChange={(e) =>
                    update("dob", e.target.value)
                  }
                />
              </div>

              <div className="field">
                <label>Mobile Number *</label>
                <input
                  value={form.phone}
                  maxLength={10}
                  onChange={(e) =>
                    update("phone", e.target.value)
                  }
                  placeholder="10-digit mobile number"
                />
              </div>

              <div className="field">
                <label>Email *</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) =>
                    update("email", e.target.value)
                  }
                  placeholder="customer@example.com"
                />
              </div>

              <div className="field">
                <label>PAN *</label>
                <input
                  className="uppercase"
                  maxLength={10}
                  value={form.pan}
                  onChange={(e) =>
                    update("pan", e.target.value)
                  }
                  placeholder="ABCDE1234F"
                />
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="form-section">
            <h3>Financial Information</h3>
            <p className="section-description">
              Provide income and existing financial obligations.
            </p>

            <div className="form-grid">
              <div className="field">
                <label>Employment Type *</label>

                <select
                  value={form.employment}
                  onChange={(e) =>
                    update("employment", e.target.value)
                  }
                >
                  <option value="">
                    Select employment type
                  </option>
                  <option>Salaried</option>
                  <option>Self-employed</option>
                  <option>Business owner</option>
                </select>
              </div>

              <div className="field">
                <label>Monthly Income *</label>

                <div className="input-with-prefix">
                  <span>₹</span>
                  <input
                    type="number"
                    value={form.income}
                    onChange={(e) =>
                      update("income", e.target.value)
                    }
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="field">
                <label>Existing Monthly EMI</label>

                <div className="input-with-prefix">
                  <span>₹</span>
                  <input
                    type="number"
                    value={form.emi}
                    onChange={(e) =>
                      update("emi", e.target.value)
                    }
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="field">
                <label>Available Monthly Income</label>

                <div className="calculated-value">
                  ₹
                  {(
                    Number(form.income || 0) -
                    Number(form.emi || 0)
                  ).toLocaleString("en-IN")}
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="form-section">
            <h3>Loan Details</h3>
            <p className="section-description">
              Select the loan product and requested amount.
            </p>

            <div className="form-grid">
              <div className="field">
                <label>Loan Type *</label>

                <select
                  value={form.loanType}
                  onChange={(e) =>
                    update("loanType", e.target.value)
                  }
                >
                  <option>Personal Loan</option>
                  <option>Home Loan</option>
                  <option>Auto Loan</option>
                </select>
              </div>

              <div className="field">
                <label>Requested Amount *</label>

                <div className="input-with-prefix">
                  <span>₹</span>
                  <input
                    type="number"
                    value={form.amount}
                    onChange={(e) =>
                      update("amount", e.target.value)
                    }
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="field">
                <label>Tenure *</label>

                <select
                  value={form.tenure}
                  onChange={(e) =>
                    update("tenure", e.target.value)
                  }
                >
                  <option value="12">12 months</option>
                  <option value="24">24 months</option>
                  <option value="36">36 months</option>
                  <option value="48">48 months</option>
                  <option value="60">60 months</option>
                </select>
              </div>

              <div className="field">
                <label>Interest Rate</label>

                <div className="calculated-value">
                  10.5% per annum
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="form-section">
            <h3>Required Documents</h3>
            <p className="section-description">
              Upload the documents required to process this
              application.
            </p>

            <div className="upload-area">
              <Icon name="upload" size={30} />

              <h4>Upload documents</h4>

              <p>
                PDF, JPG or PNG files. Maximum file size 10 MB.
              </p>

              <input type="file" />
            </div>

            <div className="document-list">
              {[
                "PAN Card",
                "Income Proof",
                "Address Proof",
              ].map((document) => (
                <div
                  className="document-row"
                  key={document}
                >
                  <div>
                    <Icon name="file" size={16} />
                    <span>{document}</span>
                  </div>

                  <span className="required-tag">
                    Required
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="form-section">
            <h3>Review & Submit</h3>
            <p className="section-description">
              Review the application information before
              submission.
            </p>

            <div className="review-grid">
              <div>
                <span>Customer</span>
                <strong>
                  {form.name || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Email</span>
                <strong>
                  {form.email || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Employment</span>
                <strong>
                  {form.employment || "Not provided"}
                </strong>
              </div>

              <div>
                <span>Monthly Income</span>
                <strong>
                  ₹
                  {Number(form.income || 0).toLocaleString(
                    "en-IN"
                  )}
                </strong>
              </div>

              <div>
                <span>Loan Type</span>
                <strong>{form.loanType}</strong>
              </div>

              <div>
                <span>Requested Amount</span>
                <strong>
                  ₹
                  {Number(form.amount || 0).toLocaleString(
                    "en-IN"
                  )}
                </strong>
              </div>

              <div>
                <span>Tenure</span>
                <strong>{form.tenure} months</strong>
              </div>
            </div>

            <div className="notice">
              <Icon name="info" size={17} />

              <span>
                Please verify all information before submitting.
                Submitted applications cannot be edited.
              </span>
            </div>
          </div>
        )}

        <div className="form-footer">
          {step > 1 && (
            <button
              className="button secondary"
              onClick={previous}
            >
              <Icon name="arrowLeft" size={15} />
              Previous
            </button>
          )}

          <button
            className="button primary"
            onClick={next}
          >
            {step === 5
              ? "Submit Application"
              : "Continue"}

            <Icon name="arrowRight" size={15} />
          </button>
        </div>
      </section>
    </>
  );
}

export default NewApplication;