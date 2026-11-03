import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check, Send } from 'lucide-react';
import './FeedbackWidget.css';

const ERROR_CATEGORIES = [
  { value: 'MISSING_SEMICOLON', label: 'Missing Semicolon (;)' },
  { value: 'UNDECLARED_IDENTIFIER', label: 'Undeclared Identifier' },
  { value: 'TYPE_MISMATCH', label: 'Type Mismatch' },
  { value: 'UNMATCHED_BRACES', label: 'Unmatched Braces ({})' },
  { value: 'UNMATCHED_PARENTHESES', label: 'Unmatched Parentheses (())' },
  { value: 'MISSING_RETURN', label: 'Missing Return Statement' },
  { value: 'INVALID_DECLARATION', label: 'Invalid Declaration' },
  { value: 'MISSING_HEADER', label: 'Missing Header (#include)' },
  { value: 'MISSING_NAMESPACE', label: 'Missing Namespace (std::)' },
  { value: 'UNDEFINED_REFERENCE', label: 'Undefined Reference (Linker)' },
  { value: 'WRONG_ARGUMENTS', label: 'Wrong Arguments / Parameter Mismatch' },
  { value: 'CONST_VIOLATION', label: 'Const Violation' },
];

export const FeedbackWidget = ({ errorId, initialCategory }) => {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [showCorrection, setShowCorrection] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory || '');
  const [submitting, setSubmitting] = useState(false);

  const handleRating = async (helpful) => {
    if (!helpful) {
      setShowCorrection(true);
      return;
    }

    setSubmitting(true);
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          error_id: errorId,
          helpful: true,
          corrected_category: null
        })
      });
      setFeedbackSent(true);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCorrectionSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!selectedCategory) return;

    setSubmitting(true);
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          error_id: errorId,
          helpful: false,
          corrected_category: selectedCategory
        })
      });
      setFeedbackSent(true);
      setShowCorrection(false);
    } catch (err) {
      console.error('Failed to submit correction:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (feedbackSent) {
    return (
      <div className="feedback-submitted-badge" onClick={(e) => e.stopPropagation()}>
        <Check size={13} />
        <span>Thank you for your feedback!</span>
      </div>
    );
  }

  return (
    <div className="feedback-widget" onClick={(e) => e.stopPropagation()}>
      {!showCorrection ? (
        <div className="feedback-prompt-row">
          <span className="feedback-label">Was this explanation helpful?</span>
          <div className="feedback-buttons">
            <button
              className="feedback-btn btn-helpful"
              onClick={() => handleRating(true)}
              disabled={submitting}
              title="Helpful"
            >
              <ThumbsUp size={12} />
              <span>Yes</span>
            </button>
            <button
              className="feedback-btn btn-not-helpful"
              onClick={() => handleRating(false)}
              disabled={submitting}
              title="Not helpful / Suggest correction"
            >
              <ThumbsDown size={12} />
              <span>No</span>
            </button>
          </div>
        </div>
      ) : (
        <form className="correction-form" onSubmit={handleCorrectionSubmit}>
          <span className="correction-title">What should this error be categorized as?</span>
          <div className="correction-controls">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-dropdown"
              disabled={submitting}
              required
            >
              <option value="">-- Select True Category --</option>
              {ERROR_CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="btn-submit-correction"
              disabled={submitting || !selectedCategory}
            >
              <Send size={12} />
              <span>Submit</span>
            </button>
            <button
              type="button"
              className="btn-cancel-correction"
              onClick={() => setShowCorrection(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

