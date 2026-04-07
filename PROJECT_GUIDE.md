# Home Lynk Project Study Guide

## 1. Project Overview

Home Lynk is a Flask-based home services booking platform.

It supports 3 roles:

- `user`: browses services, adds items to cart, selects slot/address/payment, places orders, and tracks orders
- `provider`: registers as a service professional, submits verification details and documents, and manages assigned jobs
- `admin`: reviews professional profiles, approves or rejects them, assigns orders manually or automatically, and monitors commission/payout

Main idea:

1. Customer books a service
2. Booking is stored in MySQL
3. Admin reviews and assigns the job
4. Approved professional completes the work
5. App splits booking amount into admin commission and professional payout

## 2. Tech Stack

- Backend: Python Flask
- Database: MySQL
- ORM: Flask-SQLAlchemy
- Frontend templating: Jinja2
- Frontend behavior: Vanilla JavaScript
- Styling: CSS
- Maps/location: Google Maps Places + Geolocation
- Password security: Werkzeug password hashing

## 3. Folder Structure

- `app.py`: complete backend logic, models, helper methods, and routes
- `schema.sql`: database schema and seed users
- `templates/`: all HTML pages
- `static/css/`: styling for home, services, cart, and dashboards
- `static/js/script.js`: home page/navbar/modal interactions
- `static/js/script2.js`: service page cart logic
- `static/js/cart.js`: cart, slot, payment, and location logic
- `static/images/`: logos and service icons
- `static/videos/`: service background videos

## 4. Core Database Tables and Relationships

### `users`
Stores all accounts.

Important fields:

- `id`
- `name`
- `email`
- `password`
- `role`

### `contact`
Stores messages from the contact form.

### `saved_locations`
Stores address selected during checkout.

Relationship:

- many saved locations can belong to one user

### `bookings`
Stores service orders placed by customers.

Important relation fields:

- `user_id` -> customer from `users`
- `assigned_professional_id` -> provider from `users`

Other important fields:

- `service_summary`
- `service_category`
- `total_price`
- `slot`
- `address`
- `payment_method`
- `status`
- `work_status`
- `professional_amount`
- `admin_commission`
- `admin_notes`

### `professional_profiles`
Stores provider profile and verification details.

Relationship:

- one provider user has one professional profile

### `professional_documents`
Stores uploaded Aadhaar, PAN, and optional GST files in binary form.

Relationship:

- many documents belong to one professional profile

## 5. Complete Role-Based Flow

### A. Customer Flow

1. User opens home page
2. User selects a service category
3. User adds one or more services into cart
4. Cart is stored in `localStorage` on frontend
5. User opens cart page
6. User selects:
   - service day
   - service time slot
   - address
   - payment method
7. User logs in if not already logged in
8. Cart data is posted to `/place-order`
9. Backend validates:
   - cart is not empty
   - slot and address are selected
   - payment is valid
   - all items belong to one main service category
10. Booking is created in `bookings`
11. 20% admin commission and 80% provider payout are calculated
12. User is redirected to `My Orders`

### B. Provider Flow

1. Provider registers with role `provider`
2. Provider is redirected to `/professional`
3. Provider fills profile details:
   - phone
   - city
   - experience
   - service categories
   - Aadhaar/PAN/GST
   - bank details
4. Provider uploads required documents
5. Profile status becomes `pending`
6. Admin reviews the profile
7. If approved:
   - `verification_status = approved`
   - `is_active = True`
8. Only then can provider receive assigned matching jobs
9. Provider updates job progress:
   - assigned
   - in progress
   - completed

### C. Admin Flow

1. Admin logs in and opens `/admin`
2. Admin sees:
   - verification queue
   - all bookings
   - assignment controls
   - payout summary
3. Admin approves or rejects provider profiles
4. Admin assigns orders:
   - manual assignment to a specific professional
   - automatic assignment using matching logic
5. Admin can change work status and add remarks
6. Completed jobs contribute to admin revenue and provider payout summary

## 6. Route Summary

### Public pages

- `/`: home page
- `/about`
- `/privacy`
- `/terms`
- `/reviews`
- `/categories`
- `/contact`

### Service pages

- `/electrician`
- `/plumbing`
- `/ac`
- `/deepclean`
- `/carpentry`
- `/painting`
- `/homesecurity`
- `/gardening`
- `/interior`

Each service page shows cards for sub-services and allows adding to cart.

### Authentication

- `/register`
- `/login`
- `/logout`
- `/auth`

### User order flow

- `/cart`
- `/place-order`
- `/my-orders`

### Provider dashboard

- `/professional`
- `/professional/complete-profile`
- `/professional/order/<booking_id>/status`

### Admin dashboard

- `/admin`
- `/admin/professional/<profile_id>/review`
- `/admin/order/<booking_id>/update`

### Document viewer

- `/document/<document_id>`

Only admin or the owning provider can open the uploaded document.

## 7. Smart Logic in the Project

### Service category inference
If cart items do not directly contain a clean category, backend tries to infer the main category from:

- service page name
- keywords inside service names

This helps keep order classification consistent.

### One-category-per-order rule
If customer mixes different top-level service categories in one cart, order placement is blocked.

Reason:

- one booking should map to one type of professional
- assignment becomes easier and cleaner

### Auto assignment logic
Automatic assignment checks:

- professional is approved
- professional is active
- professional offers that service category
- professional has fewer than 2 active jobs

Then it picks the best candidate using:

- lowest active work count first
- least recently assigned first

This creates fairer load distribution.

### Commission split
Every booking uses:

- admin commission = 20%
- professional payout = 80%

This is calculated by `update_booking_amounts()`.

## 8. Frontend Behavior

### Home page

- navbar login/register modal
- dropdown for logged-in account
- cart badge from `localStorage`
- category navigation

### Service pages

- category filtering inside a service page
- add to cart
- quantity increase/decrease
- cart badge update

Cart is fully frontend-managed before checkout.

### Cart page

- shows selected items from `localStorage`
- day + period + slot selection
- address search with Google Places autocomplete
- current-location detection with browser geolocation
- payment selection
- hidden checkout form posts final data to Flask

## 9. Important Security and Design Notes

These are useful to mention honestly in expo as future improvements.

### Current strengths

- passwords are hashed
- role-based route protection exists
- document access is permission-checked
- provider approval is required before job handling

### Current limitations

- Flask `secret_key` is hardcoded
- database credentials are hardcoded
- Google Maps API key is hardcoded
- online payment is not completed yet
- backend is in one large file instead of modular structure
- no advanced validation for file size/type
- no CSRF protection layer
- document files are stored directly in database blobs

## 10. Seed Accounts from `schema.sql`

Three sample users are pre-inserted:

- admin: `admin@gmail.com`
- provider: `provider@gmail.com`
- user: `user@gmail.com`

Passwords are stored as hashes, so plain text is not visible in the SQL file.

## 11. Best Way to Explain the Project in Expo

Use this short explanation:

"This project is a full-stack home services booking platform called Home Lynk. Customers can browse service categories, add services to cart, choose time slot and address, and place bookings. Service professionals can register separately, complete verification with documents, and after admin approval they receive assigned jobs. Admin manages both provider verification and order assignment. The system also calculates 20 percent admin commission and 80 percent professional payout for each booking."

## 12. Best Demo Flow

If you need to present quickly, follow this order:

1. Show home page and categories
2. Open one service page and add services
3. Open cart and explain slot/address/payment selection
4. Explain booking creation and database storage
5. Show `My Orders`
6. Switch to admin dashboard and show:
   - professional verification
   - order assignment
   - commission summary
7. Switch to provider dashboard and show:
   - profile submission
   - assigned jobs
   - work status updates

## 13. Files You Should Revise First

If time is short, focus on these:

1. `app.py`
2. `schema.sql`
3. `templates/index.html`
4. `templates/cart.html`
5. `templates/admin.html`
6. `templates/professional.html`
7. `static/js/script2.js`
8. `static/js/cart.js`

## 14. Likely Viva Questions

### Why did you use Flask?
Because the project is small-to-medium size, Flask makes routing, templating, and database integration simple and fast to build.

### Why is there role-based access?
Because customer, provider, and admin have completely different permissions and dashboards.

### Why separate `status` and `work_status`?
`work_status` is the internal operational stage like pending/assigned/in_progress/completed, while `status` stores a user-friendly label shown in UI.

### Why restrict one booking to one main category?
Because each booking is assigned to one matching professional type, so mixed-category orders would complicate assignment and execution.

### How does auto assignment work?
The system filters only approved and active professionals who offer the requested service and have fewer than 2 active jobs, then chooses the least-loaded candidate.

### How do you store uploaded documents?
Documents are stored in the `professional_documents` table as binary data with filename and MIME type.

### What can be improved next?

- Razorpay integration
- better validation
- modular Flask blueprint structure
- OTP/email verification
- notifications
- provider availability scheduling
- better analytics and reporting

## 15. One-Line Architecture Summary

Home Lynk is a role-based Flask + MySQL service-booking platform where customers create bookings, admins control verification and assignment, and professionals execute approved jobs.
