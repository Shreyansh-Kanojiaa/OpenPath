/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        background: '#1a1b26',      // Main app background
        surface: '#24283b',         // Cards, modals, sidebar
        surfaceHover: '#2f354b',    // Card hover state
        
        // Accents
        primary: '#7aa2f7',         // Primary buttons, active states, links
        primaryHover: '#5d8eea',    // Primary hover
        secondary: '#73daca',       // Success, progress, flashcards
        accent: '#bb9af7',          // AI features, badges, premium content
        
        // Semantic
        warning: '#e0af68',         // Quiz alerts, notifications
        error: '#f7768e',           // Errors, destructive actions
        success: '#73daca',         // Success states
        
        // Text
        text: '#c0caf5',            // Headings, body text
        textMuted: '#565f89',       // Subtitles, metadata, captions
        textLight: '#787c99',       // Disabled, placeholders
        
        // Borders
        border: '#414868',          // Subtle separators, input borders
        borderLight: '#565f89',     // Input focus borders
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem', letterSpacing: '0px' }],      // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem', letterSpacing: '0px' }],  // 14px
        'base': ['1rem', { lineHeight: '1.5rem', letterSpacing: '0px' }],     // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem', letterSpacing: '0px' }],  // 18px
        'xl': ['1.25rem', { lineHeight: '1.75rem', letterSpacing: '0px' }],   // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem', letterSpacing: '-0.01em' }],  // 24px
        '3xl': ['2rem', { lineHeight: '2.5rem', letterSpacing: '-0.01em' }],  // 32px
        '4xl': ['3rem', { lineHeight: '3.5rem', letterSpacing: '-0.02em' }],  // 48px
      },
      fontWeight: {
        regular: 400,
        medium: 500,
        semibold: 600,
      }
    },
  },
  plugins: [],
}
