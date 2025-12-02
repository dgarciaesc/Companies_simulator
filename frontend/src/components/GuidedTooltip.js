import React, { useEffect, useState } from 'react';
import './GuidedTooltip.css';

const GuidedTooltip = ({ targetRef, step, onNext, onSkip }) => {
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (targetRef?.current) {
      const rect = targetRef.current.getBoundingClientRect();
      setPosition({
        top: rect.bottom + window.scrollY + 20,
        left: rect.left + window.scrollX
      });
    }
  }, [targetRef]);

  if (!step) return null;

  return (
    <>
      <div className="guided-tooltip-overlay" onClick={onSkip}></div>
      <div 
        className="guided-tooltip-spotlight"
        style={{
          top: targetRef?.current ? targetRef.current.getBoundingClientRect().top - 10 : 0,
          left: targetRef?.current ? targetRef.current.getBoundingClientRect().left - 10 : 0,
          width: targetRef?.current ? targetRef.current.offsetWidth + 20 : 0,
          height: targetRef?.current ? targetRef.current.offsetHeight + 20 : 0
        }}
      ></div>
      <div 
        className="guided-tooltip"
        style={{
          top: `${position.top}px`,
          left: `${position.left}px`
        }}
      >
        <div className="guided-tooltip-header">
          <div className="consultant-mini">
            <img src="/images/john-toe.png" alt="Consultant" />
          </div>
          <div className="step-indicator">
            Step {step.currentStep} of {step.totalSteps}
          </div>
        </div>
        <div className="guided-tooltip-content">
          <h3>{step.title}</h3>
          <p>{step.description}</p>
          {step.details && (
            <ul className="tooltip-details">
              {step.details.map((detail, index) => (
                <li key={index}>{detail}</li>
              ))}
            </ul>
          )}
        </div>
        <div className="guided-tooltip-actions">
          <button className="skip-button" onClick={onSkip}>
            Skip Tutorial
          </button>
          <button className="next-button" onClick={onNext}>
            {step.currentStep === step.totalSteps ? 'Got it!' : 'Next →'}
          </button>
        </div>
      </div>
    </>
  );
};

export default GuidedTooltip;
