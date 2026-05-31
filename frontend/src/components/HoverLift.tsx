import { useState } from 'react';

interface HoverLiftProps {
  children: React.ReactNode;
  className?: string;
  liftAmount?: number; // pixels
  transitionDuration?: string;
}

const HoverLift: React.FC<HoverLiftProps> = ({
  children,
  className = '',
  liftAmount = 2,
  transitionDuration = '200ms'
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        transition: `transform ${transitionDuration} ease-in-out`,
        transform: isHovered ? `translateY(-${liftAmount}px)` : 'translateY(0)'
      }}
    >
      {children}
    </div>
  );
};

export default HoverLift;