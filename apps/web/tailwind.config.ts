import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "var(--border)",
        panel: "var(--panel)",
        "panel-border": "var(--panel-border)",
        primary: "var(--primary)",
        "primary-muted": "var(--primary-muted)",
        canon: "var(--canon)",
        generated: "var(--generated)",
        fandom: "var(--fandom)",
        danger: "var(--danger)",
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
        serif: ['var(--font-newsreader)', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'ripple': 'ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        ripple: {
          '0%': { top: '36px', left: '36px', width: '0', height: '0', opacity: '0' },
          '4.9%': { top: '36px', left: '36px', width: '0', height: '0', opacity: '0' },
          '5%': { top: '36px', left: '36px', width: '0', height: '0', opacity: '1' },
          '100%': { top: '0px', left: '0px', width: '72px', height: '72px', opacity: '0' },
        }
      }
    },
  },
  plugins: [],
};
export default config;
