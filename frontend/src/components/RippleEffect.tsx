import { useEffect, useRef } from 'react';

interface RippleEffectProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const RippleEffect: React.FC<RippleEffectProps> = ({
  children,
  className = '',
  onClick
}) => {
  const rippleRef = useRef<HTMLDivElement>(null);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!rippleRef.current) return;

    // Create ripple element
    const ripple = document.createElement('span');
    const diameter = Math.max(rippleRef.current.clientWidth, rippleRef.current.clientHeight);
    const radius = diameter / 2;

    ripple.style.width = ripple.style.height = `${diameter}px`;
    ripple.style.left = `${e.clientX - rippleRef.current.getBoundingClientRect().left - radius}px`;
    ripple.style.top = `${e.clientY - rippleRef.current.getBoundingClientRect().top - radius}px`;
    ripple.className = 'ripple';
    ripple.style.background = 'rgba(255, 255, 255, 0.3)';

    rippleRef.current.appendChild(ripple);

    // Remove ripple after animation completes
    setTimeout(() => {
      ripple.remove();
    }, 600);

    // Call original onClick handler
    if (onClick) {
      onClick();
    }
  };

  useEffect(() => {
    return () => {
      // Cleanup any remaining ripples
      rippleRef.current?.querySelectorAll('.ripple').forEach(ripple => ripple.remove());
    };
  }, []);

  return (
    <div
      ref={rippleRef}
      className={`ripple-container ${className}`}
      onClick={handleClick}
      style={{
        position: 'relative',
        overflow: 'hidden',
        cursor: 'pointer'
      }}
    >
      {children}
    </div>
  );
};

export default RippleEffect;