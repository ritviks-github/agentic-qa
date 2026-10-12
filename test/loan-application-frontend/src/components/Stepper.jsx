import Icon from "./Icon";

function Stepper({ currentStep }) {
  const steps = [
    "Personal",
    "Financial",
    "Loan Details",
    "Documents",
    "Review",
  ];

  return (
    <div className="stepper">
      {steps.map((step, index) => {
        const number = index + 1;
        const completed = number < currentStep;
        const current = number === currentStep;

        return (
          <div className="step-wrapper" key={step}>
            <div
              className={`step ${
                completed || current ? "active" : ""
              }`}
            >
              <div className="step-number">
                {completed ? (
                  <Icon name="check" size={14} />
                ) : (
                  number
                )}
              </div>

              <span>{step}</span>
            </div>

            {number < steps.length && (
              <div
                className={`step-connector ${
                  completed ? "active" : ""
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default Stepper;