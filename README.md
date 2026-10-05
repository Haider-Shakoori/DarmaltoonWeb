# Darmaltoon — Public Marketing Website

The public marketing website for **Darmaltoon**, modern pharmacy-management software designed primarily for pharmacies in Afghanistan.

This repository contains the public-facing static website only. It does not contain the Darmaltoon SaaS platform, admin panel, pharmacy backend, authentication, licensing backend, or database.

## Pages

- Home
- Features
- PharmaDesktop
- Demo Request
- About
- Contact
- 404

## Frontend

- HTML5
- Custom CSS
- Vanilla JavaScript
- English, Dari and Pashto localization
- LTR/RTL support
- Responsive layouts
- Frontend-only demo/contact form validation

## Project Structure

darmaltoon/
- index.html
- features.html
- pharmadesktop.html
- demo.html
- contact.html
- about.html
- 404.html
- assets/css/main.css
- assets/css/responsive.css
- assets/css/rtl.css
- assets/js/translations.js
- assets/js/language.js
- assets/js/app.js
- assets/js/forms.js
- assets/images/brand/
- assets/images/screenshots/

## Local Review

Open index.html directly in a browser or serve the repository with any simple static web server.

## Forms

The demo and contact forms currently validate in the browser only. Backend submission endpoints will be connected later.

## Localization

Translations are stored in assets/js/translations.js. The active language is persisted in localStorage. Dari and Pashto switch the document to RTL.

## Screenshot Assets

The website expects PharmaDesktop screenshots under assets/images/screenshots/. The real application screenshots can be added without changing the page structure.

## Next Phase

After the static design is finalized, the contact and demo forms can be connected to the production Darmaltoon backend while preserving this frontend design.
