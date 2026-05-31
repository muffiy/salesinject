import { useEffect, useRef } from 'react';

interface PulseAnimationProps {
  children: React.ReactNode;
  className?: string;
  pulseScale?: number; // scale factor
  pulseDuration?: string; // animation duration
  delay?: string; // delay before pulse starts
}

const PulseAnimation: React.FC<PulseAnimationProps> = ({
  children,
  className = '',
  pulseScale = 1.05,
  pulseDuration = '2s',
  delay = '0s'
}) => {
  useEffect(() => {
    const elements = document.querySelectorAll(`.${className.split(' ')[0]}`);
    elements.forEach(element => {
      if (element) {
        element.style.animation = `pulse ${pulseDuration} ease-in-out infinite ${delay}`;
        element.style.display = 'inline-block';
      }
    });

    return () => {
      elements.forEach(element => {
        if (element) {
          element.style.animation = 'none';
        }
      });
    };
  }, [className, pulseDuration, delay]);

  return (
    <div
      className={className}
      style={{
        position: 'relative'
      }}
    >
      {children}
    </div>
  );
};

export default PulseAnimation;