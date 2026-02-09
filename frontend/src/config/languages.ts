import { Language } from "../types/api";

export interface LanguageConfig {
  value: Language;
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
}

export const LANGUAGE_CONFIG: Record<Language, LanguageConfig> = {
  python: {
    value: "python",
    label: "Python",
    color: "text-blue-700 dark:text-blue-300",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
    borderColor: "border-blue-300 dark:border-blue-700",
    icon: "🐍",
  },
  c: {
    value: "c",
    label: "C",
    color: "text-purple-700 dark:text-purple-300",
    bgColor: "bg-purple-100 dark:bg-purple-900/30",
    borderColor: "border-purple-300 dark:border-purple-700",
    icon: "⚡",
  },
  assembly: {
    value: "assembly",
    label: "Assembly",
    color: "text-red-700 dark:text-red-300",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    borderColor: "border-red-300 dark:border-red-700",
    icon: "🔧",
  },
  cobol: {
    value: "cobol",
    label: "COBOL",
    color: "text-green-700 dark:text-green-300",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    borderColor: "border-green-300 dark:border-green-700",
    icon: "📊",
  },
};

export const ALL_LANGUAGES = Object.values(LANGUAGE_CONFIG);
