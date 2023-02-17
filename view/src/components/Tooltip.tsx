import React, { useState } from "react";

interface TooltipProps {
    content: React.ReactNode;
    direction?: "top" | "right" | "bottom" | "left";
    animated?: boolean;
    children: React.ReactNode;
    className?: string;
    tooltipClassName?: string;
}

const Tooltip: React.FC<TooltipProps> = ({
    content,
    direction = "top",
    animated = false,
    children,
    className,
    tooltipClassName,
}) => {
    const [isVisible, setIsVisible] = useState(false);

    const handleMouseEnter = () => {
        setIsVisible(true);
    };

    const handleMouseLeave = () => {
        setIsVisible(false);
    };

    const getTooltipClasses = () => {
        let baseClasses =
            "absolute text-slate-900 dark:text-slate-200 p-2 dark:bg-slate-800 z-10";
        const animationClasses = animated
            ? "opacity-0 scale-90 transform transition-opacity"
            : "";
        const visibleClasses = isVisible
            ? "opacity-100 scale-100"
            : "opacity-0";
        baseClasses = `${baseClasses} ${visibleClasses}`;
        switch (direction) {
            case "top":
                return `${baseClasses} bottom-[calc(100%+0.5em)] left-1/2 -translate-x-1/2 ${animationClasses}`;
            case "left":
                return `${baseClasses} top-1/2 right-[calc(100%+0.5em)] -translate-y-1/2 ${animationClasses}`;
            case "bottom":
                return `${baseClasses} top-[calc(100%+0.5em)] left-1/2 -translate-x-1/2 ${animationClasses}`;
            case "right":
                return `${baseClasses} top-1/2 left-[calc(100%+0.5em)] -translate-y-1/2 ${animationClasses}`;
            default:
                return "";
        }
    };

    return (
        <div
            className={`relative ${className}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {children}
            <div className={`${getTooltipClasses()} ${tooltipClassName}`}>
                {content}
            </div>
        </div>
    );
};

export default Tooltip;
