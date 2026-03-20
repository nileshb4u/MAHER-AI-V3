/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./components/**/*.{js,ts,jsx,tsx}",
        "./*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'brand-deep-blue': '#0D1B2A',
                'brand-blue': '#1B263B',
                'brand-light-blue': '#415A77',
                'brand-gray': '#778DA9',
                'brand-light-gray': '#E0E1DD',
                'brand-accent-orange': '#F77F00',
                'brand-accent-green': '#2ECC71',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
