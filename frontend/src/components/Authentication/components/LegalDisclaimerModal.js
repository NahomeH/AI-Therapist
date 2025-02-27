// components/Authentication/components/LegalDisclaimerModal.js
import React, { useState, useRef, useEffect } from 'react';
import { X } from 'lucide-react';

const LegalDisclaimerModal = ({ isOpen, onClose, onAccept }) => {
  const [hasScrolledToBottom, setHasScrolledToBottom] = useState(false);
  const contentRef = useRef(null);
  const modalRef = useRef(null);
  
  // Reset scroll state when modal opens
  useEffect(() => {
    if (isOpen) {
      setHasScrolledToBottom(false);
      
      // Focus trap and click outside to close
      const handleClickOutside = (e) => {
        if (modalRef.current && !modalRef.current.contains(e.target)) {
          onClose();
        }
      };
      
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  const handleScroll = () => {
    if (!contentRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
    // Check if scrolled near bottom (with a 30px buffer)
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 30;
    
    if (isAtBottom && !hasScrolledToBottom) {
      setHasScrolledToBottom(true);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="legal-modal-overlay">
      <div className="legal-modal" ref={modalRef}>
        <div className="legal-modal-header">
          <h3>Terms and Conditions</h3>
          <button 
            type="button"
            className="close-modal-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>
        
        <div 
          className="legal-modal-content"
          ref={contentRef}
          onScroll={handleScroll}
        >
          <div className="legal-text">
            <p>This AI therapy application ("Talk2Me") is provided as an educational and self-help tool only. By using this service, you acknowledge and agree to the following terms:</p>
            
            <p>1. <strong>Not a Substitute for Professional Help:</strong> Talk2Me is not a replacement for professional medical advice, diagnosis, or treatment. If you're experiencing a medical or mental health emergency, please call your local emergency services or crisis hotline immediately.</p>
            
            <p>2. <strong>No Licensed Therapists:</strong> Interactions with this AI do not establish a therapist-client relationship. The AI does not have the ability to make professional judgments about your specific situation.</p>
            
            <p>3. <strong>Privacy & Data:</strong> While we implement reasonable security measures, no system is entirely secure. Your conversations may be used for service improvement, research, and AI training with all identifiable information removed.</p>
            
            <p>4. <strong>Limitations:</strong> The AI may provide inaccurate, incomplete, or inappropriate responses. You are responsible for evaluating the appropriateness of any guidance provided.</p>
            
            <p>5. <strong>Age Restriction:</strong> This service is intended for users 18 years or older. If you are under 18, please use this service only with parental consent and supervision.</p>
            
            <p>6. <strong>Crisis Response:</strong> Talk2Me is not equipped to address crisis situations. If you experience thoughts of self-harm or harm to others, please contact crisis services immediately.</p>
            
            <p>7. <strong>Changes to Terms:</strong> We may update these terms at any time. Continued use of the service constitutes acceptance of any changes.</p>
            
            <p>8. <strong>Warranty Disclaimer:</strong> Talk2Me is provided "as is" without warranties of any kind, either express or implied.</p>
            
            <p>9. <strong>Limitation of Liability:</strong> We shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of or inability to use the service.</p>
            
            <p>10. <strong>Governing Law:</strong> These terms shall be governed by and construed in accordance with the laws of [Your Jurisdiction], without regard to its conflict of law principles.</p>
          </div>
        </div>
        
        <div className="legal-modal-footer">
          {!hasScrolledToBottom && (
            <div className="scroll-indicator">
              Please scroll to read all terms
            </div>
          )}
          <div className="modal-actions">
            <button 
              type="button"
              className="modal-cancel-btn"
              onClick={onClose}
            >
              Cancel
            </button>
            <button 
              type="button"
              className="modal-accept-btn"
              onClick={onAccept}
              disabled={!hasScrolledToBottom}
            >
              I Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalDisclaimerModal;