import { useState, useEffect, useRef, useCallback } from 'react';

export default function DraggablePanel({ id, children, className = '', defaultPosition = { x: 0, y: 0 } }) {
  const [position, setPosition] = useState(() => {
    try {
      const saved = localStorage.getItem(`draggable_${id}`);
      return saved ? JSON.parse(saved) : defaultPosition;
    } catch {
      return defaultPosition;
    }
  });

  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef({ startX: 0, startY: 0, initX: 0, initY: 0 });
  const [zIndex, setZIndex] = useState(() => {
    const highest = parseInt(localStorage.getItem('highest_z') || '100');
    return highest;
  });

  const bringToFront = useCallback(() => {
    const highest = parseInt(localStorage.getItem('highest_z') || '100') + 1;
    localStorage.setItem('highest_z', highest.toString());
    setZIndex(highest);
  }, []);

  const handlePointerDown = useCallback((e) => {
    bringToFront();
    
    // Only drag if clicking on the handle
    if (!e.target.closest('.drag-handle')) return;
    
    if (e.target.hasPointerCapture) {
        e.target.setPointerCapture(e.pointerId);
    }

    setIsDragging(true);
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      initX: position.x,
      initY: position.y
    };
  }, [position, bringToFront]);

  useEffect(() => {
    if (!isDragging) return;

    const handlePointerMove = (e) => {
      e.preventDefault(); // Prevent scrolling while dragging
      const dx = e.clientX - dragRef.current.startX;
      const dy = e.clientY - dragRef.current.startY;
      setPosition({
        x: dragRef.current.initX + dx,
        y: dragRef.current.initY + dy
      });
    };

    const handlePointerUp = () => {
      setIsDragging(false);
    };

    window.addEventListener('pointermove', handlePointerMove, { passive: false });
    window.addEventListener('pointerup', handlePointerUp);
    window.addEventListener('pointercancel', handlePointerUp);

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      window.removeEventListener('pointercancel', handlePointerUp);
    };
  }, [isDragging]);

  useEffect(() => {
    localStorage.setItem(`draggable_${id}`, JSON.stringify(position));
  }, [position, id]);

  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const style = isMobile 
    ? {} 
    : { transform: `translate(${position.x}px, ${position.y}px)`, zIndex };

  return (
    <div 
      className={`draggable-panel-wrapper ${className} ${isDragging ? 'dragging' : ''}`} 
      style={style}
      onPointerDown={handlePointerDown}
    >
      <div className="drag-handle" title="Drag to move">
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none">
          <circle cx="9" cy="5" r="1"></circle>
          <circle cx="9" cy="12" r="1"></circle>
          <circle cx="9" cy="19" r="1"></circle>
          <circle cx="15" cy="5" r="1"></circle>
          <circle cx="15" cy="12" r="1"></circle>
          <circle cx="15" cy="19" r="1"></circle>
        </svg>
      </div>
      <div className="draggable-content">
        {children}
      </div>
    </div>
  );
}
