import React from "react";
import { Language } from "../types/api";
import { LANGUAGE_CONFIG } from "../config/languages";

interface LanguageBadgeProps {
  language: Language;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
}

export const LanguageBadge: React.FC<LanguageBadgeProps> = ({
  language,
  size = "md",
  showIcon = true,
}) => {
  const config = LANGUAGE_CONFIG[language];

  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-1",
    lg: "text-base px-3 py-1.5",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1 rounded-lg font-semibold
        border ${config.bgColor} ${config.color} ${config.borderColor}
        ${sizeClasses[size]}
      `}
    >
      {showIcon && <span>{config.icon}</span>}
      <span>{config.label}</span>
    </span>
  );
};
